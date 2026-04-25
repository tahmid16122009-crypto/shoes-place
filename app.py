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

cart = []

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

# ================= PRODUCTS + SEARCH =================
@app.route('/products')
def products():

    q = request.args.get('q','')
    items = list(products_col.find())

    if q:
        items = [p for p in items if q.lower() in p.get('name','').lower()]

    html = """
    <form style='text-align:center;' method='get'>
        <input name='q' placeholder='Search product'>
        <button>Search</button>
    </form>

    <div style='display:flex;flex-wrap:wrap;justify-content:center;'>
    """

    for p in items:
        html += f"""
        <div style='border:1px solid #ccc;margin:10px;padding:10px;width:180px;text-align:center;'>
            <img src="{p.get('media','')}" width="150"><br>
            <h4>{p.get('name','')}</h4>
            <p>৳ {p.get('price','')}</p>

            <a href='/add_cart/{p.get('id','')}'>Add Cart</a><br>
            <a href='/product/{p.get('id','')}'>View</a>
        </div>
        """

    return html + "</div>"

# ================= PRODUCT =================
@app.route('/product/<id>')
def product(id):
    p = products_col.find_one({"id": id})
    return f"""
    <div style='text-align:center;'>
        <h2>{p['name']}</h2>
        <img src="{p['media']}" width="250"><br>
        <p>৳ {p['price']}</p>
        <a href='/add_cart/{p['id']}'>Add to Cart</a>
    </div>
    """

# ================= CART =================
@app.route('/add_cart/<id>')
def add_cart(id):
    p = products_col.find_one({"id": id})
    cart.append(p)
    return redirect('/cart')

@app.route('/cart')
def cart_page():

    total = sum(int(p.get('price',0)) for p in cart)

    html = "<h2 style='text-align:center;'>🛒 CART</h2>"

    for p in cart:
        html += f"""
        <div style='text-align:center;'>
            {p.get('name','')} - {p.get('price','')}৳
        </div>
        <hr>
        """

    html += f"<h3 style='text-align:center;'>Total: {total}৳</h3>"

    return html

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

@app.route('/dashboard', methods=['POST'])
def dashboard():

    if request.form.get('pass') != ADMIN_PASSWORD:
        return "Wrong Password"

    items = products_col.count_documents({})
    orders = orders_col.count_documents({})

    return f"""
    <h2>📊 Dashboard</h2>
    <p>Products: {items}</p>
    <p>Orders: {orders}</p>

    <form action='/add' method='POST' enctype='multipart/form-data'>
        <input name='name'><br>
        <input name='price'><br>
        <input type='file' name='media'><br>
        <button>Add</button>
    </form>
    """

# ================= ADD =================
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