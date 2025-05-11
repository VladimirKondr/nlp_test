from difflib import SequenceMatcher
from functools import lru_cache
import re
from typing import Any, Dict, List


class StructuredProductHelper:
    def __init__(self, nlp_model=None, validator=None, similarity_threshold=0.8, normalization_rules=None):
        """
        Initialize helper for processing product dictionaries.

        Args:
            nlp_model: NLPModel for linguistic analysis (optional).
            validator: ProductValidator for product validation (optional).
            similarity_threshold: Threshold for determining duplicates.
            normalization_rules: Configurable rules for name normalization.
        """
        self.nlp_model = nlp_model
        self.validator = validator
        self.similarity_threshold = similarity_threshold
        self.normalization_rules = normalization_rules or self.default_normalization_rules()

    def default_normalization_rules(self):
        """Default rules for normalizing product names."""
        return [
            (r'\s*\|\s*.*$', ''),
            (r'\s*(shop|buy|online|store|collection).*', ''),
            (r'\s+', ' '),
            (r'[.,;:-| ]$', ''),
            (r'[^\w\s]', ''),
            (r'\s+', ' ')
        ]

    def get_property_value(self, tag):
        """Helper method to extract value from a tag, handling both meta tags and text content."""
        if tag and tag.name == 'meta' and tag.get('content'):
            return tag.get('content').strip()
        elif tag:
            return tag.get_text(strip=True)
        return ''

    @lru_cache(maxsize=1000)
    def normalize_name(self, name: str) -> str:
        """Normalize product name for comparison."""
        if not name:
            return ""
        result = name.lower()
        for pattern, replacement in self.normalization_rules:
            result = re.sub(pattern, replacement, result)
        doc = self.nlp_model.tokenize(result)
        return ' '.join([token.lemma_ for token in doc if not token.is_punct])

    @lru_cache(maxsize=1000)
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two strings."""
        return SequenceMatcher(None, text1, text2).ratio()

    def are_duplicates(self, product1: Dict[str, Any], product2: Dict[str, Any]) -> bool:
        """Determine if two products are duplicates."""
        if not product1.get('name') or not product2.get('name'):
            return False

        name1 = self.normalize_name(product1['name'])
        name2 = self.normalize_name(product2['name'])

        if name1 == name2:
            return True

        similarity = self.calculate_similarity(name1, name2)
        if similarity >= self.similarity_threshold:
            return True

        if name1 in name2 or name2 in name1:
            return True

        return False

    def merge_products(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge duplicate products, retaining the most complete information."""
        if not products:
            return []

        groups = []
        for product in products:
            found_group = False
            for group in groups:
                if any(self.are_duplicates(product, item) for item in group):
                    group.append(product)
                    found_group = True
                    break

            if not found_group:
                groups.append([product])

        return [self.select_best_product(group) for group in groups]

    def select_best_product(self, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Select the best product from a group of duplicates."""
        if not products:
            return {}
        if len(products) == 1:
            return products[0]

        sorted_products = sorted(products, key=lambda p: p.get('confidence', 0), reverse=True)
        best_product = sorted_products[0].copy()

        for product in sorted_products[1:]:
            for key, value in product.items():
                if key not in best_product and value:
                    best_product[key] = value
        return best_product

    def process_structured_data(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Return a list of the best unique products.

        Args:
            products: List of dictionaries with product information.

        Returns:
            List of unique products with the best information.
        """
        filtered_products = self._filter_valid_products(products)
        return self.merge_products(filtered_products)

    def _filter_valid_products(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter products to include only valid ones."""
        filtered = [p for p in products if p.get('name')]
        if self.validator:
            filtered = [p for p in filtered if self.validator.is_valid_product_name(p.get('name', ''))]
        return filtered