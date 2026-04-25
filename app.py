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

# ================= MONGODB =================
client = MongoClient("mongodb+srv://tahmid16122009_db_user:xha1hQWvPVgPfNAc@cluster0.uxtdbbt.mongodb.net/?retryWrites=true&w=majority")
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
        <a href='/admin'>Admin</a>
    </div>
    """

# ================= PRODUCTS =================
@app.route('/products')
def products():
    try:
        items = list(products_col.find())

        html = "<h2 style='text-align:center;'>🔥 Products</h2>"
        html += "<div style='display:flex;flex-wrap:wrap;justify-content:center;'>"

        for p in items:
            html += f"""
            <div style='border:1px solid #ccc;margin:10px;padding:10px;width:200px;text-align:center;'>
                <img src="{p.get('media','')}" width="150"><br>
                <h3>{p.get('name','')}</h3>
                <p>৳ {p.get('price','')}</p>
                <p>{p.get('color','')} | {p.get('size','')}</p>

                <a href='/buy/{p.get('id','')}'>Order</a><br><br>
                <a href='/delete/{p.get('id','')}' style='color:red;'>Delete</a>
            </div>
            """

        return html + "</div>"

    except Exception as e:
        return f"Error: {str(e)}"

# ================= BUY =================
@app.route('/buy/<id>')
def buy(id):
    return f"""
    <h2 style='text-align:center;'>Order Product</h2>

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
    try:
        product = products_col.find_one({"id": id})

        orders_col.insert_one({
            "product": product,
            "name": request.form.get('name'),
            "phone": request.form.get('phone'),
            "address": request.form.get('address')
        })

        return "<h2 style='color:green;text-align:center;'>Order Placed ✅</h2>"

    except Exception as e:
        return str(e)

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
    if request.form.get('pass') != ADMIN_PASSWORD:
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

# ================= ADD =================
@app.route('/add', methods=['POST'])
def add():
    try:
        if not session.get('admin'):
            return "Not allowed"

        file = request.files.get('media')

        upload = cloudinary.uploader.upload(file, resource_type="auto")

        products_col.insert_one({
            "id": str(uuid.uuid4()),
            "name": request.form.get('name'),
            "price": request.form.get('price'),
            "media": upload.get('secure_url'),
            "color": request.form.get('color'),
            "size": request.form.get('size')
        })

        return redirect('/products')

    except Exception as e:
        return str(e)

# ================= DELETE =================
@app.route('/delete/<id>')
def delete(id):
    try:
        if not session.get('admin'):
            return "Not allowed"

        products_col.delete_one({"id": id})
        return redirect('/products')

    except Exception as e:
        return str(e)

# ================= RUN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)