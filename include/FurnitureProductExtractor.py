from include.DebugHelper import DebugHelper
from include.HTMLFetcher import HTMLFetcher
from include.HTMLProductFinder import HTMLProductFinder
from include.NLPModel import NLPModel
from include.FurnitureProductValidator import FurnitureProductValidator
from include.StructuredDataExtractor import StructuredDataExtractor
from include.ProductHelper import ProductHelper

class FurnitureProductExtractor:
    def __init__(self,
            html_fetcher=None,
            nlp_model=None,
            product_validator=None,
            product_helper=None,
            product_finder=None,
            data_extractor=None):
        """Initialize the furniture product extractor with modular components."""
        DebugHelper().log("Initializing FurnitureProductExtractor", self.__class__.__qualname__)
        self.html_fetcher = html_fetcher if html_fetcher else HTMLFetcher(timeout=3)
        nlp_model = nlp_model if nlp_model else NLPModel()
        validator = product_validator if product_validator else FurnitureProductValidator(nlp_model)
        self.product_helper = product_helper if product_helper else ProductHelper(nlp_model, validator)
        self.product_finder = product_finder if product_finder else HTMLProductFinder(nlp_model, validator, self.product_helper)
        self.data_extractor = data_extractor if data_extractor else StructuredDataExtractor(self.product_helper)

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

    def process_url(self, url, include_unstructured=False):
        """Process URL to extract product names and structured data."""
        DebugHelper().log(f"Processing URL: {url}", self.__class__.__qualname__)
        soup = self.fetch_html(url)
        if not soup:
            return [{"bad request": True}]
        DebugHelper().log(f"Processing structured data for URL: {url}", self.__class__.__qualname__)
        structured_data = self.extract_structured_data(soup)
        unstructured_data = []
        if include_unstructured:
            DebugHelper().log(f"Processing unstructured data for URL: {url}", self.__class__.__qualname__)
            unstructured_data = self.extract_unstructured_data(soup)
        
        data = structured_data + unstructured_data
        self.product_helper.process(data)
        return data
