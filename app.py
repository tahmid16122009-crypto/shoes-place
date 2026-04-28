from flask import Flask, request, redirect, session
from pymongo import MongoClient
import uuid

app = Flask(__name__)
app.secret_key = "shop_secret_key"

# ===== DATABASE =====
client = MongoClient("mongodb+srv://tahmid16122009_db_user:xha1hQWvPVgPfNAc@cluster0.uxtdbbt.mongodb.net/?retryWrites=true&w=majority")

db = client["shop"]
products_col = db["products"]
orders_col = db["orders"]

ADMIN_PASS = "Tahmid1122"

# ===== STYLE =====
def ui():
    return """
    <style>
    body{font-family:sans-serif;background:#f5f5f5;text-align:center}
    .box{background:white;padding:15px;margin:10px;border-radius:10px;box-shadow:0 0 5px #ccc}
    a,button{padding:8px 12px;margin:5px;text-decoration:none}
    button{background:#007bff;color:white;border:none;border-radius:5px}
    input{padding:8px;margin:5px;width:80%}
    </style>
    """

# ===== HOME =====
@app.route('/')
def home():
    return ui() + """
    <h1>🛍️ Shop System</h1>
    <a href='/products'>Products</a>
    <a href='/cart'>Cart</a>
    <a href='/admin'>Admin</a>
    """

# ===== PRODUCTS =====
@app.route('/products')
def products():
    html = ui() + "<h2>Products</h2>"

    try:
        for p in products_col.find():
            html += f"""
            <div class='box'>
                <h3>{p.get('name','')}</h3>
                <p>💰 {p.get('price',0)}৳</p>

                <form action='/add_to_cart' method='POST'>
                    <input type='hidden' name='id' value='{p.get("id")}'>
                    <button>Add to Cart</button>
                </form>

                <a href='/order/{p.get("id")}'>Order Now</a>
            </div>
            """
    except:
        html += "<p>Error loading products</p>"

    return html

# ===== ADD TO CART =====
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    pid = request.form.get('id')

    cart = session.get('cart', [])

    if not isinstance(cart, list):
        cart = []

    if pid:
        cart.append(pid)

    session['cart'] = cart

    return redirect('/cart')

# ===== CART =====
@app.route('/cart')
def cart():
    html = ui() + "<h2>Cart</h2>"
    cart = session.get('cart', [])

    if not isinstance(cart, list):
        cart = []

    total = 0

    try:
        for pid in cart:
            p = products_col.find_one({"id": pid})
            if not p:
                continue

            price = int(p.get("price", 0))
            total += price

            html += f"""
            <div class='box'>
                {p.get('name','')} - {price}৳
                <br>
                <a href='/order/{pid}'>Order</a>
            </div>
            """

        if len(cart) == 0:
            html += "<p>Cart empty</p>"

        html += f"<h3>Total: {total}৳</h3>"

    except:
        html += "<p>Cart error handled</p>"

    return html

# ===== ORDER PAGE =====
@app.route('/order/<pid>')
def order(pid):
    p = products_col.find_one({"id": pid})

    if not p:
        return "Product not found"

    return ui() + f"""
    <h2>Order {p.get('name')}</h2>

    <form action='/place_order/{pid}' method='POST'>
        <input name='name' placeholder='Name'><br>
        <input name='phone' placeholder='Phone'><br>
        <input name='address' placeholder='Address'><br>
        <button>Confirm Order</button>
    </form>
    """

# ===== PLACE ORDER =====
@app.route('/place_order/<pid>', methods=['POST'])
def place_order(pid):
    p = products_col.find_one({"id": pid})

    if not p:
        return "Error"

    try:
        orders_col.insert_one({
            "product": p.get('name'),
            "price": p.get('price'),
            "name": request.form.get('name'),
            "phone": request.form.get('phone'),
            "address": request.form.get('address')
        })
    except:
        return "Order failed"

    return ui() + "<h2 style='color:green'>Order Success</h2>"

# ===== ADMIN =====
@app.route('/admin')
def admin():
    return ui() + """
    <h2>Admin Login</h2>
    <form action='/dashboard' method='POST'>
        <input name='pass' placeholder='Password'>
        <button>Login</button>
    </form>
    """

# ===== DASHBOARD =====
@app.route('/dashboard', methods=['POST'])
def dashboard():
    if request.form.get('pass') != ADMIN_PASS:
        return "Wrong password"

    html = ui() + """
    <h2>Admin Panel</h2>

    <h3>Add Product</h3>
    <form action='/add_product' method='POST'>
        <input name='name' placeholder='Name'><br>
        <input name='price' placeholder='Price'><br>
        <button>Add</button>
    </form>

    <h3>Orders</h3>
    """

    try:
        for o in orders_col.find():
            html += f"""
            <div class='box'>
                Product: {o.get('product')}<br>
                Name: {o.get('name')}<br>
                Phone: {o.get('phone')}<br>
                Address: {o.get('address')}
            </div>
            """
    except:
        html += "<p>No orders</p>"

    return html

# ===== ADD PRODUCT =====
@app.route('/add_product', methods=['POST'])
def add_product():
    try:
        products_col.insert_one({
            "id": str(uuid.uuid4()),
            "name": request.form.get('name'),
            "price": request.form.get('price')
        })
    except:
        pass

    return redirect('/products')

# ===== RUN =====
if __name__ == "__main__":
    app.run(debug=True)