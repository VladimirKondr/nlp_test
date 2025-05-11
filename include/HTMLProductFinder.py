from include.DebugHelper import DebugHelper


class HTMLProductFinder:
    def __init__(self, nlp_model, validator, structured_product_helper, filter_criteria=None):
        """Initialize with NLP models, validator, text processor, and optional filter criteria."""
        DebugHelper().log("Initializing HTMLProductFinder", self.__class__.__qualname__)
        self.nlp_model = nlp_model
        self.validator = validator
        self.structured_product_helper = structured_product_helper
        self.filter_criteria = filter_criteria or self.default_filter_criteria

    def default_filter_criteria(self, tag):
        """Default filter criteria for identifying product elements."""
        if not tag.has_attr('class'):
            return False
        classes = ' '.join(tag['class']).lower()
        return ('product' in classes and ('title' in classes or 'name' in classes)) or \
               ('title' in classes or 'name' in classes)

    def find_products_dumb(self, soup):
        result = []

        # Use the provided filter criteria to find elements
        elements = soup.find_all(self.filter_criteria)

        # Extract and validate text
        for element in elements:
            text = element.get_text(strip=True)
            if self.validator.is_valid_product_name(text, element):
                result.append({"name": text})

        return result

    def find_products(self, soup):
        """Main method for finding products, returning a list of dictionaries with product attributes."""
        DebugHelper().log("Finding products in HTML", self.__class__.__qualname__)
        return self.find_products_dumb(soup)