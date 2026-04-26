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

# ================= SAFE IMAGE =================
def get_image(p):
    if not p:
        return "https://via.placeholder.com/150"

    if "media" in p:
        return p["media"]

    if "images" in p and isinstance(p["images"], list) and len(p["images"]) > 0:
        return p["images"][0]

    return "https://via.placeholder.com/150"

# ================= HOME =================
@app.route('/')
def home():
    return """
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <h1 style='text-align:center;'>🛍️ Shoes Shop Pro</h1>

    <div style='text-align:center;'>
        <a href='/products'>Products</a> |
        <a href='/cart'>Cart</a> |
        <a href='/admin'>Admin</a>
    </div>
    """

# ================= PRODUCTS + SEARCH =================
@app.route('/products')
def products():
    search = request.args.get('q', '')

    if search:
        items = list(products_col.find({"name": {"$regex": search, "$options": "i"}}))
    else:
        items = list(products_col.find())

    html = """
    <form style='text-align:center;' method='GET'>
        <input name='q' placeholder='Search product...'>
        <button>Search</button>
    </form>
    <hr>
    """

    html += "<div style='display:flex;flex-wrap:wrap;justify-content:center;'>"

    for p in items:
        img = get_image(p)

        html += f"""
        <div style='width:200px;margin:10px;padding:10px;background:#fff;border-radius:10px;text-align:center;box-shadow:0 0 10px #ddd'>
            <img src="{img}" width="150"><br>
            <h4>{p.get('name','No Name')}</h4>
            <p>৳ {p.get('price','0')}</p>

            <a href='/product/{p.get('id','')}'>View</a><br><br>
            <a href='/add_cart/{p.get('id','')}'>🛒 Add Cart</a>
        </div>
        """

    return html + "</div>"

# ================= PRODUCT DETAIL =================
@app.route('/product/<id>')
def product(id):

    p = products_col.find_one({"id": id})
    if not p:
        return "Product not found"

    img = get_image(p)

    return f"""
    <div style='text-align:center'>
        <img src="{img}" width="250"><br>
        <h2>{p.get('name')}</h2>
        <p>{p.get('description','')}</p>
        <p>৳ {p.get('price')}</p>

        <form action='/add_cart/{id}' method='POST'>
            Quantity: <input type='number' name='qty' value='1'><br><br>
            <button>Add to Cart</button>
        </form>

        <br>
        <a href='/order/{id}'>⚡ Order Now</a>
    </div>
    """

# ================= ADD TO CART (FIXED) =================
@app.route('/add_cart/<id>', methods=['POST'])
def add_cart(id):

    qty = int(request.form.get('qty', 1))

    product = products_col.find_one({"id": id})
    if not product:
        return "Invalid product"

    if 'cart' not in session:
        session['cart'] = []

    session['cart'].append({
        "id": id,
        "qty": qty
    })

    session.modified = True

    return redirect('/cart')

# ================= CART =================
@app.route('/cart')
def cart():

    cart = session.get('cart', [])

    html = "<h2 style='text-align:center'>🛒 Cart</h2>"
    total = 0

    for item in cart:
        p = products_col.find_one({"id": item["id"]})
        if not p:
            continue

        price = int(p.get('price', 0))
        subtotal = price * item.get('qty', 1)
        total += subtotal

        html += f"""
        <div style='text-align:center'>
            {p.get('name')} x {item.get('qty',1)} = {subtotal}৳
        </div><hr>
        """

    html += f"<h3 style='text-align:center'>Total: {total}৳</h3>"
    html += "<div style='text-align:center'><a href='/checkout'>Checkout</a></div>"

    return html

# ================= ORDER =================
@app.route('/order/<id>')
def order(id):

    p = products_col.find_one({"id": id})
    if not p:
        return "Product not found"

    img = get_image(p)

    return f"""
    <div style='text-align:center'>
        <img src="{img}" width="150"><br>
        <h3>{p.get('name')}</h3>

        <form action='/place_order_single/{id}' method='POST'>
        Name <input name='name'><br><br>
        Phone <input name='phone'><br><br>
        Address <input name='address'><br><br>
        Quantity <input name='qty' value='1'><br><br>
        <button>Order</button>
        </form>
    </div>
    """

@app.route('/place_order_single/<id>', methods=['POST'])
def place_single(id):

    orders_col.insert_one({
        "product_id": id,
        "name": request.form.get('name'),
        "phone": request.form.get('phone'),
        "address": request.form.get('address'),
        "qty": request.form.get('qty')
    })

    return "<h2 style='color:green;text-align:center'>Order Placed ✅</h2>"

# ================= CHECKOUT CART =================
@app.route('/checkout')
def checkout():

    return """
    <form action='/place_cart_order' method='POST' style='text-align:center'>
        Name <input name='name'><br><br>
        Phone <input name='phone'><br><br>
        Address <input name='address'><br><br>
        <button>Place Order</button>
    </form>
    """

@app.route('/place_cart_order', methods=['POST'])
def place_cart_order():

    orders_col.insert_one({
        "cart": session.get('cart', []),
        "name": request.form.get('name'),
        "phone": request.form.get('phone'),
        "address": request.form.get('address')
    })

    session['cart'] = []

    return "<h2 style='color:green;text-align:center'>Order Success 🎉</h2>"

# ================= ADMIN =================
@app.route('/admin')
def admin():
    return """
    <form action='/dashboard' method='POST' style='text-align:center'>
        <input type='password' name='pass'>
        <button>Login</button>
    </form>
    """

@app.route('/dashboard', methods=['POST'])
def dashboard():

    if request.form.get('pass') != ADMIN_PASSWORD:
        return "Wrong Password"

    orders = list(orders_col.find())

    html = "<h2>📦 Orders</h2>"

    for o in orders:
        html += f"""
        <div style='border:1px solid #ccc;margin:10px;padding:10px'>
            <b>Name:</b> {o.get('name','')}<br>
            <b>Phone:</b> {o.get('phone','')}<br>
            <b>Address:</b> {o.get('address','')}<br>
            <b>Product:</b> {o.get('product_id','')}<br>
            <b>Cart:</b> {o.get('cart','')}
        </div>
        """

    html += """
    <hr>
    <h3>Add Product</h3>
    <form action='/add' method='POST' enctype='multipart/form-data'>
        Name <input name='name'><br>
        Price <input name='price'><br>
        Description <input name='description'><br>
        Image <input type='file' name='media'><br>
        <button>Add</button>
    </form>
    """

    return html

# ================= ADD PRODUCT =================
@app.route('/add', methods=['POST'])
def add():

    file = request.files.get('media')
    upload = cloudinary.uploader.upload(file)

    products_col.insert_one({
        "id": str(uuid.uuid4()),
        "name": request.form.get('name'),
        "price": request.form.get('price'),
        "description": request.form.get('description'),
        "media": upload['secure_url']
    })

    return redirect('/products')

# ================= RUN =================
if __name__ == "__main__":
    app.run()