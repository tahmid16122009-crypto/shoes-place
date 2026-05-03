from flask import Flask, render_template, request, redirect, session
from supabase import create_client
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret123"

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ================= LOGIN =================
@app.route("/")
def index():
    if "user" not in session:
        return render_template("login.html")
    return redirect("/home")

@app.route("/login", methods=["POST"])
def login():
    session["user"] = request.form.get("name")
    session["phone"] = request.form.get("phone")
    return redirect("/home")

@app.route("/skip")
def skip():
    session["user"] = "Guest"
    session["phone"] = ""
    return redirect("/home")

# ================= HOME =================
@app.route("/home")
def home():
    products = supabase.table("products").select("*").execute().data
    return render_template("home.html", products=products)

# ================= PRODUCT =================
@app.route("/product/<int:id>")
def product(id):
    p = supabase.table("products").select("*").eq("id", id).execute().data[0]
    return render_template("product.html", p=p)

# ================= GUEST CHECK =================
def is_guest():
    return session.get("user") == "Guest"

def guest_block():
    return render_template("guest.html")

# ================= CART =================
@app.route("/add_to_cart/<int:id>")
def add_to_cart(id):
    if is_guest():
        return guest_block()

    phone = session.get("phone")

    supabase.table("cart").insert({
        "product_id": id,
        "phone": phone
    }).execute()

    return redirect("/cart")

@app.route("/cart")
def cart():
    if is_guest():
        return guest_block()

    phone = session.get("phone")

    cart_items = supabase.table("cart").select("*").eq("phone", phone).execute().data

    products = []
    for item in cart_items:
        p = supabase.table("products").select("*").eq("id", item["product_id"]).execute().data
        if p:
            products.append(p[0])

    return render_template("cart.html", products=products)

@app.route("/remove_cart/<int:id>")
def remove_cart(id):
    phone = session.get("phone")
    supabase.table("cart").delete().eq("product_id", id).eq("phone", phone).execute()
    return redirect("/cart")

# ================= ORDER =================
@app.route("/order", methods=["POST"])
def order():
    if is_guest():
        return guest_block()

    phone = session.get("phone")

    product_name = request.form.get("product_name")

    prod = supabase.table("products").select("*").eq("name", product_name).execute().data
    image = prod[0]["image"] if prod else ""

    supabase.table("orders").insert({
        "product_name": product_name,
        "quantity": request.form.get("quantity"),
        "phone": phone,
        "image": image,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    }).execute()

    return redirect("/orders")

@app.route("/orders")
def orders():
    if is_guest():
        return guest_block()

    phone = session.get("phone")

    orders = supabase.table("orders").select("*").eq("phone", phone).execute().data

    return render_template("orders.html", orders=orders)

# ================= ME =================
@app.route("/me")
def me():
    return render_template("me.html")

@app.route("/update_profile", methods=["POST"])
def update_profile():
    session["user"] = request.form.get("name")
    session["phone"] = request.form.get("phone")
    return redirect("/me")

# ================= RUN =================
if __name__ == "__main__":
    app.run()