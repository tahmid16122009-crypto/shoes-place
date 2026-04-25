from flask import Flask, request, redirect, session
from pymongo import MongoClient
import cloudinary
import cloudinary.uploader
import uuid

app = Flask(__name__)
app.secret_key = "secret123"

# ===== DEBUG MODE ON =====
app.config["PROPAGATE_EXCEPTIONS"] = True

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

ADMIN_PASSWORD = "xha1hQWvPVgPfNAc"

# ================= HOME =================
@app.route('/')
def home():
    return "<h2>Server Running OK</h2><a href='/products'>Products</a>"

# ================= PRODUCTS =================
@app.route('/products')
def products():
    try:
        items = list(products_col.find())
        html = "<h2>Products</h2>"

        for p in items:
            html += f"""
            <div>
                <img src="{p.get('media','')}" width="100"><br>
                {p.get('name','')} - {p.get('price','')}
                <br>
                <a href='/buy/{p.get('id','')}'>Buy</a>
                <hr>
            </div>
            """

        return html

    except Exception as e:
        return f"PRODUCT ERROR: {str(e)}"

# ================= BUY =================
@app.route('/buy/<id>')
def buy(id):
    return f"""
    <form action='/order/{id}' method='POST'>
    <input name='name'>
    <input name='phone'>
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
            "phone": request.form.get('phone')
        })

        return "Order Done"

    except Exception as e:
        return f"ORDER ERROR: {str(e)}"

# ================= ADMIN =================
@app.route('/admin')
def admin():
    return """
    <form action='/dashboard' method='POST'>
    <input type='password' name='pass'>
    <button>Login</button>
    </form>
    """

# ================= DASHBOARD =================
@app.route('/dashboard', methods=['POST'])
def dashboard():
    try:
        if request.form.get('pass') != ADMIN_PASSWORD:
            return "Wrong Password"

        session['admin'] = True

        return """
        <h2>Admin</h2>

        <form action='/add' method='POST' enctype='multipart/form-data'>
        <input name='name'>
        <input name='price'>
        <input type='file' name='media'>
        <button>Add</button>
        </form>
        """

    except Exception as e:
        return f"DASHBOARD ERROR: {str(e)}"

# ================= ADD =================
@app.route('/add', methods=['POST'])
def add():
    try:
        file = request.files.get('media')

        upload = cloudinary.uploader.upload(file, resource_type="auto")

        products_col.insert_one({
            "id": str(uuid.uuid4()),
            "name": request.form.get('name'),
            "price": request.form.get('price'),
            "media": upload.get('secure_url')
        })

        return redirect('/products')

    except Exception as e:
        return f"ADD ERROR: {str(e)}"

# ================= RUN =================
if __name__ == "__main__":
    app.run()