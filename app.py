from flask import Flask, render_template, request, redirect, session, url_for
from supabase import create_client
import os

app = Flask(__name__)
app.secret_key = "secret123"

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

ADMIN_PASS = "Tahmid1122"

# ---------- LOGIN ----------
@app.route("/")
def index():
    if "user" not in session:
        return render_template("login.html")
    return redirect("/home")

@app.route("/login", methods=["POST"])
def login():
    session["user"] = request.form["name"]
    session["phone"] = request.form["phone"]
    return redirect("/home")

@app.route("/skip")
def skip():
    session["user"] = "Guest"
    session["phone"] = ""
    return redirect("/home")

# ---------- HOME ----------
@app.route("/home")
def home():
    products = supabase.table("products").select("*").execute().data
    return render_template("home.html", products=products)

# ---------- PRODUCT ----------
@app.route("/product/<int:id>")
def product(id):
    p = supabase.table("products").select("*").eq("id", id).execute().data[0]
    return render_template("product.html", p=p)

# ---------- CART ----------
@app.route("/add_to_cart/<int:id>")
def add_to_cart(id):
    cart = session.get("cart", [])
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

# ---------- ORDER ----------
@app.route("/order", methods=["POST"])
def order():
    data = {
        "name": request.form["name"],
        "phone": request.form["phone"],
        "product_name": request.form["product_name"],
        "quantity": request.form["quantity"],
        "district": request.form["district"],
        "upazila": request.form["upazila"],
        "union": request.form["union"],
        "road": request.form.get("road", ""),
        "holding": request.form.get("holding", ""),
        "status": "pending"
    }
    supabase.table("orders").insert(data).execute()
    return redirect("/orders")

@app.route("/orders")
def orders():
    orders = supabase.table("orders").select("*").execute().data
    return render_template("orders.html", orders=orders)

# ---------- ADMIN ----------
@app.route("/admin", methods=["GET","POST"])
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

@app.route("/add_product", methods=["POST"])
def add_product():
    data = {
        "name": request.form["name"],
        "price": request.form["price"],
        "description": request.form["description"],
        "image": request.form["image"]
    }
    supabase.table("products").insert(data).execute()
    return redirect("/admin")

@app.route("/delete/<int:id>")
def delete(id):
    supabase.table("products").delete().eq("id", id).execute()
    return redirect("/admin")

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))