from flask import Flask, request, redirect

app = Flask(__name__)

cart = []
orders = []

# PRODUCTS DATABASE (NEW + OLD)
products = [
    {
        "id": "nike_air",
        "name": "Nike Air Max",
        "price": 3200,
        "img": "https://via.placeholder.com/300",
        "colors": ["Black", "White"],
        "sizes": ["40", "41", "42", "43"]
    },
    {
        "id": "adidas_run",
        "name": "Adidas Running",
        "price": 2700,
        "img": "https://via.placeholder.com/300",
        "colors": ["Red", "Blue"],
        "sizes": ["40", "41", "42"]
    },
    {
        "id": "puma_sport",
        "name": "Puma Sport",
        "price": 2500,
        "img": "https://via.placeholder.com/300",
        "colors": ["Black", "Green"],
        "sizes": ["39", "40", "41", "42"]
    },
    {
        "id": "new_balance",
        "name": "New Balance",
        "price": 2900,
        "img": "https://via.placeholder.com/300",
        "colors": ["Grey", "White"],
        "sizes": ["40", "41", "42", "43"]
    }
]

# HOME
@app.route('/')
def home():
    return """
    <h1 style='text-align:center;'>👟 Shoes Place</h1>
    <div style='text-align:center;'>
        <a href='/products'>Products</a> |
        <a href='/cart'>Cart</a> |
        <a href='/admin'>Admin</a>
    </div>
    """

# PRODUCTS
@app.route('/products')
def products_page():
    html = "<h2 style='text-align:center;'>🔥 All Shoes</h2>"
    html += "<div style='display:flex;flex-wrap:wrap;justify-content:center;gap:20px;'>"

    for p in products:
        html += f"""
        <div style='border:1px solid #ccc;padding:10px;width:220px;text-align:center;'>
            <img src="{p['img']}" width="200"><br>
            <h3>{p['name']}</h3>
            <p>{p['price']}৳</p>

            <a href='/add/{p['id']}' style='background:green;color:white;padding:5px;display:block;margin:5px;'>Add to Cart</a>

            <a href='/order_form/{p['id']}' style='background:orange;color:white;padding:5px;display:block;'>Order Now</a>
        </div>
        """

    html += "</div>"
    return html

# ADD CART
@app.route('/add/<pid>')
def add(pid):
    cart.append(pid)
    return redirect('/products')

# CART
@app.route('/cart')
def cart_page():
    items = [p for p in products if p['id'] in cart]

    html = "<h2 style='text-align:center;'>🛒 Cart</h2>"

    for i in items:
        html += f"<p style='text-align:center;'>{i['name']} - {i['price']}৳</p>"

    return html

# ORDER FORM
@app.route('/order_form/<pid>')
def order_form(pid):
    product = next((p for p in products if p['id'] == pid), None)

    if not product:
        return "Product not found"

    return f"""
    <h2 style='text-align:center;'>📦 Order Now</h2>

    <form action='/submit_order' method='POST' style='text-align:center;'>

    <input name='name' placeholder='Your Name' required><br><br>
    <input name='phone' placeholder='Phone' required><br><br>
    <input name='address' placeholder='Address' required><br><br>

    <input name='product' value='{product['name']}' readonly><br><br>

    <select name='color'>
        <option>{product['colors'][0]}</option>
        <option>{product['colors'][1]}</option>
    </select><br><br>

    <select name='size'>
        <option>{product['sizes'][0]}</option>
        <option>{product['sizes'][1]}</option>
    </select><br><br>

    <input name='qty' placeholder='Quantity'><br><br>

    <button>Place Order</button>

    </form>
    """

# SUBMIT ORDER
@app.route('/submit_order', methods=['POST'])
def submit_order():

    data = {
        "name": request.form['name'],
        "phone": request.form['phone'],
        "address": request.form['address'],
        "product": request.form['product'],
        "color": request.form['color'],
        "size": request.form['size'],
        "qty": request.form['qty']
    }

    orders.append(data)

    print("NEW ORDER:", data)

    return "<h2 style='text-align:center;color:green;'>Order Placed ✅</h2><a href='/'>Home</a>"

# ADMIN PANEL
@app.route('/admin')
def admin():
    html = "<h2 style='text-align:center;'>🧾 Orders</h2>"

    for o in orders:
        html += f"""
        <div style='border:1px solid gray;margin:10px;padding:10px'>
        <b>{o['product']}</b><br>
        {o['name']} | {o['phone']}<br>
        {o['color']} | {o['size']} | Qty: {o['qty']}
        </div>
        """

    return html

app.run(host='0.0.0.0', port=5000)