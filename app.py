from flask import Flask, request, redirect

app = Flask(__name__)

cart = []
orders = []

# HOME / LOGIN
@app.route('/')
def home():
    return """
    <h2 style='text-align:center;'>👟 Shoes Place</h2>

    <div style='text-align:center;'>
    <a href='/products'>🛍️ Products</a> |
    <a href='/cart'>🧾 Cart</a>
    </div>

    <form action='/products' style='text-align:center;margin-top:20px;'>
    <input name='name' placeholder='Enter Name'><br><br>
    <button>Enter Shop</button>
    </form>
    """

# PRODUCTS
@app.route('/products')
def products():
    return """
    <h2 style='text-align:center;'>🔥 Products</h2>

    <div style='text-align:center;'>

    <div style='border:1px solid gray;margin:10px;padding:10px'>
    <img src="https://i.ibb.co/your-image.jpg" width="200"><br>
    <h3>Nike Air</h3>
    <p>3000৳</p>

    <a href='/order?product=Nike Air'>📦 Order Now</a><br>
    <a href='/add/Nike Air'>🛒 Add to Cart</a>
    </div>

    <div style='border:1px solid gray;margin:10px;padding:10px'>
    <img src="https://i.ibb.co/your-image2.jpg" width="200"><br>
    <h3>Adidas Run</h3>
    <p>2500৳</p>

    <a href='/order?product=Adidas Run'>📦 Order Now</a><br>
    <a href='/add/Adidas Run'>🛒 Add to Cart</a>
    </div>

    </div>
    """

# ADD CART
@app.route('/add/<item>')
def add(item):
    cart.append(item)
    return redirect('/products')

# CART
@app.route('/cart')
def cart_page():
    return f"""
    <h2 style='text-align:center;'>🧾 Cart</h2>
    <p style='text-align:center;'>{cart}</p>
    """

# ORDER FORM
@app.route('/order')
def order():
    product = request.args.get('product')

    return f"""
    <h2 style='text-align:center;'>📦 Order Form</h2>

    <form action='/submit_order' method='POST' style='text-align:center;'>

    <input name='name' placeholder='Name'><br><br>
    <input name='phone' placeholder='Phone'><br><br>
    <input name='address' placeholder='Address'><br><br>

    <input name='product' value='{product}'><br><br>

    <input name='color' placeholder='Color'><br><br>
    <input name='size' placeholder='Size'><br><br>
    <input name='qty' placeholder='Quantity'><br><br>

    <button>Place Order</button>

    </form>
    """

# SAVE ORDER
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

    return """
    <h2 style='text-align:center;color:green;'>Order Placed ✅</h2>
    <a href='/'>Home</a>
    """

# ADMIN PANEL
@app.route('/admin')
def admin():

    html = "<h2 style='text-align:center;'>🧾 Orders</h2>"

    for o in orders:
        html += f"""
        <div style='border:1px solid gray;margin:10px;padding:10px'>
        Name: {o['name']}<br>
        Phone: {o['phone']}<br>
        Product: {o['product']}<br>
        Color: {o['color']}<br>
        Size: {o['size']}<br>
        Qty: {o['qty']}<br>
        </div>
        """

    return html

app.run(host='0.0.0.0', port=10000)
