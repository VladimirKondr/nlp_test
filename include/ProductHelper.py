from difflib import SequenceMatcher
from functools import lru_cache
import re
from typing import Any, Dict, List


class ProductHelper:
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

    def are_duplicates(self, product1: str, product2: str) -> bool:
        """Determine if two products are duplicates."""
        if not product1 or not product2:
            return False

        name1 = self.normalize_name(product1)
        name2 = self.normalize_name(product2)

        if name1 == name2:
            return True

        similarity = self.calculate_similarity(name1, name2)
        if similarity >= self.similarity_threshold:
            return True

        if name1 in name2 or name2 in name1:
            return True

        return False
    
    def remove_duplicates(self, products: List[str]) -> List[str]:
        """Remove duplicate product names from a list."""
        unique_products = []
        seen = set()

        for product in products:
            normalized_name = self.normalize_name(product)
            if normalized_name not in seen:
                seen.add(normalized_name)
                unique_products.append(product)

        return unique_products

    def process(self, products: List[str]) -> List[str]:
        """Process a list of product names, removing duplicates and normalizing."""
        if not products:
            return []
        
        # Remove empty
        products = [p for p in products if p]

        # Remove duplicates
        unique_products = self.remove_duplicates(products)

        return unique_products