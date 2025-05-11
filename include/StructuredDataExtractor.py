import json
import re
from include.DebugHelper import DebugHelper


class StructuredDataExtractor:
    def __init__(self, structured_product_helper):
        DebugHelper().log("Initializing StructuredDataExtractor", self.__class__.__qualname__)
        self.structured_product_helper = structured_product_helper
        self.extractors = self._register_extractors()

    def _register_extractors(self):
        """Register all available extractors."""
        return [
            self.extract_json_ld,
            self.extract_microdata,
            self.extract_rdfa,
            self.extract_opengraph,
            self.extract_twitter_card,
            self.extract_dublin_core
        ]

    def extract_structured_product_data(self, soup, structured_data):
        """Generic method to extract structured product data using registered extractors."""
        for extractor in self.extractors:
            try:
                extractor(soup, structured_data)
            except Exception as e:
                DebugHelper().log(f"Error in extractor {extractor.__name__}: {str(e)}", self.__class__.__qualname__)

    def extract_json_ld(self, soup, structured_data):
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_ld_scripts:
            try:
                if not script.string:
                    continue
                data = json.loads(script.string)
                self.add_product_data(data, structured_data, 'json-ld', 0.95)
            except Exception:
                continue

    def extract_microdata(self, soup, structured_data):
        microdata_products = soup.find_all(itemtype=re.compile(r'schema.org/Product'))
        for product in microdata_products:
            product_data = {
                'name': self.structured_product_helper.get_property_value(product.find(itemprop="name")),
                'description': self.structured_product_helper.get_property_value(product.find(itemprop="description")),
                'price': self.structured_product_helper.get_property_value(product.find(itemprop="price")),
                'currency': self.structured_product_helper.get_property_value(product.find(itemprop="priceCurrency")),
                'source': 'microdata',
                'confidence': 0.9
            }
            structured_data.append(product_data)

    def extract_rdfa(self, soup, structured_data):
        rdfa_candidates = soup.find_all(attrs={"typeof": True})
        for candidate in rdfa_candidates:
            if "Product" in candidate.get("typeof", ""):
                product_data = {
                    "name": self.structured_product_helper.get_property_value(candidate.find(attrs={"property": "name"})),
                    "description": self.structured_product_helper.get_property_value(candidate.find(attrs={"property": "description"})),
                    "price": self.structured_product_helper.get_property_value(candidate.find(attrs={"property": "price"})),
                    "currency": self.structured_product_helper.get_property_value(candidate.find(attrs={"property": "priceCurrency"})),
                    "source": "rdfa",
                    "confidence": 0.9
                }
                structured_data.append(product_data)

    def extract_opengraph(self, soup, structured_data):
        og_title = soup.find('meta', {'property': 'og:title'})
        if og_title:
            product_data = {
                'name': self.structured_product_helper.get_property_value(og_title),
                'description': self.structured_product_helper.get_property_value(soup.find('meta', {'property': 'og:description'})),
                'price': self.structured_product_helper.get_property_value(soup.find('meta', {'property': 'og:price:amount'})),
                'currency': self.structured_product_helper.get_property_value(soup.find('meta', {'property': 'og:price:currency'})),
                'source': 'opengraph',
                'confidence': 0.85
            }
            structured_data.append(product_data)

    def extract_twitter_card(self, soup, structured_data):
        twitter_title = soup.find('meta', {'name': 'twitter:title'})
        if twitter_title:
            product_data = {
                'name': self.structured_product_helper.get_property_value(twitter_title),
                'description': self.structured_product_helper.get_property_value(soup.find('meta', {'name': 'twitter:description'})),
                'price': '',
                'currency': '',
                'source': 'twitter_card',
                'confidence': 0.8
            }
            structured_data.append(product_data)

    def extract_dublin_core(self, soup, structured_data):
        dc_title = soup.find('meta', {'name': 'DC.title'})
        if dc_title:
            product_data = {
                'name': self.structured_product_helper.get_property_value(dc_title),
                'description': self.structured_product_helper.get_property_value(soup.find('meta', {'name': 'DC.description'})),
                'price': '',
                'currency': '',
                'source': 'dublin_core',
                'confidence': 0.75
            }
            structured_data.append(product_data)

    def extract_all_structured_data(self, soup):
        DebugHelper().log("Extracting all structured data", self.__class__.__qualname__)
        structured_data = []
        self.extract_structured_product_data(soup, structured_data)
        return self.structured_product_helper.process_structured_data(structured_data)

    def add_product_data(self, data, structured_data, source, confidence):
        """Add product data to the structured data list."""
        product_data = {
            'name': data.get('name', ''),
            'description': data.get('description', ''),
            'price': data.get('offers', {}).get('price', ''),
            'currency': data.get('offers', {}).get('priceCurrency', ''),
            'source': source,
            'confidence': confidence
        }
        structured_data.append(product_data)