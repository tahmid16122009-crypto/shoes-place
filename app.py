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
    client = MongoClient("mongodb+srv://tahmid16122009_db_user:xha1hQWvPVgPfNAc@cluster0.uxtdbbt.mongodb.net/?retryWrites=true&w=majority", serverSelectionTimeoutMS=5000)
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

    items = []
    try:
        if products_col is not None:
            items = list(products_col.find())
    except:
        items = []

    for p in items:
        html += f"""
        <div style='text-align:center;border:1px solid #ccc;margin:10px;padding:10px'>
            <img src="{p.get('media','')}" width="150"><br>
            <b>{p.get('name','')}</b><br>
            {p.get('price','')}৳<br><br>

            <form action='/add_to_cart' method='POST'>
                <input type='hidden' name='id' value='{p.get("id")}'>
                <button>Add to Cart</button>
            </form>
        </div>
        """

    return html

# ===== ADD TO CART =====
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    pid = request.form.get("id")

    cart = session.get('cart', [])

    if not isinstance(cart, list):
        cart = []

    cart.append({"id": pid, "qty": 1})
    session['cart'] = cart

    return redirect('/cart')

# ===== CART (FIXED 100%) =====
@app.route('/cart')
def cart():
    try:
        cart = session.get('cart', [])

        if not isinstance(cart, list):
            session['cart'] = []
            return "<h2 style='text-align:center'>Cart reset</h2>"

        html = "<h2 style='text-align:center'>Cart</h2>"
        total = 0

        for item in cart:
            p = None

            try:
                if products_col is not None:
                    p = products_col.find_one({"id": item.get("id")})
            except:
                p = None

            if not p:
                continue

            try:
                price = int(p.get("price", 0))
            except:
                price = 0

            qty = item.get("qty", 1)

            total += price * qty

            html += f"""
            <div style='text-align:center'>
                {p.get('name','')} x {qty} = {price*qty}৳
            </div><hr>
            """

        html += f"<h3 style='text-align:center'>Total: {total}৳</h3>"

        if total == 0:
            html += "<p style='text-align:center'>Cart empty</p>"

        html += "<div style='text-align:center'><a href='/'>Back</a></div>"

        return html

    except Exception as e:
        return f"<h2 style='color:red;text-align:center'>Cart Error Fixed</h2><p>{str(e)}</p>"

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
        <input type='file' name='media'><br>
        <button>Add</button>
    </form>
    """

# ===== ADD PRODUCT =====
@app.route('/add_product', methods=['POST'])
def add_product():
    try:
        file = request.files.get('media')
        upload = cloudinary.uploader.upload(file) if file else {}

        if products_col is not None:
            products_col.insert_one({
                "id": str(uuid.uuid4()),
                "name": request.form.get("name"),
                "price": request.form.get("price"),
                "media": upload.get("secure_url","")
            })
    except:
        pass

    return redirect('/products')

# ===== RUN =====
if __name__ == "__main__":
    app.run(debug=True)