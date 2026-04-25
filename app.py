from flask import Flask, request, redirect, session, render_template_string
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "secret123"

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# DATABASE (temporary)
products = []
orders = []

ADMIN_PASSWORD = "admin123"

# ================= HOME =================
@app.route('/')
def home():
    return """
    <h1 style='text-align:center;'>👟 Shoes Shop</h1>
    <div style='text-align:center;'>
        <a href='/products'>Products</a> |
        <a href='/admin_login'>Admin</a>
    </div>
    """

# ================= PRODUCTS =================
@app.route('/products')
def show_products():

    html = "<h2 style='text-align:center;'>Products</h2>"

    for i, p in enumerate(products):
        html += f"""
        <div style='text-align:center;border:1px solid #ccc;margin:10px;padding:10px'>
            <img src='/{p['img']}' width='150'><br>
            <b>{p['name']}</b><br>
            {p['price']}৳<br>
            <a href='/buy/{i}'>Order Now</a>
        </div>
        """

    return html + "<br><center><a href='/'>Home</a></center>"

# ================= ORDER PAGE =================
@app.route('/buy/<int:id>')
def buy(id):

    p = products[id]

    return f"""
    <h2 style='text-align:center;'>Order {p['name']}</h2>

    <form action='/place_order/{id}' method='POST' style='text-align:center;'>

        <input name='name' placeholder='Name' required><br><br>
        <input name='phone' placeholder='Phone' required><br><br>
        <input name='address' placeholder='Address' required><br><br>

        <button>Place Order</button>
    </form>
    """

# ================= PLACE ORDER =================
@app.route('/place_order/<int:id>', methods=['POST'])
def place_order(id):

    p = products[id]

    orders.append({
        "product": p['name'],
        "price": p['price'],
        "name": request.form['name'],
        "phone": request.form['phone'],
        "address": request.form['address']
    })

    return "<h2 style='text-align:center;color:green;'>Order Placed ✅</h2><a href='/products'>Back</a>"

# ================= ADMIN LOGIN =================
@app.route('/admin_login')
def admin_login():
    return """
    <h2 style='text-align:center;'>Admin Login</h2>
    <form action='/admin' method='POST' style='text-align:center;'>
        <input name='password' type='password' placeholder='Password'><br><br>
        <button>Login</button>
    </form>
    """

# ================= ADMIN PANEL =================
@app.route('/admin', methods=['POST'])
def admin():

    if request.form['password'] != ADMIN_PASSWORD:
        return "Wrong Password"

    session['admin'] = True

    return redirect('/dashboard')

# ================= DASHBOARD =================
@app.route('/dashboard')
def dashboard():

    if not session.get('admin'):
        return "Access Denied"

    html = """
    <h2 style='text-align:center;'>📦 Admin Dashboard</h2>

    <h3 style='text-align:center;'>➕ Add Product</h3>

    <form action='/add_product' method='POST' enctype='multipart/form-data' style='text-align:center;'>
        <input name='name' placeholder='Product Name'><br><br>
        <input name='price' placeholder='Price'><br><br>
        <input type='file' name='image'><br><br>
        <button>Add Product</button>
    </form>

    <hr>
    <h3 style='text-align:center;'>🧾 Orders</h3>
    """

    for o in orders:
        html += f"""
        <div style='border:1px solid black;margin:10px;padding:10px'>
            <b>{o['product']}</b><br>
            {o['name']} | {o['phone']}<br>
            {o['address']}<br>
            {o['price']}৳
        </div>
        """

    return html

# ================= ADD PRODUCT =================
@app.route('/add_product', methods=['POST'])
def add_product():

    if not session.get('admin'):
        return "Not allowed"

    name = request.form['name']
    price = request.form['price']

    image = request.files['image']
    filename = secure_filename(image.filename)

    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image.save(path)

    products.append({
        "name": name,
        "price": price,
        "img": path
    })

    return redirect('/dashboard')

# ================= RUN =================
app.run(host='0.0.0.0', port=5000)