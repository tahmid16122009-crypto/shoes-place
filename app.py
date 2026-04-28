from flask import Flask, request, redirect, session
from pymongo import MongoClient
import cloudinary
import cloudinary.uploader
import uuid

app = Flask(__name__)
app.secret_key = "secret123"

# ===== CLOUDINARY =====
cloudinary.config(
    cloud_name="dpfswecue",
    api_key="814473384843783",
    api_secret="BFp92tezRMgWq5tkb3inueu49FI"
)

# ===== MONGODB =====
try:
    client = MongoClient("mongodb+srv://tahmid16122009_db_user:xha1hQWvPVgPfNAc@cluster0.uxtdbbt.mongodb.net/?retryWrites=true&w=majority")
    db = client["shop"]
    products_col = db["products"]
    orders_col = db["orders"]
except:
    products_col = None
    orders_col = None

ADMIN_PASSWORD = "Tahmid1122"

# ===== HOME =====
@app.route('/')
def home():
    return """
    <h1 style='text-align:center'>🛍️ Shoes Shop</h1>
    <div style='text-align:center'>
        <a href='/products'>Products</a> |
        <a href='/cart'>Cart</a> |
        <a href='/admin'>Admin</a>
    </div>
    """

# ===== PRODUCTS =====
@app.route('/products')
def products():
    html = "<h2 style='text-align:center'>Products</h2>"
    html += "<div style='text-align:center'><form><input name='q' placeholder='Search'><button>Search</button></form></div><br>"

    q = request.args.get('q', "")

    if products_col:
        items = products_col.find()
    else:
        items = []

    for p in items:
        if q.lower() not in p.get("name","").lower():
            continue

        html += f"""
        <div style='border:1px solid #ccc;margin:10px;padding:10px;text-align:center'>
            <img src="{p.get('media')}" width="150"><br>
            <b>{p.get('name')}</b><br>
            {p.get('description','')}<br>
            💰 {p.get('price')}৳<br><br>

            <a href='/product/{p.get("id")}'>View</a>
        </div>
        """

    return html

# ===== SINGLE PRODUCT =====
@app.route('/product/<pid>')
def product(pid):
    if not products_col:
        return "DB Error"

    p = products_col.find_one({"id": pid})
    if not p:
        return "Not found"

    return f"""
    <div style='text-align:center'>
        <img src="{p.get('media')}" width="200"><br>
        <h2>{p.get('name')}</h2>
        <p>{p.get('description')}</p>
        <p>💰 {p.get('price')}৳</p>

        <form action='/add_to_cart' method='POST'>
            <input type='hidden' name='id' value='{p.get("id")}'>
            <input type='number' name='qty' value='1' min='1'>
            <button>Add to Cart</button>
        </form>

        <br><a href='/buy/{p.get("id")}'>Order Now</a>
    </div>
    """

# ===== ADD TO CART =====
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    pid = request.form.get("id")
    qty = int(request.form.get("qty",1))

    cart = session.get('cart', [])

    if not isinstance(cart, list):
        cart = []

    cart.append({"id": pid, "qty": qty})
    session['cart'] = cart

    return redirect('/cart')

# ===== CART =====
@app.route('/cart')
def cart():
    cart = session.get('cart', [])

    html = "<h2 style='text-align:center'>Cart</h2>"
    total = 0

    for item in cart:
        p = products_col.find_one({"id": item.get("id")}) if products_col else None
        if not p:
            continue

        price = int(p.get("price",0))
        qty = item.get("qty",1)

        total += price * qty

        html += f"""
        <div style='text-align:center'>
            {p.get('name')} x {qty} = {price*qty}৳
        </div><hr>
        """

    html += f"<h3 style='text-align:center'>Total: {total}৳</h3>"
    html += "<div style='text-align:center'><a href='/checkout'>Checkout</a></div>"

    return html

# ===== CHECKOUT =====
@app.route('/checkout')
def checkout():
    return """
    <h2 style='text-align:center'>Checkout</h2>
    <form action='/place_order' method='POST' style='text-align:center'>
        <input name='name' placeholder='Name'><br><br>
        <input name='phone' placeholder='Phone'><br><br>
        <input name='address' placeholder='Address'><br><br>
        <button>Place Order</button>
    </form>
    """

# ===== PLACE ORDER =====
@app.route('/place_order', methods=['POST'])
def place_order():
    cart = session.get('cart', [])

    if orders_col:
        orders_col.insert_one({
            "customer": request.form.to_dict(),
            "cart": cart
        })

    session['cart'] = []

    return "<h2 style='text-align:center;color:green'>Order Placed</h2>"

# ===== ADMIN =====
@app.route('/admin')
def admin():
    return """
    <form action='/dashboard' method='POST'>
        <input name='pass' placeholder='Password'>
        <button>Login</button>
    </form>
    """

# ===== DASHBOARD =====
@app.route('/dashboard', methods=['POST'])
def dashboard():
    if request.form.get('pass') != ADMIN_PASSWORD:
        return "Wrong password"

    return """
    <h2>Admin Panel</h2>
    <form action='/add_product' method='POST' enctype='multipart/form-data'>
        <input name='name' placeholder='Name'><br>
        <input name='price' placeholder='Price'><br>
        <input name='description' placeholder='Description'><br>
        <input type='file' name='media'><br>
        <button>Add</button>
    </form>
    """

# ===== ADD PRODUCT =====
@app.route('/add_product', methods=['POST'])
def add_product():
    file = request.files.get('media')

    upload = cloudinary.uploader.upload(file, resource_type="auto") if file else {}

    products_col.insert_one({
        "id": str(uuid.uuid4()),
        "name": request.form.get("name"),
        "price": request.form.get("price"),
        "description": request.form.get("description"),
        "media": upload.get("secure_url","")
    })

    return redirect('/products')

# ===== RUN =====
if __name__ == "__main__":
    app.run(debug=True)