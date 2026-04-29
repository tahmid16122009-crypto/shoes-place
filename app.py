import os
import uuid
from flask import Flask, render_template, request, redirect, session
from supabase import create_client

app = Flask(__name__)
app.secret_key = "secret123"

# ================= SUPABASE =================
SUPABASE_URL = "https://hjwgjopshptmhlkcdagh.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_KEY:
    print("ERROR: SUPABASE_KEY missing")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

ADMIN_PASSWORD = "Tahmid1122"

# ================= HOME =================
@app.route("/")
def home():
    try:
        products = supabase.table("products").select("*").execute().data or []
    except Exception as e:
        return f"Supabase error: {e}"

    cart_ids = session.get("cart", [])
    cart_items = []

    for pid in cart_ids:
        try:
            res = supabase.table("products").select("*").eq("id", pid).execute()
            if res.data:
                cart_items.append(res.data[0])
        except:
            pass

    orders = session.get("orders", [])

    return render_template("index.html",
                           products=products,
                           cart_items=cart_items,
                           orders=orders)

# ================= ADD TO CART =================
@app.route("/add/<int:pid>")
def add(pid):
    cart = session.get("cart", [])
    if pid not in cart:
        cart.append(pid)
    session["cart"] = cart
    return redirect("/")

# ================= ORDER =================
@app.route("/order", methods=["POST"])
def order():
    name = request.form.get("name")
    phone = request.form.get("phone")
    address = request.form.get("address")

    cart = session.get("cart", [])
    user_orders = session.get("orders", [])

    for pid in cart:
        try:
            product = supabase.table("products").select("*").eq("id", pid).execute().data
            if product:
                product = product[0]

                order_data = {
                    "product_name": product.get("name"),
                    "customer_name": name,
                    "phone": phone,
                    "address": address,
                    "status": "Order placed"
                }

                supabase.table("orders").insert(order_data).execute()
                user_orders.append(order_data)
        except Exception as e:
            return f"Order error: {e}"

    session["orders"] = user_orders
    session["cart"] = []
    return redirect("/")

# ================= ADMIN LOGIN =================
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        password = request.form.get("password")
        if password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/admin/dashboard")
        else:
            return "Wrong password"

    return render_template("admin_login.html")

# ================= ADMIN DASHBOARD =================
@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get("admin"):
        return redirect("/admin")

    try:
        products = supabase.table("products").select("*").execute().data or []
        orders = supabase.table("orders").select("*").execute().data or []

        return render_template("admin.html",
                               products=products,
                               orders=orders)

    except Exception as e:
        return f"ADMIN ERROR: {e}"

# ================= ADD PRODUCT =================
@app.route("/add_product", methods=["POST"])
def add_product():
    if not session.get("admin"):
        return redirect("/admin")

    try:
        name = request.form.get("name")
        price = request.form.get("price")
        file = request.files.get("image")

        if file:
            filename = str(uuid.uuid4()) + file.filename

            supabase.storage.from_("products").upload(filename, file.read())
            image_url = supabase.storage.from_("products").get_public_url(filename)

            supabase.table("products").insert({
                "name": name,
                "price": price,
                "image": image_url
            }).execute()

        return redirect("/admin/dashboard")

    except Exception as e:
        return f"ADD PRODUCT ERROR: {e}"

# ================= UPDATE ORDER =================
@app.route("/update_order/<int:oid>/<status>")
def update_order(oid, status):
    if not session.get("admin"):
        return redirect("/admin")

    try:
        supabase.table("orders").update({"status": status}).eq("id", oid).execute()
        return redirect("/admin/dashboard")
    except Exception as e:
        return f"UPDATE ERROR: {e}"

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)