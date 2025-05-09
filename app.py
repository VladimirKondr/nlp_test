import subprocess
import os

# Run setup.py once before starting the app
setup_file = os.path.join(os.getcwd(), 'setup.py')
subprocess.run(['python', setup_file], check=True)
import nltk
nltk_data_dir = os.path.join(os.getcwd(), "nltk_data")
nltk.data.path.append(nltk_data_dir)
from flask import Flask, request, jsonify, render_template
from include.FurnitureProductExtractor import FurnitureProductExtractor

app = Flask(__name__)
extractor = FurnitureProductExtractor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/extract', methods=['POST'])
def extract():
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({"error": "URL is required"}), 400

    try:
        products = extractor.process_url(url, True)
        if products and products[0].get("bad request"):
            return jsonify({"error": "Failed to fetch the URL"}), 400

        product_names = [product.get('name', '') for product in products]
        return jsonify({"products": product_names})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)