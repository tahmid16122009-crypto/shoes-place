from flask import Flask, render_template, request, redirect, url_for, session
from supabase import create_client
import os

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
    session["user"] = request.form["name"]
    session["phone"] = request.form["phone"]
    return redirect("/home")

@app.route("/skip")
def skip():
    session["user"] = "Guest"
    session["phone"] = "N/A"
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

# ================= ORDER =================
@app.route("/order", methods=["POST"])
def order():
    data = {
        "name": session.get("user"),
        "phone": session.get("phone"),
        "address": request.form["address"],
        "product_id": request.form["product_id"],
        "status": "pending"
    }

    supabase.table("orders").insert(data).execute()
    return redirect("/home")

# ================= ADMIN =================
@app.route("/admin")
def admin():
    products = supabase.table("products").select("*").execute().data
    orders = supabase.table("orders").select("*").execute().data
    return render_template("admin.html", products=products, orders=orders)

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

# ================= RUN =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)