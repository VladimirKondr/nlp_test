import json
import re
from include.DebugHelper import DebugHelper, time_func


class StructuredDataExtractor:
    def __init__(self, structured_product_helper):
        DebugHelper.log("Initializing StructuredDataExtractor", self.__class__.__qualname__)
        self.structured_product_helper = structured_product_helper
    
    @time_func()
    def extract_structured_product_data_json_ld(self, soup, structured_data):
        """Extract structured product data from JSON-LD, including currency."""
        DebugHelper.log("Extracting JSON-LD metadata", self.__class__.__qualname__)
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        for idx, script in enumerate(json_ld_scripts):
            try:
                if not script.string:
                    continue
                data = json.loads(script.string)
                if '@type' in data and data['@type'] == 'Product':
                    offers = data.get('offers', {})
                    product_data = {
                        'name': data.get('name', ''),
                        'description': data.get('description', ''),
                        'price': offers.get('price', ''),
                        'currency': offers.get('priceCurrency', ''),
                        'source': 'json-ld',
                        'confidence': 0.95
                    }
                    structured_data.append(product_data)
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and '@type' in item and item['@type'] == 'Product':
                            offers = item.get('offers', {})
                            product_data = {
                                'name': item.get('name', ''),
                                'description': item.get('description', ''),
                                'price': offers.get('price', ''),
                                'currency': offers.get('priceCurrency', ''),
                                'source': 'json-ld-array',
                                'confidence': 0.95
                            }
                            structured_data.append(product_data)
            except Exception as e:
                continue

    @time_func()
    def extract_structured_product_data_microdata(self, soup, structured_data):
        """Extract structured product data from microdata, including currency."""
        DebugHelper.log("Extracting microdata metadata", self.__class__.__qualname__)
        microdata_products = soup.find_all(itemtype=re.compile(r'schema.org/Product'))
        for product in microdata_products:
            name = product.find(itemprop="name")
            description = product.find(itemprop="description")
            price = product.find(itemprop="price")
            currency = None
            offers = product.find(itemprop="offers")
            if offers:
                price = price or offers.find(itemprop="price")
                currency = offers.find(itemprop="priceCurrency")
            product_data = {
                'name': self.structured_product_helper.get_property_value(name),
                'description': self.structured_product_helper.get_property_value(description),
                'price': self.structured_product_helper.get_property_value(price),
                'currency': self.structured_product_helper.get_property_value(currency),
                'source': 'microdata',
                'confidence': 0.9
            }
            structured_data.append(product_data)

    @time_func()
    def extract_structured_product_data_rdfa(self, soup, structured_data):
        """Extract product data from RDFa markup."""
        try:
            # Find all elements with typeof attribute that could represent products
            rdfa_candidates = soup.find_all(attrs={"typeof": True})
            
            # Filter only top-level Product elements
            product_candidates = []
            for candidate in rdfa_candidates:
                if "Product" in candidate.get("typeof", ""):
                    # Check if this is a top-level product (not nested in another product)
                    if not any(parent.has_attr("typeof") and "Product" in parent.get("typeof", "") 
                            for parent in candidate.parents):
                        product_candidates.append(candidate)
            
            for product in product_candidates:
                # Extract basic product data
                product_data = {
                    "name": "",
                    "description": "",
                    "price": "",
                    "currency": "",
                    "source": "rdfa",
                    "confidence": 0.9,
                    "category": ""
                }
                
                # Extract direct properties from the product element
                name_elem = product.find(attrs={"property": "name"})
                if name_elem:
                    product_data["name"] = self.structured_product_helper.get_property_value(name_elem)
                    
                desc_elem = product.find(attrs={"property": "description"})
                if desc_elem:
                    product_data["description"] = self.structured_product_helper.get_property_value(desc_elem)
                
                # Look for offers that might contain price information
                offers_elem = product.find(attrs={"property": "offers"})
                if offers_elem:
                    price_elem = offers_elem.find(attrs={"property": "price"})
                    if price_elem:
                        product_data["price"] = self.structured_product_helper.get_property_value(price_elem)
                        
                    currency_elem = offers_elem.find(attrs={"property": "priceCurrency"})
                    if currency_elem:
                        product_data["currency"] = self.structured_product_helper.get_property_value(currency_elem)
                
                # Direct price element (outside of offers)
                if not product_data["price"]:
                    price_elem = product.find(attrs={"property": "price"})
                    if price_elem:
                        product_data["price"] = self.structured_product_helper.get_property_value(price_elem)
                        
                # Direct currency element (outside of offers)
                if not product_data["currency"]:
                    currency_elem = product.find(attrs={"property": "priceCurrency"})
                    if currency_elem:
                        product_data["currency"] = self.structured_product_helper.get_property_value(currency_elem)
                
                # Only add products that have at least a name
                if product_data["name"]:
                    structured_data.append(product_data)
                    
        except Exception as e:
            # Log the error but continue processing
            print(f"Error extracting RDFa product data: {str(e)}")

    @time_func()
    def extract_structured_product_data_opengraph(self, soup, structured_data):
        """Extract product data from Open Graph, including currency."""
        DebugHelper.log("Extracting Open Graph metadata", self.__class__.__qualname__)
        og_title = soup.find('meta', {'property': 'og:title'})
        og_description = soup.find('meta', {'property': 'og:description'})
        og_price = soup.find('meta', {'property': 'og:price:amount'}) or soup.find('meta', {'property': 'product:price:amount'})
        og_currency = soup.find('meta', {'property': 'og:price:currency'}) or soup.find('meta', {'property': 'product:price:currency'})
        if og_title:
            product_data = {
                'name': self.structured_product_helper.get_property_value(og_title),
                'description': self.structured_product_helper.get_property_value(og_description) if og_description else '',
                'price': self.structured_product_helper.get_property_value(og_price) if og_price else '',
                'currency': self.structured_product_helper.get_property_value(og_currency) if og_currency else '',
                'source': 'opengraph',
                'confidence': 0.85
            }
            structured_data.append(product_data)

    @time_func()
    def extract_structured_product_data_twitter_card(self, soup, structured_data):
        """Extract product data from Twitter Card, including currency."""
        DebugHelper.log("Extracting Twitter Card metadata", self.__class__.__qualname__)
        twitter_title = soup.find('meta', {'name': 'twitter:title'})
        twitter_description = soup.find('meta', {'name': 'twitter:description'})
        twitter_label1 = soup.find('meta', {'name': 'twitter:label1'})
        twitter_data1 = soup.find('meta', {'name': 'twitter:data1'})
        if twitter_title:
            price, currency = '', ''
            if twitter_label1 and twitter_data1:
                label = self.structured_product_helper.get_property_value(twitter_label1).lower()
                if 'price' in label:
                    price_text = self.structured_product_helper.get_property_value(twitter_data1)
                    # Parse price for currency (e.g., "$799.00" or "SGD 329.00")
                    match = re.match(r'([A-Z$€£¥]+)?\s*(\d+\.?\d*)\s*([A-Z$€£¥]+)?', price_text)
                    if match:
                        currency = match.group(1) or match.group(3) or ''
                        price = match.group(2) or price_text
            product_data = {
                'name': self.structured_product_helper.get_property_value(twitter_title),
                'description': self.structured_product_helper.get_property_value(twitter_description) if twitter_description else '',
                'price': price,
                'currency': currency,
                'source': 'twitter_card',
                'confidence': 0.8
            }
            structured_data.append(product_data)

    @time_func()
    def extract_structured_product_data_dublin_core(self, soup, structured_data):
        """Extract product data from Dublin Core, no currency typically available."""
        DebugHelper.log("Extracting Dublin Core metadata", self.__class__.__qualname__)
        dc_title = soup.find('meta', {'name': 'DC.title'}) or soup.find('meta', {'property': 'DC.title'})
        dc_description = soup.find('meta', {'name': 'DC.description'}) or soup.find('meta', {'property': 'DC.description'})
        dc_subject = soup.find('meta', {'name': 'DC.subject'}) or soup.find('meta', {'property': 'DC.subject'})
        if dc_title:
            product_data = {
                'name': self.structured_product_helper.get_property_value(dc_title),
                'description': self.structured_product_helper.get_property_value(dc_description) if dc_description else '',
                'price': '',
                'currency': '',
                'source': 'dublin_core',
                'confidence': 0.75
            }
            if dc_subject:
                product_data['category'] = self.structured_product_helper.get_property_value(dc_subject)
            structured_data.append(product_data)



    @time_func()
    def extract_all_structured_data(self, soup):
        """Extract structured product data from schema.org markup"""

        DebugHelper.log("Extracting all structured data", self.__class__.__qualname__)
        structured_data = []
        
        # Look for JSON-LD markup
        self.extract_structured_product_data_json_ld(soup, structured_data)
                
        # Check for microdata schema.org product markup
        self.extract_structured_product_data_microdata(soup, structured_data)
        
        # Find elements with RDFa product markup
        self.extract_structured_product_data_rdfa(soup, structured_data)

        # Check for Open Graph metadata
        self.extract_structured_product_data_opengraph(soup, structured_data)

        # Check for Twitter Card metadata
        self.extract_structured_product_data_twitter_card(soup, structured_data)

        # Check for Dublin Core metadata
        self.extract_structured_product_data_dublin_core(soup, structured_data)

        return self.structured_product_helper.process_structured_data(structured_data)