from include.DebugHelper import DebugHelper
from include.NLPModel import NLPModel
from include.ProductValidator import ProductValidator

class HTMLProductFinder:
    def __init__(self, nlp_model=None, validator=None, filter_criteria=None):
        """Initialize with NLP models, validator, text processor, and optional filter criteria."""
        DebugHelper().log("Initializing HTMLProductFinder", self.__class__.__qualname__)
        self.nlp_model = nlp_model if nlp_model else NLpModel()
        self.validator = validator if validator else ProductValidator(self.nlp_model)
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

        elements = soup.find_all(self.filter_criteria)

        for element in elements:
            text = element.get_text(strip=True)
            if self.validator.is_valid_product_name(text, element):
                result.append(text)

        return result

    def find_products(self, soup):
        """Main method for finding products, returning a list of dictionaries with product attributes."""
        DebugHelper().log("Finding products in HTML", self.__class__.__qualname__)
        return self.find_products_dumb(soup)