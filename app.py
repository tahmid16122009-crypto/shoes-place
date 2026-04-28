from flask import Flask, request, redirect, session

from pymongo import MongoClient
import uuid

app = Flask(__name__)
app.secret_key = "secret123"

# ===== DATABASE =====
client = MongoClient("mongodb+srv://tahmid16122009_db_user:xha1hQWvPVgPfNAc@cluster0.uxtdbbt.mongodb.net/?retryWrites=true&w=majority")
db = client["shop"]

products_col = db["products"]
orders_col = db["orders"]

ADMIN_PASS = "Tahmid1122"

# ===== SIMPLE STYLE =====
def style():
    return """
    <style>
    body{font-family:sans-serif;background:#f2f2f2;text-align:center}
    .card{background:#fff;padding:15px;margin:10px;border-radius:10px}
    button{padding:10px 15px;border:none;background:#007bff;color:#fff;border-radius:5px}
    input{padding:8px;margin:5px;width:80%}
    a{display:inline-block;margin:5px}
    </style>
    """

# ===== HOME =====
@app.route('/')
def home():
    return style() + """
    <h1>🛍️ My Shop</h1>
    <a href='/products'>Products</a>
    <a href='/cart'>Cart</a>
    <a href='/admin'>Admin</a>
    """

# ===== PRODUCTS =====
@app.route('/products')
def products():
    html = style() + "<h2>Products</h2>"

    for p in products_col.find():
        html += f"""
        <div class='card'>
            <h3>{p['name']}</h3>
            <p>💰 {p['price']}৳</p>

            <form action='/add_to_cart' method='POST'>
                <input type='hidden' name='id' value='{p['id']}'>
                <button>Add to Cart</button>
            </form>

            <br>
            <a href='/order/{p['id']}'>Order Now</a>
        </div>
        """

    return html

# ===== ADD TO CART =====
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    pid = request.form['id']

    cart = session.get('cart', [])
    cart.append(pid)
    session['cart'] = cart

    return redirect('/cart')

# ===== CART =====
@app.route('/cart')
def cart():
    html = style() + "<h2>Cart</h2>"
    cart = session.get('cart', [])

    total = 0

    for pid in cart:
        p = products_col.find_one({"id": pid})
        if p:
            price = int(p['price'])
            total += price

            html += f"""
            <div class='card'>
                {p['name']} - {price}৳
                <br>
                <a href='/order/{pid}'>Order This</a>
            </div>
            """

    html += f"<h3>Total: {total}৳</h3>"

    if not cart:
        html += "<p>Cart Empty</p>"

    return html

# ===== ORDER PAGE =====
@app.route('/order/<pid>')
def order(pid):
    p = products_col.find_one({"id": pid})
    if not p:
        return "Not found"

    return style() + f"""
    <h2>Order: {p['name']}</h2>

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

    orders_col.insert_one({
        "product": p['name'],
        "name": request.form['name'],
        "phone": request.form['phone'],
        "address": request.form['address']
    })

    return style() + "<h2 style='color:green'>Order Successful</h2>"

# ===== ADMIN LOGIN =====
@app.route('/admin')
def admin():
    return style() + """
    <h2>Admin Login</h2>
    <form action='/dashboard' method='POST'>
        <input name='pass' placeholder='Password'><br>
        <button>Login</button>
    </form>
    """

# ===== DASHBOARD =====
@app.route('/dashboard', methods=['POST'])
def dashboard():
    if request.form['pass'] != ADMIN_PASS:
        return "Wrong password"

    html = style() + """
    <h2>Admin Panel</h2>

    <h3>Add Product</h3>
    <form action='/add_product' method='POST'>
        <input name='name' placeholder='Product Name'><br>
        <input name='price' placeholder='Price'><br>
        <button>Add</button>
    </form>

    <h3>Orders</h3>
    """

    for o in orders_col.find():
        html += f"""
        <div class='card'>
            Product: {o['product']}<br>
            Name: {o['name']}<br>
            Phone: {o['phone']}<br>
            Address: {o['address']}
        </div>
        """

    return html

# ===== ADD PRODUCT =====
@app.route('/add_product', methods=['POST'])
def add_product():
    products_col.insert_one({
        "id": str(uuid.uuid4()),
        "name": request.form['name'],
        "price": request.form['price']
    })

    return redirect('/products')

# ===== RUN =====
if __name__ == "__main__":
    app.run(debug=True)