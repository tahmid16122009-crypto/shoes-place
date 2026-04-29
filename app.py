import os
from flask import Flask, render_template, request, redirect, session
from supabase import create_client

app = Flask(__name__)
app.secret_key = "secret123"

# ================= SAFE SUPABASE INIT =================
SUPABASE_URL = "https://hjwgjopshptmhlkcdagh.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = None

if SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print("Supabase init error:", e)
else:
    print("SUPABASE_KEY NOT FOUND")

ADMIN_PASSWORD = "Tahmid1122"

# ================= HOME (CRASH PROOF) =================
@app.route("/home")
def home():
    try:
        user = session.get("user")

        products = []
        if supabase:
            res = supabase.table("products").select("*").execute()
            products = res.data or []

        cart_ids = session.get("cart", [])
        cart_items = []

        if supabase:
            for pid in cart_ids:
                try:
                    r = supabase.table("products").select("*").eq("id", pid).execute()
                    if r.data:
                        cart_items.append(r.data[0])
                except:
                    pass

        return render_template("home.html",
                               products=products,
                               cart_items=cart_items,
                               user=user)

    except Exception as e:
        return f"HOME ERROR: {str(e)}"

# ================= ROOT =================
@app.route("/")
def root():
    return redirect("/home")

# ================= LOGIN =================
@app.route("/login", methods=["POST"])
def login():
    session["user"] = {
        "name": request.form.get("name"),
        "phone": request.form.get("phone")
    }
    return redirect("/home")

# ================= CART =================
@app.route("/add/<int:pid>")
def add(pid):
    cart = session.get("cart", [])
    if pid not in cart:
        cart.append(pid)
    session["cart"] = cart
    return redirect("/home")

# ================= CART PAGE =================
@app.route("/cart")
def cart():
    try:
        cart = session.get("cart", [])
        items = []

        if supabase:
            for pid in cart:
                r = supabase.table("products").select("*").eq("id", pid).execute()
                if r.data:
                    items.append(r.data[0])

        return render_template("cart.html", items=items)

    except Exception as e:
        return f"CART ERROR: {e}"

# ================= ORDER =================
@app.route("/order", methods=["POST"])
def order():
    try:
        user = session.get("user")
        cart = session.get("cart", [])

        if not supabase:
            return "DB not connected"

        for pid in cart:
            product = supabase.table("products").select("*").eq("id", pid).execute().data
            if product:
                p = product[0]

                supabase.table("orders").insert({
                    "product_name": p["name"],
                    "customer_name": user["name"] if user else "Guest",
                    "phone": user["phone"] if user else "000",
                    "address": request.form.get("address"),
                    "quantity": 1,
                    "status": "Order placed"
                }).execute()

        session["cart"] = []
        return redirect("/orders")

    except Exception as e:
        return f"ORDER ERROR: {e}"

# ================= ORDERS =================
@app.route("/orders")
def orders():
    try:
        user = session.get("user")
        all_orders = supabase.table("orders").select("*").execute().data or []

        if user:
            filtered = [o for o in all_orders if o["phone"] == user["phone"]]
        else:
            filtered = []

        return render_template("orders.html", orders=filtered)

    except Exception as e:
        return f"ORDERS ERROR: {e}"

# ================= ME =================
@app.route("/me")
def me():
    return render_template("me.html", user=session.get("user"))

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)