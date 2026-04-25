from flask import Flask, request, redirect, session

app = Flask(__name__)
app.secret_key = "secret123"

# ======================
# DATABASE (IN MEMORY)
# ======================
products = []
orders = []

ADMIN_PASSWORD = "admin123"

# ======================
# HOME
# ======================
@app.route('/')
def home():
    return """
    <h1 style='text-align:center;'>👟 My E-Commerce Shop</h1>

    <div style='text-align:center;'>
        <a href='/products'>Products</a> |
        <a href='/admin_login'>Admin</a>
    </div>
    """

# ======================
# VIEW PRODUCTS
# ======================
@app.route('/products')
def show_products():

    html = "<h2 style='text-align:center;'>🛒 Products</h2>"

    for i, p in enumerate(products):
        html += f"""
        <div style='border:1px solid #ccc;margin:10px;padding:10px;text-align:center;'>
            <img src="{p['img']}" width="150"><br>
            <b>{p['name']}</b><br>
            {p['price']}৳<br>
            <a href='/buy/{i}'>Order Now</a>
        </div>
        """

    return html + "<br><center><a href='/'>Home</a></center>"

# ======================
# BUY PAGE
# ======================
@app.route('/buy/<int:id>')
def buy(id):

    p = products[id]

    return f"""
    <h2 style='text-align:center;'>Order: {p['name']}</h2>

    <form action='/place_order/{id}' method='POST' style='text-align:center;'>

        <input name='name' placeholder='Name' required><br><br>
        <input name='phone' placeholder='Phone' required><br><br>
        <input name='address' placeholder='Address' required><br><br>

        <button>Place Order</button>
    </form>
    """

# ======================
# PLACE ORDER
# ======================
@app.route('/place_order/<int:id>', methods=['POST'])
def place_order(id):

    p = products[id]

    order = {
        "product": p['name'],
        "price": p['price'],
        "name": request.form['name'],
        "phone": request.form['phone'],
        "address": request.form['address'],
        "status": "Paid (Demo)"
    }

    orders.append(order)

    return """
    <h2 style='text-align:center;color:green;'>Order Placed ✅</h2>
    <a href='/products'>Back</a>
    """

# ======================
# ADMIN LOGIN
# ======================
@app.route('/admin_login')
def admin_login():
    return """
    <h2 style='text-align:center;'>Admin Login</h2>

    <form action='/admin' method='POST' style='text-align:center;'>
        <input name='password' placeholder='Password'><br><br>
        <button>Login</button>
    </form>
    """

# ======================
# ADMIN PANEL
# ======================
@app.route('/admin', methods=['POST'])
def admin():

    if request.form['password'] != ADMIN_PASSWORD:
        return "Wrong password"

    session['admin'] = True

    return redirect('/dashboard')


@app.route('/dashboard')
def dashboard():

    if not session.get('admin'):
        return "Access Denied"

    html = "<h2 style='text-align:center;'>📦 ADMIN DASHBOARD</h2>"

    # ADD PRODUCT FORM
    html += """
    <h3 style='text-align:center;'>➕ Add Product</h3>

    <form action='/add_product' method='POST' style='text-align:center;'>

        <input name='name' placeholder='Product Name'><br><br>
        <input name='price' placeholder='Price'><br><br>
        <input name='img' placeholder='Image URL'><br><br>

        <button>Add Product</button>
    </form>

    <hr>
    <h3 style='text-align:center;'>📦 Orders</h3>
    """

    for o in orders:
        html += f"""
        <div style='border:1px solid black;margin:10px;padding:10px'>
            <b>{o['product']}</b><br>
            {o['name']} | {o['phone']}<br>
            {o['address']}<br>
            {o['status']}
        </div>
        """

    return html

# ======================
# ADD PRODUCT (ADMIN ONLY)
# ======================
@app.route('/add_product', methods=['POST'])
def add_product():

    if not session.get('admin'):
        return "Not allowed"

    products.append({
        "name": request.form['name'],
        "price": request.form['price'],
        "img": request.form['img']
    })

    return redirect('/dashboard')

# ======================
# RUN APP
# ======================
app.run(host='0.0.0.0', port=5000)