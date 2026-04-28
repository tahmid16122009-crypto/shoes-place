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

# HOME
@app.route("/")
def home():
    products = supabase.table("products").select("*").execute().data or []
    orders = session.get("orders", [])
    cart = session.get("cart", [])
    return render_template("index.html", products=products, cart=cart, orders=orders)

# ADD CART
@app.route("/add/<int:pid>")
def add(pid):
    cart = session.get("cart", [])
    cart.append(pid)
    session["cart"] = cart
    return redirect("/")

# PLACE ORDER
@app.route("/order", methods=["POST"])
def order():
    name = request.form.get("name")
    phone = request.form.get("phone")

    cart = session.get("cart", [])
    user_orders = session.get("orders", [])

    for pid in cart:
        product = supabase.table("products").select("*").eq("id", pid).execute().data[0]

        order_data = {
            "product_name": product["name"],
            "customer_name": name,
            "phone": phone,
            "status": "Order placed"
        }

        supabase.table("orders").insert(order_data).execute()
        user_orders.append(order_data)

    session["orders"] = user_orders
    session["cart"] = []
    return redirect("/")

# ADMIN LOGIN + PANEL
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        if request.form.get("password") != ADMIN_PASSWORD:
            return "Wrong password"

    products = supabase.table("products").select("*").execute().data or []
    orders = supabase.table("orders").select("*").execute().data or []
    return render_template("admin.html", products=products, orders=orders)

# ADD PRODUCT
@app.route("/add_product", methods=["POST"])
def add_product():
    name = request.form["name"]
    price = request.form["price"]
    file = request.files["image"]

    filename = str(uuid.uuid4()) + file.filename
    supabase.storage.from_("products").upload(filename, file.read())

    image_url = supabase.storage.from_("products").get_public_url(filename)

    supabase.table("products").insert({
        "name": name,
        "price": price,
        "image": image_url
    }).execute()

    return redirect("/admin")

# UPDATE ORDER STATUS
@app.route("/update_order/<id>/<status>")
def update_order(id, status):
    supabase.table("orders").update({"status": status}).eq("id", id).execute()
    return redirect("/admin")

if __name__ == "__main__":
    app.run()