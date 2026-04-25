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

# ================= MONGO DB =================
client = MongoClient("mongodb+srv://tahmid16122009_db_user:xha1hQWvPVgPfNAc@cluster0.uxtdbbt.mongodb.net/?appName=Cluster0")

db = client["shop"]
products_col = db["products"]
orders_col = db["orders"]

ADMIN_PASSWORD = "xha1hQWvPVgPfNAc"

# ================= HOME =================
@app.route('/')
def home():
    return """
    <h1 style='text-align:center;'>🛍️ Shoes Shop Pro</h1>
    <div style='text-align:center;'>
        <a href='/products'>Products</a> |
        <a href='/admin'>Admin Panel</a>
    </div>
    """

# ================= PRODUCTS =================
@app.route('/products')
def products():

    items = list(products_col.find())

    html = "<h2 style='text-align:center;'>🔥 Products</h2><div style='display:flex;flex-wrap:wrap;justify-content:center;'>"

    for i, p in enumerate(items):
        html += f"""
        <div style='border:1px solid #ccc;margin:10px;padding:10px;width:200px;text-align:center;'>
            <img src="{p['media']}" width="150"><br>
            <h3>{p['name']}</h3>
            <p>৳ {p['price']}</p>
            <p>{p['color']} | {p['size']}</p>
            <a href='/buy/{p['id']}'>Order</a>
            <br><br>
            <a href='/delete/{p['id']}' style='color:red;'>Delete</a>
        </div>
        """

    return html + "</div>"

# ================= BUY =================
@app.route('/buy/<id>')
def buy(id):

    return f"""
    <h2 style='text-align:center;'>Place Order</h2>

    <form action='/order/{id}' method='POST' style='text-align:center;'>
        <input name='name' placeholder='Name'><br><br>
        <input name='phone' placeholder='Phone'><br><br>
        <input name='address' placeholder='Address'><br><br>
        <button>Order</button>
    </form>
    """

# ================= ORDER =================
@app.route('/order/<id>', methods=['POST'])
def order(id):

    product = products_col.find_one({"id": id})

    orders_col.insert_one({
        "product": product,
        "customer": request.form['name'],
        "phone": request.form['phone'],
        "address": request.form['address']
    })

    return "<h2 style='text-align:center;color:green;'>Order Placed ✅</h2>"

# ================= ADMIN =================
@app.route('/admin')
def admin():
    return """
    <h2 style='text-align:center;'>Admin Login</h2>

    <form action='/dashboard' method='POST' style='text-align:center;'>
        <input type='password' name='pass'><br><br>
        <button>Login</button>
    </form>
    """

# ================= DASHBOARD =================
@app.route('/dashboard', methods=['POST'])
def dashboard():

    if request.form['pass'] != ADMIN_PASSWORD:
        return "Wrong Password"

    session['admin'] = True

    orders = list(orders_col.find())

    return """
    <h2 style='text-align:center;'>📦 Admin Panel</h2>

    <form action='/add' method='POST' enctype='multipart/form-data' style='text-align:center;'>
        <input name='name' placeholder='Name'><br><br>
        <input name='price' placeholder='Price'><br><br>
        <input type='file' name='media'><br><br>
        <input name='color' placeholder='Color'><br><br>
        <input name='size' placeholder='Size'><br><br>
        <button>Add Product</button>
    </form>

    <hr>

    <h3>Orders</h3>
    """ + str(orders)

# ================= ADD PRODUCT =================
@app.route('/add', methods=['POST'])
def add():

    if not session.get('admin'):
        return "Not allowed"

    file = request.files['media']

    upload = cloudinary.uploader.upload(file, resource_type="auto")

    products_col.insert_one({
        "id": str(uuid.uuid4()),
        "name": request.form['name'],
        "price": request.form['price'],
        "media": upload['secure_url'],
        "color": request.form['color'],
        "size": request.form['size']
    })

    return redirect('/products')

# ================= DELETE =================
@app.route('/delete/<id>')
def delete(id):

    if not session.get('admin'):
        return "Not allowed"

    products_col.delete_one({"id": id})

    return redirect('/products')

# ================= RUN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)