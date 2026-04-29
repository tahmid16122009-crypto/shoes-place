import os
import uuid
from flask import Flask, render_template, request, redirect, session
from supabase import create_client

app = Flask(__name__)
app.secret_key = "secret123"

# ================= SUPABASE =================
SUPABASE_URL = "https://hjwgjopshptmhlkcdagh.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

ADMIN_PASSWORD = "Tahmid1122"

# ================= HOME =================
@app.route("/")
def home():
    user = session.get("user")

    try:
        products = supabase.table("products").select("*").execute().data or []
        orders = supabase.table("orders").select("*").execute().data or []
    except:
        products = []
        orders = []

    cart = session.get("cart", [])
    cart_items = []

    for pid in cart:
        try:
            r = supabase.table("products").select("*").eq("id", pid).execute()
            if r.data:
                cart_items.append(r.data[0])
        except:
            pass

    return render_template("index.html",
                           products=products,
                           cart_items=cart_items,
                           orders=orders,
                           user=user)

# ================= LOGIN =================
@app.route("/login", methods=["POST"])
def login():
    session["user"] = {
        "name": request.form.get("name"),
        "phone": request.form.get("phone")
    }
    return redirect("/")

# ================= CART =================
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
    user = session.get("user")

    if not user:
        return redirect("/")

    cart = session.get("cart", [])

    for pid in cart:
        try:
            product = supabase.table("products").select("*").eq("id", pid).execute().data
            if product:
                product = product[0]

                supabase.table("orders").insert({
                    "product_name": product["name"],
                    "customer_name": user["name"],
                    "phone": user["phone"],
                    "address": request.form.get("address"),
                    "quantity": 1,
                    "status": "Order placed"
                }).execute()
        except:
            pass

    session["cart"] = []
    return redirect("/")

# ================= ADMIN =================
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/admin/dashboard")
        return "Wrong password"

    return render_template("admin_login.html")

# ================= ADMIN DASHBOARD =================
@app.route("/admin/dashboard")
def dashboard():
    if not session.get("admin"):
        return redirect("/admin")

    products = supabase.table("products").select("*").execute().data or []
    orders = supabase.table("orders").select("*").execute().data or []

    return render_template("admin.html",
                           products=products,
                           orders=orders)

# ================= ADD PRODUCT =================
@app.route("/add_product", methods=["POST"])
def add_product():
    if not session.get("admin"):
        return redirect("/admin")

    name = request.form.get("name")
    price = request.form.get("price")
    description = request.form.get("description")
    file = request.files.get("image")

    try:
        filename = str(uuid.uuid4()) + file.filename

        supabase.storage.from_("products").upload(filename, file.read())
        image_url = supabase.storage.from_("products").get_public_url(filename)

        supabase.table("products").insert({
            "name": name,
            "price": price,
            "description": description,
            "image": image_url
        }).execute()

    except Exception as e:
        return f"Upload error: {e}"

    return redirect("/admin/dashboard")

# ================= UPDATE ORDER =================
@app.route("/update_order/<int:oid>/<status>")
def update_order(oid, status):
    if not session.get("admin"):
        return redirect("/admin")

    supabase.table("orders").update({
        "status": status
    }).eq("id", oid).execute()

    return redirect("/admin/dashboard")

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)