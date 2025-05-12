from include.ProductValidator import ProductValidator

class FurnitureProductValidator(ProductValidator):
    def __init__(self, nlp_model=None, furniture_properties=None):
        super().__init__(nlp_model if nlp_model else NLPModel())
        self.furniture_properties = furniture_properties or [
            'width', 'height', 'depth', 'material', 'color', 'dimensions', 'size', 'weight',
            'style', 'finish', 'design', 'shape', 'pattern', 'texture', 'price', 'brand',
            'manufacturer', 'assembly', 'features', 'warranty', 'care instructions'
        ]

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

    def is_valid_product_name(self, name, tag=None):
        """Validate product name with furniture-specific checks."""
        if not super().is_valid_product_name(name, tag):
            return False

        if not self._contains_furniture_terms(name, tag):
            return False

        return True