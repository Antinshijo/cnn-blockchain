from flask import Flask, render_template, request
from blockchain import Blockchain
import qrcode
import os
import random

app = Flask(__name__)
blockchain = Blockchain()

# ================= HOME =================
@app.route('/')
def home():
    return render_template("login.html")


# ================= DASHBOARD =================
@app.route('/dashboard')
def dashboard():

    total_blocks = len(blockchain.chain)

    # Genesis block remove pannina real product count
    total_products = total_blocks - 1

    latest_product = None

    if total_products > 0:
        latest_product = blockchain.chain[-1]["data"]["product_name"]

    return render_template(
        "dashboard.html",
        chain=blockchain.chain,
        total_blocks=total_blocks,
        total_products=total_products,
        latest_product=latest_product
    )


# ================= REGISTER PRODUCT =================
@app.route('/register', methods=['GET', 'POST'])
def register_product():

    if request.method == 'POST':

        product_name = request.form['product_name']
        product_id = request.form['product_id']

        # Blockchain block create
        previous_block = blockchain.get_previous_block()
        previous_hash = blockchain.hash(previous_block)

        blockchain.create_block(
            proof=1,
            previous_hash=previous_hash,
            data={
                "product_name": product_name,
                "product_id": product_id
            }
        )

        # QR CODE GENERATION
        qr_data = f"http://127.0.0.1:5000/verify?product_id={product_id}"

        qr = qrcode.make(qr_data)

        os.makedirs("static/qr_codes", exist_ok=True)

        qr_path = f"static/qr_codes/{product_id}.png"
        qr.save(qr_path)

        return render_template("qr_result.html", qr_path=qr_path)

    return render_template("register_product.html")


# ================= VERIFY PRODUCT =================
@app.route('/verify', methods=['GET', 'POST'])
def verify_product():

    product_id = request.args.get('product_id')

    if request.method == 'POST':
        product_id = request.form['product_id']

    if product_id:

        for block in blockchain.chain:

            if block.get("data") and block["data"].get("product_id") == product_id:

                return render_template(
                    "verify.html",
                    result="Product is Genuine ✅",
                    product_id=product_id
                )

        return render_template(
            "verify.html",
            result="Product Not Found ❌",
            product_id=product_id
        )

    return render_template("verify.html")


# ================= VIEW BLOCKCHAIN =================
@app.route('/blockchain')
def view_blockchain():
    return render_template("blockchain_view.html", chain=blockchain.chain)


# ================= AI PRODUCT DETECTION =================
@app.route('/detect', methods=['GET','POST'])
def detect_product():

    result = None
    image_path = None

    if request.method == 'POST':

        file = request.files.get('image')

        if file and file.filename != "":

            os.makedirs("static/uploads", exist_ok=True)

            filepath = os.path.join("static/uploads", file.filename)
            file.save(filepath)

            image_path = filepath

            # AI Simulation
            result = random.choice([
                "Genuine Product ✅",
                "Fake Product ❌"
            ])

    return render_template(
        "detect.html",
        result=result,
        image=image_path
    )


# ================= RUN SERVER =================
if __name__ == '__main__':
    app.run(debug=True)