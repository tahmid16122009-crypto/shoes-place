from flask import Flask, render_template, request, redirect, session
from supabase import create_client

app = Flask(__name__)
app.secret_key = "secret123"

# ✅ Supabase Connect
SUPABASE_URL = "https://hjwgjopshptmhlkcdagh.supabase.co"
SUPABASE_KEY = "sb_publishable_kz0El2AdaJuoxOADnqABdQ_Mnve6_GM"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------- HOME (Products) ----------------
@app.route("/")
def home():
    res = supabase.table("products").select("*").execute()
    products = res.data if res.data else []
    return render_template("index.html", products=products)

# ---------------- ADD TO CART ----------------
@app.route("/add_to_cart/<int:pid>")
def add_to_cart(pid):
    if "cart" not in session:
        session["cart"] = []

    session["cart"].append(pid)
    session.modified = True
    return redirect("/")

# ---------------- CART PAGE ----------------
@app.route("/cart")
def cart():
    cart_ids = session.get("cart", [])
    items = []

    for pid in cart_ids:
        res = supabase.table("products").select("*").eq("id", pid).execute()
        if res.data:
            items.append(res.data[0])

    return render_template("cart.html", items=items)

# ---------------- ORDER ----------------
@app.route("/order", methods=["POST"])
def order():
    name = request.form.get("name")
    phone = request.form.get("phone")
    address = request.form.get("address")

    cart_ids = session.get("cart", [])

    for pid in cart_ids:
        supabase.table("orders").insert({
            "product_name": str(pid),
            "customer_name": name,
            "phone": phone,
            "address": address,
            "quantity": 1
        }).execute()

    session["cart"] = []
    return "Order Placed Successfully!"

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)