from include.NLPModel import NLPModel

class ProductValidator:
    def __init__(self, nlp_model):
        self.model = nlp_model if nlp_model else NLPModel()
        
    def is_valid_product_name(self, name, tag=None):
        """Universal product name validation."""
        if not self._is_valid_length(name):
            return False

        if not self._is_valid_word_count(name):
            return False

        if not self._has_valid_special_characters(name):
            return False

        return True

    def _is_valid_length(self, name):
        """Check if the product name length is valid."""
        return 3 <= len(name) <= 50

    def _is_valid_word_count(self, name):
        """Check if the product name has a valid word count."""
        word_count = len(name.split())
        return 1 <= word_count <= 10

    def _has_valid_special_characters(self, name):
        """Check if the product name has a valid number of special characters."""
        special_char_count = sum(1 for c in name if c in r"!@#$%^&*()_+={}[]|\\:;<>?/")
        return special_char_count <= 2