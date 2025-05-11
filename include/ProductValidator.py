class ProductValidator:
    def __init__(self, nlp_model, furniture_properties=None):
        self.model = nlp_model
        self.furniture_properties = furniture_properties or [
            'width', 'height', 'depth', 'material', 'color', 'dimensions', 'size', 'weight',
            'style', 'finish', 'design', 'shape', 'pattern', 'texture', 'price', 'brand',
            'manufacturer', 'assembly', 'features', 'warranty', 'care instructions'
        ]

    def is_valid_product_name(self, name, tag=None):
        """Universal product name validation."""
        if not self._is_valid_length(name):
            return False

        if not self._is_valid_word_count(name):
            return False

        if not self._has_valid_special_characters(name):
            return False

        if not self._contains_furniture_terms(name, tag):
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

    def _contains_furniture_terms(self, name, tag):
        """Check if the product name or surrounding tag contains furniture-related terms."""
        tokens = self.model.tokenize(name)
        furniture_tokens = [t for t in tokens if self.model.predict_category_membership(t.lemma_, "furniture")]
        return bool(furniture_tokens) or self._has_furniture_related_property(tag)

    def _has_furniture_related_property(self, tag):
        """Check if element surroundings indicate furniture."""
        if not tag:
            return False

        nearby_text = ' '.join(t.get_text().lower() for t in tag.find_all(['span', 'div', 'p'], limit=5))
        return any(prop in nearby_text for prop in self.furniture_properties)