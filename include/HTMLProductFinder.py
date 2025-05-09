from include.DebugHelper import DebugHelper, time_func


class HTMLProductFinder:
    def __init__(self, nlp_model, validator, structured_product_helper):
        """Инициализация с моделями NLP, валидатором и текстовым процессором."""
        DebugHelper.log("Initializing HTMLProductFinder", self.__class__.__qualname__)
        self.nlp_model = nlp_model
        self.validator = validator
        self.structured_product_helper = structured_product_helper
    

    @time_func()
    def find_products_dumb(self, soup):
        result = []
        
        # Функция для фильтрации элементов по классам
        def class_filter(tag):
            if not tag.has_attr('class'):
                return False
            classes = ' '.join(tag['class']).lower()
            # Ищем элементы, содержащие 'product' + 'title'/'name' или их комбинации
            return ('product' in classes and ('title' in classes or 'name' in classes)) or \
                ('title' in classes or 'name' in classes)  # Расширенный вариант
        
        # Поиск всех подходящих элементов
        elements = soup.find_all(class_filter)
        
        # Извлечение и проверка текста
        for element in elements:
            text = element.get_text(strip=True)
            if self.validator.is_valid_product_name(text, element):
                result.append({"name": text})
        
        return result

    @time_func()
    def find_products(self, soup):
        """Основной метод поиска продуктов, возвращающий список словарей с атрибутами товаров."""
        DebugHelper.log("Finding products in HTML", self.__class__.__qualname__)
        return self.find_products_dumb(soup)