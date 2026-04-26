from flask import Flask, request, redirect, session
from pymongo import MongoClient
import cloudinary
import cloudinary.uploader
import uuid

app = Flask(__name__)
app.secret_key = "secret123"

# ================= CLOUDINARY =================
cloudinary.config(
    cloud_name="dpfswecue",
    api_key="814473384843783",
    api_secret="BFp92tezRMgWq5tkb3inueu49FI"
)

# ================= MONGO =================
client = MongoClient("mongodb+srv://tahmid16122009_db_user:xha1hQWvPVgPfNAc@cluster0.uxtdbbt.mongodb.net/?retryWrites=true&w=majority")
db = client["shop"]
products_col = db["products"]
orders_col = db["orders"]

ADMIN_PASSWORD = "Tahmid1122"

# ================= HOME =================
@app.route('/')
def home():
    return """
    <h1 style='text-align:center;'>🛍️ PRO SHOP</h1>
    <div style='text-align:center;'>
        <a href='/products'>Products</a> |
        <a href='/cart'>Cart</a> |
        <a href='/admin'>Admin</a>
    </div>
    """

# ================= PRODUCTS =================
@app.route('/products')
def products():
    items = list(products_col.find())

    html = "<h2 style='text-align:center;'>Products</h2>"
    html += "<div style='display:flex;flex-wrap:wrap;justify-content:center;'>"

    for p in items:
        html += f"""
        <div style='border:1px solid #ccc;margin:10px;padding:10px;width:180px;text-align:center;'>
            <img src="{p.get('media','')}" width="150"><br>
            <h4>{p.get('name','')}</h4>
            <p>৳ {p.get('price','')}</p>

            <a href='/add_cart/{p.get('id','')}'>🛒 Add to Cart</a><br>
        </div>
        """

    return html + "</div>"

# ================= ADD TO CART =================
@app.route('/add_cart/<id>')
def add_cart(id):
    if 'cart' not in session:
        session['cart'] = []

    session['cart'].append(id)
    session.modified = True

    return redirect('/cart')

# ================= CART =================
@app.route('/cart')
def cart_page():

    cart_ids = session.get('cart', [])
    items = []

    for cid in cart_ids:
        p = products_col.find_one({"id": cid})
        if p:
            items.append(p)

    total = sum(int(p.get('price', 0)) for p in items)

    html = "<h2 style='text-align:center;'>🛒 Cart</h2>"

    for p in items:
        html += f"""
        <div style='text-align:center;'>
            {p.get('name','')} - {p.get('price','')}৳
        </div>
        <hr>
        """

    html += f"<h3 style='text-align:center;'>Total: {total}৳</h3>"

    html += """
    <div style='text-align:center;'>
        <a href='/checkout'>✅ Proceed to Checkout</a>
    </div>
    """

    return html

# ================= CHECKOUT PAGE =================
@app.route('/checkout')
def checkout():
    return """
    <h2 style='text-align:center;'>Checkout</h2>

    <form action='/place_order' method='POST' style='text-align:center;'>
        <input name='name' placeholder='Your Name'><br><br>
        <input name='phone' placeholder='Phone'><br><br>
        <input name='address' placeholder='Address'><br><br>

        <button>Place Order</button>
    </form>
    """

# ================= PLACE ORDER =================
@app.route('/place_order', methods=['POST'])
def place_order():

    cart_ids = session.get('cart', [])
    items = []

    for cid in cart_ids:
        p = products_col.find_one({"id": cid})
        if p:
            items.append(p)

    orders_col.insert_one({
        "id": str(uuid.uuid4()),
        "items": items,
        "name": request.form.get('name'),
        "phone": request.form.get('phone'),
        "address": request.form.get('address')
    })

    # clear cart after order
    session['cart'] = []

    return "<h2 style='color:green;text-align:center;'>🎉 Order Placed Successfully!</h2>"

# ================= ADMIN =================
@app.route('/admin')
def admin():
    return """
    <form action='/dashboard' method='POST' style='text-align:center;'>
        <h2>Admin Login</h2>
        <input type='password' name='pass'>
        <button>Login</button>
    </form>
    """

# ================= DASHBOARD =================
@app.route('/dashboard', methods=['POST'])
def dashboard():

    if request.form.get('pass') != ADMIN_PASSWORD:
        return "Wrong Password"

    orders = list(orders_col.find())

    html = "<h2>📦 Orders</h2>"

    for o in orders:
        html += f"""
        <div>
            <b>{o.get('name')}</b> ({o.get('phone')})<br>
            Address: {o.get('address')}<br>
            Items: {len(o.get('items', []))}
        </div>
        <hr>
        """

    html += """
    <form action='/add' method='POST' enctype='multipart/form-data'>
        <input name='name'><br>
        <input name='price'><br>
        <input type='file' name='media'><br>
        <button>Add Product</button>
    </form>
    """

    return html

# ================= ADD PRODUCT =================
@app.route('/add', methods=['POST'])
def add():

    file = request.files.get('media')
    upload = cloudinary.uploader.upload(file, resource_type="auto")

    products_col.insert_one({
        "id": str(uuid.uuid4()),
        "name": request.form.get('name'),
        "price": request.form.get('price'),
        "media": upload.get('secure_url')
    })

    return redirect('/products')

# ================= RUN =================
if __name__ == "__main__":
    app.run()