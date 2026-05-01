from flask import Flask, render_template, request, redirect, url_for
from supabase import create_client
import os

app = Flask(__name__)

# =========================
# SUPABASE CONFIG
# =========================
SUPABASE_URL = "YOUR_SUPABASE_URL"
SUPABASE_KEY = "YOUR_SUPABASE_KEY"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# =========================
# HOME - PRODUCTS LIST
# =========================
@app.route("/")
def home():
    products = supabase.table("products").select("*").execute().data
    return render_template("home.html", products=products)

# =========================
# PRODUCT DETAILS PAGE
# =========================
@app.route("/product/<int:id>")
def product(id):
    try:
        res = supabase.table("products").select("*").eq("id", id).execute()
        product = res.data[0]
        return render_template("product.html", p=product)
    except:
        return "PRODUCT ERROR"

# =========================
# ORDER SAVE
# =========================
@app.route("/order", methods=["POST"])
def order():
    try:
        data = {
            "name": request.form["name"],
            "phone": request.form["phone"],
            "district": request.form["district"],
            "upazila": request.form["union"],
            "village": request.form["village"],
            "road": request.form.get("road", ""),
            "holding": request.form.get("holding", ""),
            "product_id": request.form.get("product_id", None),
            "status": "pending"
        }

        supabase.table("orders").insert(data).execute()

        return redirect(url_for("home"))

    except Exception as e:
        return f"ORDER ERROR: {str(e)}"

# =========================
# ADMIN PANEL
# =========================
@app.route("/admin")
def admin():
    products = supabase.table("products").select("*").execute().data
    orders = supabase.table("orders").select("*").execute().data

    return render_template("admin.html", products=products, orders=orders)

# =========================
# ADD PRODUCT
# =========================
@app.route("/add_product", methods=["POST"])
def add_product():
    try:
        data = {
            "name": request.form["name"],
            "price": request.form["price"],
            "description": request.form["description"],
            "image": request.form["image"]
        }

        supabase.table("products").insert(data).execute()

        return redirect(url_for("admin"))

    except Exception as e:
        return f"ADD PRODUCT ERROR: {str(e)}"

# =========================
# DELETE PRODUCT
# =========================
@app.route("/delete_product/<int:id>")
def delete_product(id):
    supabase.table("products").delete().eq("id", id).execute()
    return redirect(url_for("admin"))

# =========================
# UPDATE STATUS ORDER
# =========================
@app.route("/update_order/<int:id>/<status>")
def update_order(id, status):
    supabase.table("orders").update({"status": status}).eq("id", id).execute()
    return redirect(url_for("admin"))

# =========================
# RUN APP
# =========================
if __name__ == "__main__":
    app.run(debug=True)