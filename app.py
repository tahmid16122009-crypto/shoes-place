from flask import Flask, render_template, request, redirect, url_for, session
from supabase import create_client

app = Flask(__name__)
app.secret_key = "secret123"

SUPABASE_URL = "YOUR_SUPABASE_URL"
SUPABASE_KEY = "YOUR_SUPABASE_KEY"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# =========================
# LOGIN PAGE
# =========================
@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/do_login", methods=["POST"])
def do_login():
    session["user"] = request.form["name"]
    return redirect(url_for("home"))

@app.route("/skip_login")
def skip_login():
    session["user"] = "Guest"
    return redirect(url_for("home"))

# =========================
# HOME
# =========================
@app.route("/")
def home():
    products = supabase.table("products").select("*").execute().data
    return render_template("home.html", products=products)

# =========================
# PRODUCT PAGE
# =========================
@app.route("/product/<int:id>")
def product(id):
    p = supabase.table("products").select("*").eq("id", id).execute().data[0]
    return render_template("product.html", p=p)

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
            "address": request.form["address"],  # manual full address
            "product_id": request.form.get("product_id"),
            "status": "pending"
        }

        supabase.table("orders").insert(data).execute()
        return redirect(url_for("home"))

    except Exception as e:
        return f"ORDER ERROR: {str(e)}"

# =========================
# ADMIN PANEL (FIXED ROUTE)
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
        return f"ADD ERROR: {str(e)}"

# =========================
# DELETE PRODUCT
# =========================
@app.route("/delete/<int:id>")
def delete(id):
    supabase.table("products").delete().eq("id", id).execute()
    return redirect(url_for("admin"))

# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)