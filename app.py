import os
from flask import Flask, render_template, request, redirect, session
from supabase import create_client

app = Flask(__name__)
app.secret_key = "secret123"

SUPABASE_URL = "https://hjwgjopshptmhlkcdagh.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

ADMIN_PASSWORD = "Tahmid1122"

# ================= HOME =================
@app.route("/")
@app.route("/home")
def home():
    try:
        user = session.get("user")
        products = supabase.table("products").select("*").execute().data or []

        cart = session.get("cart", [])
        cart_items = []

        for pid in cart:
            r = supabase.table("products").select("*").eq("id", pid).execute()
            if r.data:
                cart_items.append(r.data[0])

        return render_template("home.html",
                               products=products,
                               cart_items=cart_items,
                               user=user)

    except Exception as e:
        return f"HOME ERROR: {e}"

# ================= LOGIN =================
@app.route("/login", methods=["POST"])
def login():
    session["user"] = {
        "name": request.form.get("name"),
        "phone": request.form.get("phone")
    }
    return redirect("/home")

# ================= CART =================
@app.route("/add/<int:pid>")
def add(pid):
    cart = session.get("cart", [])
    if pid not in cart:
        cart.append(pid)
    session["cart"] = cart
    return redirect("/home")

@app.route("/cart")
def cart():
    try:
        cart = session.get("cart", [])
        items = []

        for pid in cart:
            r = supabase.table("products").select("*").eq("id", pid).execute()
            if r.data:
                items.append(r.data[0])

        return render_template("cart.html", items=items)

    except Exception as e:
        return f"CART ERROR: {e}"

# ================= ORDER =================
@app.route("/order", methods=["POST"])
def order():
    try:
        user = session.get("user")
        cart = session.get("cart", [])

        for pid in cart:
            product = supabase.table("products").select("*").eq("id", pid).execute().data
            if product:
                p = product[0]

                supabase.table("orders").insert({
                    "product_name": p["name"],
                    "customer_name": user["name"] if user else "Guest",
                    "phone": user["phone"] if user else "000",
                    "address": request.form.get("address"),
                    "quantity": 1,
                    "status": "Order placed"
                }).execute()

        session["cart"] = []
        return redirect("/orders")

    except Exception as e:
        return f"ORDER ERROR: {e}"

# ================= ORDERS =================
@app.route("/orders")
def orders():
    try:
        user = session.get("user")
        all_orders = supabase.table("orders").select("*").execute().data or []

        if user:
            my_orders = [o for o in all_orders if o["phone"] == user["phone"]]
        else:
            my_orders = []

        return render_template("orders.html", orders=my_orders)

    except Exception as e:
        return f"ORDERS ERROR: {e}"

# ================= ME =================
@app.route("/me")
def me():
    return render_template("me.html", user=session.get("user"))

# ================= ADMIN =================
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/admin/dashboard")
        return "Wrong password"

    return render_template("admin_login.html")

@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get("admin"):
        return redirect("/admin")

    products = supabase.table("products").select("*").execute().data or []
    orders = supabase.table("orders").select("*").execute().data or []

    return render_template("admin.html",
                           products=products,
                           orders=orders)

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)