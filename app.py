import os
import uuid
from flask import Flask, render_template, request, redirect, session
from supabase import create_client

app = Flask(__name__)
app.secret_key = "secret123"

SUPABASE_URL = "https://hjwgjopshptmhlkcdagh.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

ADMIN_PASSWORD = "Tahmid1122"

# ---------------- LOGIN ----------------
@app.route("/login", methods=["POST"])
def login():
    session["user"] = {
        "name": request.form.get("name"),
        "phone": request.form.get("phone")
    }
    return redirect("/home")

# ---------------- HOME ----------------
@app.route("/")
def root():
    return redirect("/home")

@app.route("/home")
def home():
    user = session.get("user")
    products = supabase.table("products").select("*").execute().data or []
    return render_template("home.html", products=products, user=user)

# ---------------- CART ----------------
@app.route("/add/<int:pid>")
def add(pid):
    cart = session.get("cart", [])
    if pid not in cart:
        cart.append(pid)
    session["cart"] = cart
    return redirect("/home")

@app.route("/cart")
def cart():
    cart = session.get("cart", [])
    items = []

    for pid in cart:
        r = supabase.table("products").select("*").eq("id", pid).execute()
        if r.data:
            items.append(r.data[0])

    return render_template("cart.html", items=items)

# ---------------- ORDER ----------------
@app.route("/order", methods=["POST"])
def order():
    user = session.get("user")
    cart = session.get("cart", [])

    for pid in cart:
        product = supabase.table("products").select("*").eq("id", pid).execute().data
        if product:
            product = product[0]

            supabase.table("orders").insert({
                "product_name": product["name"],
                "customer_name": user["name"] if user else "Guest",
                "phone": user["phone"] if user else "000",
                "address": request.form.get("address"),
                "quantity": 1,
                "status": "Order placed"
            }).execute()

    session["cart"] = []
    return redirect("/orders")

# ---------------- ORDERS ----------------
@app.route("/orders")
def orders():
    user = session.get("user")
    all_orders = supabase.table("orders").select("*").execute().data or []

    if user:
        user_orders = [o for o in all_orders if o["phone"] == user["phone"]]
    else:
        user_orders = []

    return render_template("orders.html", orders=user_orders)

# ---------------- ME ----------------
@app.route("/me")
def me():
    user = session.get("user")
    return render_template("me.html", user=user)

# ---------------- ADMIN ----------------
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

# ---------------- ADD PRODUCT ----------------
@app.route("/add_product", methods=["POST"])
def add_product():
    if not session.get("admin"):
        return redirect("/admin")

    name = request.form.get("name")
    price = request.form.get("price")
    description = request.form.get("description")
    file = request.files.get("image")

    filename = str(uuid.uuid4()) + file.filename

    supabase.storage.from_("products").upload(filename, file.read())
    image_url = supabase.storage.from_("products").get_public_url(filename)

    supabase.table("products").insert({
        "name": name,
        "price": price,
        "description": description,
        "image": image_url
    }).execute()

    return redirect("/admin/dashboard")

# ---------------- UPDATE ORDER ----------------
@app.route("/update_order/<int:oid>/<status>")
def update_order(oid, status):
    if not session.get("admin"):
        return redirect("/admin")

    supabase.table("orders").update({
        "status": status
    }).eq("id", oid).execute()

    return redirect("/admin/dashboard")

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)