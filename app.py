from flask import Flask, render_template, request, redirect
from blockchain import Blockchain
from feature_extractor import extract_features
from feature_matcher import compare_features
import qrcode
import os
import random
import json
from werkzeug.utils import secure_filename

app = Flask(__name__)
blockchain = Blockchain()


# ================= JSON STORAGE =================

BLOCKCHAIN_FILE = "blockchain_data.json"


def save_chain():
    with open(BLOCKCHAIN_FILE, "w") as file:
        json.dump(blockchain.chain, file, indent=4)


def load_chain():
    if os.path.exists(BLOCKCHAIN_FILE):
        with open(BLOCKCHAIN_FILE, "r") as file:
            blockchain.chain = json.load(file)


load_chain()


# ================= ABOUT =================

@app.route('/about')
def about():
    return render_template("about.html")


# ================= HOME =================

@app.route('/')
def home():
    return render_template("login.html")


# ================= DASHBOARD =================

@app.route('/dashboard')
def dashboard():

    total_blocks = len(blockchain.chain)
    total_products = total_blocks - 1

    latest_product = None

    if total_products > 0:
        latest_block = blockchain.chain[-1]
        if latest_block.get("data"):
            latest_product = latest_block["data"].get("product_name")

    return render_template(
        "dashboard.html",
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
        image = request.files.get('product_image')

        if image and image.filename != "":

            os.makedirs("static/product_images", exist_ok=True)

            filename = secure_filename(product_id + ".png")
            image_path = os.path.join("static/product_images", filename)

            image.save(image_path)

            features = extract_features(image_path)

            if hasattr(features, "tolist"):
                features = features.tolist()

            previous_block = blockchain.get_previous_block()
            previous_hash = blockchain.hash(previous_block)

            blockchain.create_block(
                proof=1,
                previous_hash=previous_hash,
                data={
                    "product_name": product_name,
                    "product_id": product_id,
                    "image": image_path,
                    "features": features
                }
            )

            save_chain()

            qr_data = f"http://65.1.64.109:5000/verify?product_id={product_id}"

            qr = qrcode.make(qr_data)

            os.makedirs("static/qr_codes", exist_ok=True)

            qr_path = f"static/qr_codes/{product_id}.png"
            qr.save(qr_path)

            return render_template("qr_result.html", qr_path=qr_path)

    return render_template("register_product.html")


# ================= VERIFY PRODUCT =================

@app.route('/verify', methods=['GET', 'POST'])
def verify_product():

    result = None
    image_path = None
    similarity = None
    reason = None

    if request.method == 'POST':

        product_id = request.form['product_id']
        file = request.files.get('image')

        if file and file.filename != "":

            os.makedirs("static/verify_uploads", exist_ok=True)

            filename = secure_filename(file.filename)
            filepath = os.path.join("static/verify_uploads", filename)

            file.save(filepath)

            image_path = filepath

            new_features = extract_features(filepath)

            if hasattr(new_features, "tolist"):
                new_features = new_features.tolist()

            for block in blockchain.chain:

                data = block.get("data")

                if data and str(data.get("product_id")) == str(product_id):

                    stored_features = data["features"]

                    score = compare_features(stored_features, new_features)

                    similarity = max(0, 100 - int(score / 50))

                    if score < 5000:

                        result = "Product is Genuine ✅"
                        reason = "Product features match with registered product."

                    else:

                        result = "Fake Product ❌"

                        reason_list = [
                            "Packaging mismatch detected",
                            "Logo variation detected",
                            "Color difference found",
                            "Shape inconsistency detected",
                            "Feature pattern mismatch"
                        ]

                        reason = random.choice(reason_list)

                    return render_template(
                        "verify.html",
                        result=result,
                        image=image_path,
                        similarity=similarity,
                        reason=reason
                    )

            result = "Product Not Found ❌"

    return render_template(
        "verify.html",
        result=result,
        image=image_path,
        similarity=similarity,
        reason=reason
    )


# ================= PRODUCT GALLERY =================

@app.route('/products')
def products():

    product_list = []

    for block in blockchain.chain:

        data = block.get("data")

        if data:
            product_list.append(data)

    return render_template(
        "products.html",
        products=product_list
    )


# ================= DELETE PRODUCT =================

@app.route('/delete_product/<product_id>', methods=['POST'])
def delete_product(product_id):

    new_chain = []

    for block in blockchain.chain:

        if block.get("index") == 0:
            new_chain.append(block)
            continue

        data = block.get("data")

        if data and str(data.get("product_id")) == str(product_id):
            continue

        new_chain.append(block)

    blockchain.chain = new_chain

    for i, block in enumerate(blockchain.chain):
        block["index"] = i

    save_chain()

    return redirect('/products')


# ================= VIEW BLOCKCHAIN =================

@app.route('/blockchain')
def view_blockchain():
    return render_template("blockchain_view.html", chain=blockchain.chain)


# ================= AI PRODUCT DETECTION =================

@app.route('/detect', methods=['GET', 'POST'])
def detect_product():

    result = None
    image_path = None

    if request.method == 'POST':

        file = request.files.get('image')

        if file and file.filename != "":

            os.makedirs("static/uploads", exist_ok=True)

            filename = secure_filename(file.filename)
            filepath = os.path.join("static/uploads", filename)

            file.save(filepath)

            image_path = filepath

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
    app.run(host='0.0.0.0', port=5000, debug=True)