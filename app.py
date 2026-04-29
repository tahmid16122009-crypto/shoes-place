import os
from flask import Flask, render_template, request, redirect, session
from supabase import create_client

app = Flask(__name__)
app.secret_key = "secret123"

SUPABASE_URL = "https://hjwgjopshptmhlkcdagh.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------- LOGIN ----------
@app.route("/")
def index():
    if not session.get("user"):
        return render_template("login.html")
    return redirect("/home")

@app.route("/login", methods=["POST"])
def login():
    session["user"] = {
        "name": request.form.get("name"),
        "phone": request.form.get("phone")
    }
    return redirect("/home")

@app.route("/skip")
def skip():
    session["user"] = None
    return redirect("/home")

# ---------- HOME ----------
@app.route("/home")
def home():
    q = request.args.get("q", "")
    products = supabase.table("products").select("*").execute().data or []

    if q:
        products = [p for p in products if q.lower() in p["name"].lower()]

    return render_template("home.html", products=products, q=q)

# ---------- PRODUCT ----------
@app.route("/product/<int:pid>")
def product(pid):
    data = supabase.table("products").select("*").eq("id", pid).execute().data
    if not data:
        return "Product not found"
    return render_template("product.html", p=data[0])

# ---------- CART ----------
@app.route("/add/<int:pid>")
def add(pid):
    cart = session.get("cart", {})
    cart[str(pid)] = cart.get(str(pid), 0) + 1
    session["cart"] = cart
    return redirect("/cart")

@app.route("/cart")
def cart():
    cart = session.get("cart", {})
    items = []
    total = 0

    for pid, qty in cart.items():
        r = supabase.table("products").select("*").eq("id", int(pid)).execute()
        if r.data:
            p = r.data[0]
            p["qty"] = qty
            p["subtotal"] = qty * int(p["price"])
            total += p["subtotal"]
            items.append(p)

    return render_template("cart.html", items=items, total=total)

@app.route("/inc/<int:pid>")
def inc(pid):
    cart = session.get("cart", {})
    cart[str(pid)] += 1
    session["cart"] = cart
    return redirect("/cart")

@app.route("/dec/<int:pid>")
def dec(pid):
    cart = session.get("cart", {})
    if cart[str(pid)] > 1:
        cart[str(pid)] -= 1
    else:
        cart.pop(str(pid))
    session["cart"] = cart
    return redirect("/cart")

# ---------- ORDER ----------
@app.route("/order", methods=["POST"])
def order():
    user = session.get("user")
    cart = session.get("cart", {})

    for pid, qty in cart.items():
        product = supabase.table("products").select("*").eq("id", int(pid)).execute().data
        if product:
            p = product[0]
            supabase.table("orders").insert({
                "product_name": p["name"],
                "customer_name": user["name"] if user else "Guest",
                "phone": user["phone"] if user else "000",
                "address": request.form.get("address"),
                "quantity": qty,
                "status": "Order placed"
            }).execute()

    session["cart"] = {}
    return redirect("/orders")

# ---------- ORDERS ----------
@app.route("/orders")
def orders():
    user = session.get("user")
    data = supabase.table("orders").select("*").execute().data or []

    if user:
        my = [o for o in data if o["phone"] == user["phone"]]
    else:
        my = []

    return render_template("orders.html", orders=my)

# ---------- ME ----------
@app.route("/me")
def me():
    return render_template("me.html", user=session.get("user"))