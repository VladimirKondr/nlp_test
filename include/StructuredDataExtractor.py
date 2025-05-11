import json
import re
from include.DebugHelper import DebugHelper


class StructuredDataExtractor:
    def __init__(self, product_helper):
        DebugHelper().log("Initializing StructuredDataExtractor", self.__class__.__qualname__)
        self.product_helper = product_helper
    
    def extract_structured_product_data_json_ld(self, soup, structured_data):
        """Extract structured product data from JSON-LD, including currency."""
        DebugHelper().log("Extracting JSON-LD metadata", self.__class__.__qualname__)
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        for idx, script in enumerate(json_ld_scripts):
            try:
                if not script.string:
                    continue
                data = json.loads(script.string)
                if '@type' in data and data['@type'] == 'Product':
                    structured_data.append(data.get('name', ''))
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and '@type' in item and item['@type'] == 'Product':
                            structured_data.append(item.get('name', ''))
            except Exception as e:
                DebugHelper().log(f"Error parsing JSON-LD script {idx}: {str(e)}", self.__class__.__qualname__)
                continue

    def extract_structured_product_data_microdata(self, soup, structured_data):
        """Extract structured product data from microdata, including currency."""
        DebugHelper().log("Extracting microdata metadata", self.__class__.__qualname__)
        try:
            microdata_products = soup.find_all(itemtype=re.compile(r'schema.org/Product'))
            for product in microdata_products:
                name = product.find(itemprop="name")
                structured_data.append(self.product_helper.get_property_value(name))
        except Exception as e:
            # Log the error but continue processing
            DebugHelper().log(f"Error extracting microdata product data: {str(e)}", self.__class__.__qualname__)
            return
            

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
                # Extract direct properties from the product element
                name_elem = product.find(attrs={"property": "name"})
                structured_data.append(self.product_helper.get_property_value(name_elem))
                    
        except Exception as e:
            # Log the error but continue processing
            DebugHelper().log(f"Error extracting RDFa product data: {str(e)}", self.__class__.__qualname__)



    def extract_all_structured_data(self, soup):
        """Extract structured product data from schema.org markup"""

        DebugHelper().log("Extracting all structured data", self.__class__.__qualname__)
        structured_data = []
        
        # Look for JSON-LD markup
        self.extract_structured_product_data_json_ld(soup, structured_data)
                
        # Check for microdata schema.org product markup
        self.extract_structured_product_data_microdata(soup, structured_data)
        
        # Find elements with RDFa product markup
        self.extract_structured_product_data_rdfa(soup, structured_data)

        return structured_data