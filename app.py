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
    <body style='font-family:Arial;text-align:center;background:#f5f5f5;'>
        <h1>🛍️ Shoes Shop Pro</h1>
        <a href='/products'>Products</a> |
        <a href='/admin'>Admin</a>
    </body>
    </html>
    """

# ================= PRODUCTS (MODERN UI) =================
@app.route('/products')
def products():
    items = list(products_col.find())

    html = """
    <html>
    <head>
    <style>
    body{font-family:Arial;background:#f5f5f5;margin:0}
    .header{background:white;padding:15px;font-size:22px;font-weight:bold;text-align:center}
    .grid{display:flex;flex-wrap:wrap;justify-content:center;padding:10px}
    .card{width:180px;background:white;margin:10px;padding:10px;border-radius:12px;
    box-shadow:0 4px 10px rgba(0,0,0,0.1);text-align:center;transition:0.3s}
    .card:hover{transform:scale(1.05)}
    img{width:100%;border-radius:10px}
    .btn{display:block;margin-top:5px;padding:6px;text-decoration:none;
    background:#ff4d4d;color:white;border-radius:6px}
    .btn2{background:#333}
    </style>
    </head>
    <body>

    <div class='header'>🛍️ Shoes Shop Pro</div>
    <div class='grid'>
    """

    for p in items:
        html += f"""
        <div class='card'>
            <img src="{p.get('media','')}">
            <h4>{p.get('name','')}</h4>
            <p>৳ {p.get('price','')}</p>

            <a class='btn' href='/product/{p.get('id','')}'>View</a>
            <a class='btn btn2' href='/buy/{p.get('id','')}'>Buy</a>
        </div>
        """

    html += "</div></body></html>"
    return html

# ================= PRODUCT DETAILS =================
@app.route('/product/<id>')
def product_detail(id):
    p = products_col.find_one({"id": id})

    if not p:
        return "Not found"

    return f"""
    <div style='text-align:center;font-family:Arial;'>
        <h2>{p['name']}</h2>
        <img src="{p['media']}" width="250"><br>
        <h3>৳ {p['price']}</h3>
        <p>{p.get('color','')} | {p.get('size','')}</p>
        <a href='/buy/{p['id']}'>🛒 Order Now</a>
    </div>
    """

# ================= BUY =================
@app.route('/buy/<id>')
def buy(id):
    return f"""
    <form action='/order/{id}' method='POST' style='text-align:center;'>
        <h2>Order</h2>
        <input name='name' placeholder='Name'><br><br>
        <input name='phone' placeholder='Phone'><br><br>
        <input name='address' placeholder='Address'><br><br>
        <button>Place Order</button>
    </form>
    """

# ================= ORDER =================
@app.route('/order/<id>', methods=['POST'])
def order(id):
    product = products_col.find_one({"id": id})

    orders_col.insert_one({
        "product": product,
        "name": request.form.get('name'),
        "phone": request.form.get('phone'),
        "address": request.form.get('address')
    })

    return "<h2 style='color:green;text-align:center;'>Order Placed ✅</h2>"

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

    session['admin'] = True

    return """
    <h2 style='text-align:center;'>📦 Admin Panel</h2>

    <form action='/add' method='POST' enctype='multipart/form-data' style='text-align:center;'>
        <input name='name'><br><br>
        <input name='price'><br><br>
        <input name='color'><br><br>
        <input name='size'><br><br>
        <input type='file' name='media'><br><br>
        <button>Add Product</button>
    </form>
    """

# ================= ADD PRODUCT =================
@app.route('/add', methods=['POST'])
def add():

    file = request.files.get('media')

    upload = cloudinary.uploader.upload(file, resource_type="auto")

    products_col.insert_one({
        "id": str(uuid.uuid4()),
        "name": request.form.get('name'),
        "price": request.form.get('price'),
        "color": request.form.get('color'),
        "size": request.form.get('size'),
        "media": upload.get('secure_url')
    })

    return redirect('/products')

# ================= RUN =================
if __name__ == "__main__":
    app.run()