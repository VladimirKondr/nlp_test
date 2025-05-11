from include.DebugHelper import DebugHelper
from include.HTMLFetcher import HTMLFetcher
from include.HTMLProductFinder import HTMLProductFinder
from include.NLPModel import NLPModel
from include.ProductValidator import ProductValidator
from include.StructuredDataExtractor import StructuredDataExtractor
from include.StructuredProductHelper import StructuredProductHelper

class FurnitureProductExtractor:
    def __init__(self, html_fetcher=None, product_finder=None, data_extractor=None):
        """Initialize the furniture product extractor with modular components."""
        DebugHelper().log("Initializing FurnitureProductExtractor", self.__class__.__qualname__)
        self.html_fetcher = html_fetcher if html_fetcher else HTMLFetcher(timeout=3)
        nlp_model = NLPModel()
        validator = ProductValidator(nlp_model)
        structured_product_helper = StructuredProductHelper(nlp_model, validator)
        self.product_finder = product_finder if product_finder else HTMLProductFinder(nlp_model, validator, structured_product_helper)
        self.data_extractor = data_extractor if data_extractor else StructuredDataExtractor(structured_product_helper)

    def fetch_html(self, url):
        """Fetch and parse HTML from a URL."""
        DebugHelper().log(f"Fetching HTML for URL: {url}", self.__class__.__qualname__)
        return self.html_fetcher.fetch_page(url, 'lxml')

    def extract_structured_data(self, soup):
        """Extract structured product data from the HTML soup."""
        DebugHelper().log("Extracting structured data", self.__class__.__qualname__)
        return self.data_extractor.extract_all_structured_data(soup)

    def extract_unstructured_data(self, soup):
        """Extract unstructured product data from the HTML soup."""
        DebugHelper().log("Extracting unstructured data", self.__class__.__qualname__)
        return self.product_finder.find_products(soup)

    def process_structured_data(self, soup):
        """Process URL to extract only structured product data."""
        return self.extract_structured_data(soup)

    def process_unstructured_data(self, soup):
        """Process URL to extract only unstructured product data."""
        return self.extract_unstructured_data(soup)

    def process_url(self, url, include_unstructured=False):
        """Process URL to extract product names and structured data."""
        DebugHelper().log(f"Processing URL: {url}", self.__class__.__qualname__)
        soup = self.fetch_html(url)
        if not soup:
            return [{"bad request": True}]
        DebugHelper().log(f"Processing structured data for URL: {url}", self.__class__.__qualname__)
        structured_data = self.process_structured_data(soup)
        if include_unstructured:
            DebugHelper().log(f"Processing unstructured data for URL: {url}", self.__class__.__qualname__)
            unstructured_data = self.process_unstructured_data(soup)
            return structured_data + unstructured_data
        return structured_data