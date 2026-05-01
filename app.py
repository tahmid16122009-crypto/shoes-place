import os, time
from flask import Flask, render_template, request, redirect, session
from supabase import create_client

app = Flask(__name__)
app.secret_key = "secret123"

# ===== SUPABASE =====
SUPABASE_URL = "https://hjwgjopshptmhlkcdagh.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

ADMIN_PASSWORD = "Tahmid1122"

# ================= HOME =================
@app.route("/")
def index():
    return redirect("/home")

@app.route("/home")
def home():
    products = supabase.table("products").select("*").execute().data or []
    return render_template("home.html", products=products)

# ================= PRODUCT =================
@app.route("/product/<int:pid>")
def product(pid):
    p = supabase.table("products").select("*").eq("id", pid).execute().data
    if not p:
        return "Product not found"
    return render_template("product.html", p=p[0])

# ================= CART =================
@app.route("/add/<int:pid>")
def add(pid):
    cart = session.get("cart", {})
    cart[str(pid)] = cart.get(str(pid), 0) + 1
    session["cart"] = cart
    return redirect("/cart")

@app.route("/cart")
def cart():
    cart = session.get("cart", {})
    items = []

    for pid, qty in cart.items():
        r = supabase.table("products").select("*").eq("id", int(pid)).execute()
        if r.data:
            p = r.data[0]
            p["qty"] = qty
            items.append(p)

    return render_template("cart.html", items=items)

# ================= ORDER =================
@app.route("/order", methods=["POST"])
def order():
    cart = session.get("cart", {})

    name = request.form.get("name") or ""
    phone = request.form.get("phone") or ""
    district = request.form.get("district") or ""
    union = request.form.get("union") or ""
    village = request.form.get("village") or ""
    road = request.form.get("road") or ""
    holding = request.form.get("holding") or ""
    address = request.form.get("address") or ""

    for pid, qty in cart.items():
        product = supabase.table("products").select("*").eq("id", int(pid)).execute().data
        if product:
            p = product[0]

            supabase.table("orders").insert({
                "product_name": p.get("name",""),
                "customer_name": name,
                "phone": phone,
                "district": district,
                "union": union,
                "village": village,
                "road": road,
                "holding": holding,
                "address": address,
                "quantity": qty,
                "status": "Order placed"
            }).execute()

    session["cart"] = {}
    return redirect("/orders")

# ================= USER ORDERS =================
@app.route("/orders")
def orders():
    data = supabase.table("orders").select("*").execute().data or []
    return render_template("orders.html", orders=data)

# ================= ME =================
@app.route("/me")
def me():
    return render_template("me.html")

# ================= ADMIN =================
@app.route("/admin", methods=["GET","POST"])
def admin():
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/admin/dashboard")
    return render_template("admin_login.html")

@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get("admin"):
        return redirect("/admin")

    products = supabase.table("products").select("*").execute().data or []
    return render_template("admin.html", products=products)

# ================= ADD PRODUCT =================
@app.route("/add_product", methods=["POST"])
def add_product():
    if not session.get("admin"):
        return redirect("/admin")

    name = request.form.get("name") or ""
    price = request.form.get("price") or ""
    description = request.form.get("description") or ""

    file = request.files.get("image")
    image_url = ""

    try:
        if file and file.filename != "":
            filename = str(int(time.time())) + "_" + file.filename

            supabase.storage.from_("products").upload(
                filename,
                file.read(),
                {"content-type": file.content_type}
            )

            image_url = f"{SUPABASE_URL}/storage/v1/object/public/products/{filename}"
    except Exception as e:
        print("IMAGE ERROR:", e)

    supabase.table("products").insert({
        "name": name,
        "price": price,
        "image": image_url,
        "description": description
    }).execute()

    return redirect("/admin/dashboard")

# ================= DELETE PRODUCT =================
@app.route("/delete/<int:pid>")
def delete_product(pid):
    if not session.get("admin"):
        return redirect("/admin")

    supabase.table("products").delete().eq("id", pid).execute()
    return redirect("/admin/dashboard")

# ================= EDIT PRODUCT =================
@app.route("/edit/<int:pid>", methods=["GET","POST"])
def edit(pid):
    if not session.get("admin"):
        return redirect("/admin")

    if request.method == "POST":
        supabase.table("products").update({
            "name": request.form.get("name"),
            "price": request.form.get("price"),
            "description": request.form.get("description")
        }).eq("id", pid).execute()

        return redirect("/admin/dashboard")

    p = supabase.table("products").select("*").eq("id", pid).execute().data[0]
    return render_template("edit_product.html", p=p)

# ================= ADMIN ORDERS =================
@app.route("/admin/orders")
def admin_orders():
    if not session.get("admin"):
        return redirect("/admin")

    orders = supabase.table("orders").select("*").execute().data or []
    return render_template("admin_orders.html", orders=orders)

# ================= CHANGE STATUS =================
@app.route("/status/<int:oid>/<status>")
def change_status(oid, status):
    if not session.get("admin"):
        return redirect("/admin")

    supabase.table("orders").update({
        "status": status
    }).eq("id", oid).execute()

    return redirect("/admin/orders")

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)