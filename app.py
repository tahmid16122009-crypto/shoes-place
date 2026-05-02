from flask import Flask, render_template, request, redirect, session, url_for
from supabase import create_client
import os
import uuid

app = Flask(__name__)
app.secret_key = "secret123"

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

ADMIN_PASS = "Tahmid1122"

# ========= LOGIN =========
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

# ========= HOME =========
@app.route("/home")
def home():
    products = supabase.table("products").select("*").execute().data
    return render_template("home.html", products=products)

# ========= PRODUCT =========
@app.route("/product/<int:id>")
def product(id):
    res = supabase.table("products").select("*").eq("id", id).execute().data
    return render_template("product.html", p=res[0])

# ========= CART =========
@app.route("/add_to_cart/<int:id>")
def add_to_cart(id):
    cart = session.get("cart", [])
    if id not in cart:
        cart.append(id)
    session["cart"] = cart
    return redirect("/cart")

@app.route("/cart")
def cart():
    cart_ids = session.get("cart", [])
    products = []
    for cid in cart_ids:
        res = supabase.table("products").select("*").eq("id", cid).execute().data
        if res:
            products.append(res[0])
    return render_template("cart.html", products=products)

@app.route("/remove_cart/<int:id>")
def remove_cart(id):
    cart = session.get("cart", [])
    if id in cart:
        cart.remove(id)
    session["cart"] = cart
    return redirect("/cart")

# ========= ORDER =========
@app.route("/order", methods=["POST"])
def order():
    try:
        data = {
            "product_name": request.form.get("product_name"),
            "quantity": request.form.get("quantity"),
            "phone": request.form.get("phone"),
            "district": request.form.get("district"),
            "status": "pending"
        }

        # name থাকলে add
        if request.form.get("name"):
            data["name"] = request.form.get("name")

        supabase.table("orders").insert(data).execute()

        return redirect("/orders")

    except Exception as e:
        return f"ORDER ERROR: {str(e)}"

@app.route("/orders")
def orders():
    orders = supabase.table("orders").select("*").execute().data
    return render_template("orders.html", orders=orders)

# ========= ME =========
@app.route("/me")
def me():
    return render_template("me.html")

@app.route("/update_profile", methods=["POST"])
def update_profile():
    session["user"] = request.form.get("name")
    session["phone"] = request.form.get("phone")
    return redirect("/me")

# ========= ADMIN =========
@app.route("/admin", methods=["GET","POST"])
def admin():
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASS:
            session["admin"] = True

    if not session.get("admin"):
        return render_template("admin_login.html")

    products = supabase.table("products").select("*").execute().data
    return render_template("admin.html", products=products)

# ========= ADD PRODUCT (IMAGE UPLOAD FIX) =========
@app.route("/add_product", methods=["POST"])
def add_product():
    try:
        file = request.files.get("image")

        image_url = ""
        if file:
            filename = str(uuid.uuid4()) + file.filename
            supabase.storage.from_("products").upload(filename, file)
            image_url = f"{SUPABASE_URL}/storage/v1/object/public/products/{filename}"

        data = {
            "name": request.form.get("name"),
            "price": request.form.get("price"),
            "description": request.form.get("description"),
            "image": image_url
        }

        supabase.table("products").insert(data).execute()

        return redirect("/admin")

    except Exception as e:
        return f"ADD ERROR: {str(e)}"

# ========= DELETE =========
@app.route("/delete/<int:id>")
def delete(id):
    supabase.table("products").delete().eq("id", id).execute()
    return redirect("/admin")

# ========= RUN =========
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))