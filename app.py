from flask import Flask, render_template, request, redirect, session
from supabase import create_client
import os

app = Flask(__name__)
app.secret_key = "secret123"

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

ADMIN_PASS = "Tahmid1122"

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
    try:
        products = supabase.table("products").select("*").execute().data
    except:
        products = []
    return render_template("home.html", products=products)

# ================= PRODUCT =================
@app.route("/product/<int:id>")
def product(id):
    res = supabase.table("products").select("*").eq("id", id).execute().data
    if not res:
        return "Product not found"
    return render_template("product.html", p=res[0])

# ================= CART =================
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

# ================= ORDER =================
@app.route("/order", methods=["POST"])
def order():
    try:
        data = {
            "name": request.form.get("name"),
            "phone": request.form.get("phone"),
            "product_name": request.form.get("product_name"),
            "quantity": request.form.get("quantity"),
            "district": request.form.get("district"),
            "upazila": request.form.get("upazila"),
            "union": request.form.get("union"),
            "road": request.form.get("road"),
            "holding": request.form.get("holding"),
            "status": "pending"
        }

        supabase.table("orders").insert(data).execute()
        return redirect("/orders")

    except Exception as e:
        return f"ORDER ERROR: {str(e)}"

@app.route("/orders")
def orders():
    try:
        orders = supabase.table("orders").select("*").execute().data
    except:
        orders = []
    return render_template("orders.html", orders=orders)

# ================= ME =================
@app.route("/me")
def me():
    if session.get("user") == "Guest":
        return render_template("login.html")
    return render_template("me.html")

# ================= ADMIN =================
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASS:
            session["admin"] = True
        else:
            return "Wrong password"

    if not session.get("admin"):
        return render_template("admin_login.html")

    products = supabase.table("products").select("*").execute().data
    return render_template("admin.html", products=products)

# ================= ADD PRODUCT =================
@app.route("/add_product", methods=["POST"])
def add_product():
    try:
        data = {
            "name": request.form.get("name"),
            "price": request.form.get("price"),
            "description": request.form.get("description"),
            "image": request.form.get("image")
        }

        supabase.table("products").insert(data).execute()
        return redirect("/admin")

    except Exception as e:
        return f"ADD ERROR: {str(e)}"

# ================= DELETE =================
@app.route("/delete/<int:id>")
def delete(id):
    try:
        supabase.table("products").delete().eq("id", id).execute()
    except:
        pass
    return redirect("/admin")

# ================= RUN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))