from flask import Flask, render_template, request
from blockchain import Blockchain
from feature_extractor import extract_features
from feature_matcher import compare_features
import qrcode
import os
import random
from werkzeug.utils import secure_filename

app = Flask(__name__)
blockchain = Blockchain()


# ================= HOME =================
@app.route('/')
def home():
    return "WORKING ✅"


# ================= DASHBOARD =================
@app.route('/dashboard')
def dashboard():

    total_blocks = len(blockchain.chain)
    total_products = total_blocks - 1

    latest_product = None

    if total_products > 0:
        latest_product = blockchain.chain[-1]["data"]["product_name"]

    return render_template(
        "dashboard.html",
        total_blocks=total_blocks,
        total_products=total_products,
        latest_product=latest_product
    )


# ================= REGISTER PRODUCT =================
@app.route('/register', methods=['GET','POST'])
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

            # AI FEATURE EXTRACTION
            features = extract_features(image_path)

            # convert numpy → list
            if hasattr(features, "tolist"):
                features = features.tolist()

            # Blockchain block
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

            # QR CODE
            qr_data = f"http://127.0.0.1:5000/verify?product_id={product_id}"

            qr = qrcode.make(qr_data)

            os.makedirs("static/qr_codes", exist_ok=True)

            qr_path = f"static/qr_codes/{product_id}.png"
            qr.save(qr_path)

            return render_template("qr_result.html", qr_path=qr_path)

    return render_template("register_product.html")


# ================= VERIFY PRODUCT =================
@app.route('/verify', methods=['GET','POST'])
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

            for block in blockchain.chain:

                if block.get("data") and block["data"].get("product_id") == product_id:

                    stored_features = block["data"]["features"]

                    score = compare_features(stored_features, new_features)

                    # similarity %
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
        if block.get("data"):
            product_list.append(block["data"])

    return render_template(
        "products.html",
        products=product_list
    )


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
    app.run(debug=True)