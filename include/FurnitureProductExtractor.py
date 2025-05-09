

from include.DebugHelper import DebugHelper
from include.HTMLFetcher import HTMLFetcher
from include.HTMLProductFinder import HTMLProductFinder
from include.NLPModel import NLPModel
from include.ProductValidator import ProductValidator
from include.StructuredDataExtractor import StructuredDataExtractor
from include.StructuredProductHelper import StructuredProductHelper
from include.DebugHelper import time_func

class FurnitureProductExtractor:
    def __init__(self, model=None):
        """Initialize the furniture product extractor."""
        DebugHelper.log("Initializing FurnitureProductExtractor", self.__class__.__qualname__)
        self.nlp_model = model if model else NLPModel()
        self.html_fetcher = HTMLFetcher()
        self.product_validator = ProductValidator(self.nlp_model)
        self.structured_product_helper = StructuredProductHelper(self.nlp_model, self.product_validator)
        self.html_finder = HTMLProductFinder(self.nlp_model, self.product_validator, self.structured_product_helper)
        self.data_extractor = StructuredDataExtractor(self.structured_product_helper)
    
    @time_func()
    def process_url(self, url, include_unstructured = False):
        """Process URL to extract product names and structured data"""
        DebugHelper.log(f"Processing URL: {url}", self.__class__.__qualname__)
        soup = self.html_fetcher.fetch_page(url, 'lxml', 3)
        if not soup:
            return [{"bad request": True}]
            
        # Get structured data
        DebugHelper.log("Extracting structured data", self.__class__.__qualname__)
        products = self.data_extractor.extract_all_structured_data(soup)
        
        if (include_unstructured):
            # Find products in HTML tree
            DebugHelper.log("Finding products in HTML", self.__class__.__qualname__)
            products += self.html_finder.find_products(soup)
        
        return products