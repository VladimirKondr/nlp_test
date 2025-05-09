class ProductValidator:
    def __init__(self, nlp_model):
        self.model = nlp_model

    def is_valid_product_name(self, name, tag=None):
        """Universal product name validation"""
        # Length and structure checks
        if len(name) < 3 or len(name) > 50:
            return False
            
        word_count = len(name.split())
        if word_count < 1 or word_count > 10:
            return False

        # Special character check
        special_char_count = sum(1 for c in name if c in r"!@#$%^&*()_+={}[]|\:;<>?/")
        if special_char_count > 2:
            return False
        
        # Furniture term check
        tokens = self.model.tokenize(name)
        furniture_tokens = [t for t in tokens if self.model.predict_category_membership(t.lemma_, "furniture")]
        if not furniture_tokens and not self.has_furniture_related_property(tag):
            return False
            
        return True
    
    def has_furniture_related_property(self, tag):
        """Check if element surroundings indicate furniture"""
        if not tag:
            return False
            
        furniture_properties = ['width', 'height', 'depth', 'material', 'color', 'dimensions', 'size', 'weight', 'style', 'finish', 'design', 'shape', 'pattern', 'texture', 'price', 'brand', 'manufacturer', 'assembly', 'features', 'warranty', 'care instructions']
        nearby_text = ' '.join(t.get_text().lower() for t in tag.find_all(['span', 'div', 'p'], limit=5))
        
        return any(prop in nearby_text for prop in furniture_properties)