from flask import Flask, request, redirect, session
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

# ================= DATABASE =================
products = []
orders = []

ADMIN_PASSWORD = "Tahmid2009"

# ================= HOME =================
@app.route('/')
def home():
    return """
    <h1 style='text-align:center;font-family:sans-serif;'>🛍️ Shoes Shop Pro</h1>

    <div style='text-align:center;'>
        <a href='/products'>Products</a> |
        <a href='/admin'>Admin Panel</a>
    </div>
    """

# ================= PRODUCTS =================
@app.route('/products')
def products_page():

    html = """
    <h2 style='text-align:center;'>🔥 Products</h2>
    <div style='display:flex;flex-wrap:wrap;justify-content:center;'>
    """

    for i, p in enumerate(products):
        html += f"""
        <div style='border:1px solid #ddd;border-radius:10px;margin:10px;padding:10px;width:200px;text-align:center;'>
            <img src="{p['media']}" width="150"><br>

            <h3>{p['name']}</h3>
            <p>💰 {p['price']}৳</p>
            <p>🎨 {p['color']} | 📏 {p['size']}</p>

            <a href='/buy/{i}'>Order</a><br><br>

            <a href='/delete/{i}' style='color:red;'>Delete</a>
            <a href='/edit/{i}'>Edit</a>
        </div>
        """

    return html + "</div>"

# ================= BUY =================
@app.route('/buy/<int:id>')
def buy(id):

    p = products[id]

    return f"""
    <h2 style='text-align:center;'>Order {p['name']}</h2>

    <form action='/order/{id}' method='POST' style='text-align:center;'>
        <input name='name' placeholder='Name'><br><br>
        <input name='phone' placeholder='Phone'><br><br>
        <input name='address' placeholder='Address'><br><br>
        <button>Place Order</button>
    </form>
    """

# ================= ORDER =================
@app.route('/order/<int:id>', methods=['POST'])
def order(id):

    p = products[id]

    orders.append({
        "product": p['name'],
        "name": request.form['name'],
        "phone": request.form['phone']
    })

    return "<h2 style='text-align:center;color:green;'>Order Placed ✅</h2>"

# ================= ADMIN LOGIN =================
@app.route('/admin')
def admin():
    return """
    <h2 style='text-align:center;'>Admin Login</h2>

    <form action='/dashboard' method='POST' style='text-align:center;'>
        <input type='password' name='pass' placeholder='Password'><br><br>
        <button>Login</button>
    </form>
    """

# ================= DASHBOARD =================
@app.route('/dashboard', methods=['POST'])
def dashboard():

    if request.form['pass'] != ADMIN_PASSWORD:
        return "Wrong Password"

    session['admin'] = True

    return """
    <h2 style='text-align:center;'>📦 Admin Panel</h2>

    <form action='/add' method='POST' enctype='multipart/form-data' style='text-align:center;'>

        <input name='name' placeholder='Product Name'><br><br>
        <input name='price' placeholder='Price'><br><br>

        <input type='file' name='media'><br><br>

        <input name='color' placeholder='Color'><br><br>
        <input name='size' placeholder='Size'><br><br>

        <button>Add Product</button>
    </form>

    <hr>
    <h3 style='text-align:center;'>Orders</h3>
    """ + "<br>".join([o['name'] + " ordered " + o['product'] for o in orders])

# ================= ADD PRODUCT (IMAGE + VIDEO) =================
@app.route('/add', methods=['POST'])
def add():

    if not session.get('admin'):
        return "Not allowed"

    file = request.files['media']

    upload = cloudinary.uploader.upload(
        file,
        resource_type="auto"   # 🔥 image + video both support
    )

    media_url = upload['secure_url']

    products.append({
        "id": str(uuid.uuid4()),
        "name": request.form['name'],
        "price": request.form['price'],
        "media": media_url,
        "color": request.form['color'],
        "size": request.form['size']
    })

    return redirect('/products')

# ================= DELETE =================
@app.route('/delete/<int:id>')
def delete(id):

    if not session.get('admin'):
        return "Not allowed"

    products.pop(id)
    return redirect('/products')

# ================= EDIT =================
@app.route('/edit/<int:id>')
def edit(id):

    p = products[id]

    return f"""
    <h2 style='text-align:center;'>Edit Product</h2>

    <form action='/update/{id}' method='POST' style='text-align:center;'>

        <input name='name' value='{p['name']}'><br><br>
        <input name='price' value='{p['price']}'><br><br>

        <input name='color' value='{p['color']}'><br><br>
        <input name='size' value='{p['size']}'><br><br>

        <button>Update</button>
    </form>
    """

# ================= UPDATE =================
@app.route('/update/<int:id>', methods=['POST'])
def update(id):

    products[id]['name'] = request.form['name']
    products[id]['price'] = request.form['price']
    products[id]['color'] = request.form['color']
    products[id]['size'] = request.form['size']

    return redirect('/products')

# ================= RUN =================
