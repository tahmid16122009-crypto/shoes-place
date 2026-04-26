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
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    </head>
    <body style='text-align:center;font-family:Arial;background:#f5f5f5'>
    <h1>🛍️ Pro Shop</h1>
    <a href='/products'>Products</a> | 
    <a href='/cart'>Cart</a> | 
    <a href='/admin'>Admin</a>
    </body>
    </html>
    """

# ================= PRODUCTS =================
@app.route('/products')
def products():
    items = list(products_col.find())

    html = "<h2 style='text-align:center;'>Products</h2><div style='display:flex;flex-wrap:wrap;justify-content:center;'>"

    for p in items:
        html += f"""
        <div style='width:200px;background:white;margin:10px;padding:10px;border-radius:10px;text-align:center'>
            <img src="{p['images'][0]}" width="150"><br>
            <h4>{p['name']}</h4>
            <p>৳ {p['price']}</p>
            <a href='/product/{p["id"]}'>View</a>
        </div>
        """

    return html + "</div>"

# ================= PRODUCT DETAIL =================
@app.route('/product/<id>')
def product(id):
    p = products_col.find_one({"id": id})

    images_html = "".join([f"<img src='{img}' width='80'>" for img in p.get("images", [])])

    return f"""
    <div style='text-align:center'>
        <h2>{p['name']}</h2>
        <img src="{p['images'][0]}" width="250"><br>
        {images_html}
        <p>{p.get('description','')}</p>
        <p>৳ {p['price']}</p>

        <form action='/add_cart/{id}' method='post'>
        Quantity: <input type='number' name='qty' value='1'><br><br>
        <button>Add to Cart</button>
        </form>

        <br>
        <a href='/order/{id}'>⚡ Order Now</a>
    </div>
    """

# ================= ADD CART =================
@app.route('/add_cart/<id>', methods=['POST'])
def add_cart(id):

    qty = int(request.form.get('qty', 1))

    if 'cart' not in session:
        session['cart'] = []

    session['cart'].append({"id": id, "qty": qty})
    session.modified = True

    return redirect('/cart')

# ================= CART =================
@app.route('/cart')
def cart():

    cart_items = session.get('cart', [])
    html = "<h2 style='text-align:center'>Cart</h2>"

    for item in cart_items:
        p = products_col.find_one({"id": item['id']})
        html += f"""
        <div style='text-align:center'>
        {p['name']} x {item['qty']} = {int(p['price'])*item['qty']}৳
        </div><hr>
        """

    html += "<div style='text-align:center'><a href='/checkout'>Checkout</a></div>"

    return html

# ================= ORDER PAGE =================
@app.route('/order/<id>')
def order(id):
    p = products_col.find_one({"id": id})

    return f"""
    <div style='text-align:center'>
        <img src="{p['images'][0]}" width="150"><br>
        <h3>{p['name']}</h3>

        <form action='/place_single/{id}' method='POST'>
        <input name='name' placeholder='Name'><br><br>
        <input name='phone' placeholder='Phone'><br><br>
        <input name='address' placeholder='Address'><br><br>
        Quantity: <input name='qty' type='number' value='1'><br><br>
        <button>Place Order</button>
        </form>
    </div>
    """

@app.route('/place_single/<id>', methods=['POST'])
def place_single(id):
    orders_col.insert_one({
        "product_id": id,
        "qty": request.form.get('qty'),
        "name": request.form.get('name')
    })
    return "Order Done"

# ================= CHECKOUT =================
@app.route('/checkout')
def checkout():
    return """
    <form action='/place_order' method='POST'>
    Name <input name='name'><br>
    Phone <input name='phone'><br>
    Address <input name='address'><br>
    <button>Order All</button>
    </form>
    """

@app.route('/place_order', methods=['POST'])
def place_order():
    orders_col.insert_one({
        "cart": session.get('cart', []),
        "name": request.form.get('name')
    })
    session['cart'] = []
    return "Order Success"

# ================= ADMIN =================
@app.route('/admin')
def admin():
    return """
    <form action='/dashboard' method='POST'>
    <input type='password' name='pass'>
    <button>Login</button>
    </form>
    """

@app.route('/dashboard', methods=['POST'])
def dashboard():

    if request.form.get('pass') != ADMIN_PASSWORD:
        return "Wrong Password"

    return """
    <h2>Add Product</h2>
    <form action='/add' method='POST' enctype='multipart/form-data'>
    Name <input name='name'><br>
    Price <input name='price'><br>
    Description <input name='description'><br>
    Colors <input name='colors'><br>
    Sizes <input name='sizes'><br>
    Images (max 5) <input type='file' name='images' multiple><br>
    Videos (max 3) <input type='file' name='videos' multiple><br>
    <button>Add</button>
    </form>
    """

# ================= ADD PRODUCT =================
@app.route('/add', methods=['POST'])
def add():

    images = request.files.getlist("images")
    videos = request.files.getlist("videos")

    img_urls = []
    vid_urls = []

    for img in images[:5]:
        upload = cloudinary.uploader.upload(img)
        img_urls.append(upload['secure_url'])

    for vid in videos[:3]:
        upload = cloudinary.uploader.upload(vid, resource_type="video")
        vid_urls.append(upload['secure_url'])

    products_col.insert_one({
        "id": str(uuid.uuid4()),
        "name": request.form.get('name'),
        "price": request.form.get('price'),
        "description": request.form.get('description'),
        "colors": request.form.get('colors'),
        "sizes": request.form.get('sizes'),
        "images": img_urls,
        "videos": vid_urls
    })

    return redirect('/products')

# ================= RUN =================
if __name__ == "__main__":
    app.run()