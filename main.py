import nltk
import os
nltk_data_dir = os.path.join(os.getcwd(), "nltk_data")


nltk.data.path.append(nltk_data_dir)

from include.FurnitureProductExtractor import FurnitureProductExtractor


extractor = FurnitureProductExtractor()
url = "https://www.vavoom.com.au/products/ebony-chest"
products = extractor.process_url(url, True)
if products and products[0].get("bad request"):
    print("Bad request")
names = [product.get('name', '') for product in products]
print(names)