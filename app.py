import os
import uuid
from flask import Flask, render_template, request, redirect, session
from supabase import create_client

app = Flask(__name__)
app.secret_key = "secret123"

# ================= SUPABASE =================
SUPABASE_URL = "https://hjwgjopshptmhlkcdagh.supabase.co"

# 🔥 SECRET KEY now comes from Render (NOT GitHub)
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

ADMIN_PASSWORD = "Tahmid1122"

# ================= HOME =================
@app.route("/")
def home():
    products = supabase.table("products").select("*").execute().data or []

    cart_ids = session.get("cart", [])
    cart_items = []

    for pid in cart_ids:
        res = supabase.table("products").select("*").eq("id", pid).execute()
        if res.data:
            cart_items.append(res.data[0])

    return render_template("index.html", products=products, cart_items=cart_items)

# ================= ADD TO CART =================
@app.route("/add/<int:pid>")
def add(pid):
    if "cart" not in session:
        session["cart"] = []

    session["cart"].append(int(pid))
    session.modified = True
    return redirect("/")

# ================= ORDER =================
@app.route("/order", methods=["POST"])
def order():
    name = request.form.get("name")
    phone = request.form.get("phone")
    address = request.form.get("address")

    cart = session.get("cart", [])

    for pid in cart:
        supabase.table("orders").insert({
            "product_name": str(pid),
            "customer_name": name,
            "phone": phone,
            "address": address,
            "quantity": 1
        }).execute()

    session["cart"] = []
    return redirect("/")

# ================= ADMIN PANEL =================
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        if request.form.get("password") != ADMIN_PASSWORD:
            return "Wrong Password"

    return render_template("admin.html")

# ================= ADD PRODUCT (IMAGE UPLOAD) =================
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

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)