from difflib import SequenceMatcher
from functools import lru_cache
import re
from typing import Any, Dict, List


class StructuredProductHelper:
    def __init__(self, nlp_model=None, validator=None, similarity_threshold=0.8):
        """
        Инициализирует helper для обработки продуктовых словарей
        
        Args:
            nlp_model: NLPModel для лингвистического анализа (опционально)
            validator: ProductValidator для валидации продуктов (опционально)
            similarity_threshold: Порог схожести для определения дубликатов
        """
        self.nlp_model = nlp_model
        self.validator = validator
        self.similarity_threshold = similarity_threshold
    
    def get_property_value(self, tag):
        """Helper method to extract value from a tag, handling both meta tags and text content."""
        if tag and tag.name == 'meta' and tag.get('content'):
            return tag.get('content').strip()
        elif tag:
            return tag.get_text(strip=True)
        return ''
        
    @lru_cache(maxsize=1000)
    def normalize_name(self, name: str) -> str:
        """Нормализует название продукта для сравнения"""
        if not name:
            return ""
        # Приведение к нижнему регистру
        result = name.lower()
        name = re.sub(r'\s*\|\s*.*$', '', name)
        name = re.sub(r'\s*(shop|buy|online|store|collection).*', '', name)
        name = re.sub(r'\s+', ' ', name)  # Normalize spaces
        name = name.strip('.,;:-| ')  # Strip common punctuation
        # Удаление специальных символов
        result = re.sub(r'[^\w\s]', '', result)
        # Удаление лишних пробелов
        result = re.sub(r'\s+', ' ', result).strip()
        doc = self.nlp_model.tokenize(result)
        return ' '.join([token.lemma_ for token in doc if not token.is_punct])
    
    @lru_cache(maxsize=1000)
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Вычисляет степень схожести между двумя строками"""
        # Используем SequenceMatcher для расчета сходства
        return SequenceMatcher(None, text1, text2).ratio()
    
    def are_duplicates(self, product1: Dict[str, Any], product2: Dict[str, Any]) -> bool:
        """Определяет, являются ли два продукта дубликатами"""
        # Если имена отсутствуют, это не дубликаты
        if not product1.get('name') or not product2.get('name'):
            return False
            
        name1 = self.normalize_name(product1['name'])
        name2 = self.normalize_name(product2['name'])
        
        # Точное совпадение
        if name1 == name2:
            return True
            
        # Высокая степень сходства
        similarity = self.calculate_similarity(name1, name2)
        if similarity >= self.similarity_threshold:
            return True
            
        # Проверка, является ли одно название подстрокой другого
        if name1 in name2 or name2 in name1:
            return True
                
        return False
    
    def merge_products(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Объединяет дубликаты продуктов, сохраняя наиболее полную информацию"""
        if not products:
            return []
            
        # Группируем дубликаты
        groups = []
        for product in products:
            # Ищем существующую группу для этого продукта
            found_group = False
            for group in groups:
                if any(self.are_duplicates(product, item) for item in group):
                    group.append(product)
                    found_group = True
                    break
                    
            # Если группа не найдена, создаем новую
            if not found_group:
                groups.append([product])
                
        # Выбираем лучший продукт из каждой группы
        result = []
        for group in groups:
            best_product = self.select_best_product(group)
            result.append(best_product)
            
        return result
    
    def select_best_product(self, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Выбирает лучший продукт из группы дубликатов"""
        if not products:
            return {}
        if len(products) == 1:
            return products[0]
            
        # Сортируем по уровню достоверности (confidence)
        sorted_products = sorted(products, key=lambda p: p.get('confidence', 0), reverse=True)
        
        # Берем продукт с наивысшим уровнем достоверности за основу
        best_product = sorted_products[0].copy()
        
        # Объединяем информацию из других продуктов, если она отсутствует в лучшем
        for product in sorted_products[1:]:
            for key, value in product.items():
                # Если поле отсутствует в лучшем продукте, добавляем его
                if key not in best_product and value:
                    best_product[key] = value
        return best_product

        


    
    def process_structured_data(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Возвращает список лучших уникальных продуктов
        
        Args:
            products: Список словарей с информацией о продуктах
            
        Returns:
            Список уникальных продуктов с наилучшей информацией
        """

        filtered_products = [p for p in products if p.get('name')]
        
        # Дополнительная валидация через validator, если доступен
        if self.validator:
            filtered_products = [p for p in filtered_products 
                               if self.validator.is_valid_product_name(p.get('name', ''))]
        
        # Объединяем дубликаты
        merged_products = self.merge_products(filtered_products)
        
        return merged_products