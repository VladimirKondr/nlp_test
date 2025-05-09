from functools import lru_cache
import spacy
from nltk.corpus import wordnet as wn


class NLPModel:
    def __init__(self):
        self.model = spacy.load("en_core_web_sm")
    
    @lru_cache(maxsize=1000)
    def tokenize(self, text: str) -> list:
        """Tokenize text into words"""
        return self.model(text)
    
    @lru_cache(maxsize=1000)
    def predict_category_membership(self, word: str, category: str) -> bool:
        """
        Проверяет, принадлежит ли слово к категории, используя WordNet.
        Возвращает True, если:
        - слово является гипонимом (более узким понятием) категории,
        - слово НЕ является самим названием категории или её синонимом.
        """
        word_synsets = wn.synsets(word)
        category_synsets = wn.synsets(category)
        
        # Если синсеты не найдены, возвращаем False
        if not word_synsets or not category_synsets:
            return False
        
        # Собираем все леммы (синонимы) категории для исключения
        category_lemmas = set()
        for syn in category_synsets:
            category_lemmas.update([lemma.name().lower() for lemma in syn.lemmas()])
        
        # Если слово совпадает с категорией или её синонимом, возвращаем False
        if word.lower() in category_lemmas:
            return False
        
        # Проверяем, есть ли у слова синсет, для которого категория является гиперонимом
        for word_syn in word_synsets:
            for hypernym_path in word_syn.hypernym_paths():
                for category_syn in category_synsets:
                    if category_syn in hypernym_path:
                        return True
        return False