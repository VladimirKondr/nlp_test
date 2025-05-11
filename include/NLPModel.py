from functools import lru_cache
import spacy
from nltk.corpus import wordnet as wn


class NLPModel:
    def __init__(self):
        try:
            self.model = spacy.load("en_core_web_sm")
        except Exception as e:
            raise RuntimeError(f"Error loading SpaCy model: {e}")

    @lru_cache(maxsize=1000)
    def tokenize(self, text: str) -> list:
        """Tokenize text into words."""
        return self.model(text)

    @lru_cache(maxsize=1000)
    def predict_category_membership(self, word: str, category: str) -> bool:
        """Check if a word belongs to a category using WordNet."""
        word_synsets = self._get_synsets(word)
        category_synsets = self._get_synsets(category)

        if not word_synsets or not category_synsets:
            return False

        if self._is_exact_match(word, category_synsets):
            return False

        return self._is_hyponym(word_synsets, category_synsets)

    def _get_synsets(self, term: str):
        """Retrieve synsets for a given term."""
        try:
            return wn.synsets(term)
        except Exception as e:
            raise RuntimeError(f"Error accessing WordNet for term '{term}': {e}")

    def _is_exact_match(self, word: str, category_synsets) -> bool:
        """Check if the word matches the category or its synonyms."""
        category_lemmas = set()
        for syn in category_synsets:
            category_lemmas.update([lemma.name().lower() for lemma in syn.lemmas()])

        return word.lower() in category_lemmas

    def _is_hyponym(self, word_synsets, category_synsets) -> bool:
        """Check if the word is a hyponym of the category."""
        for word_syn in word_synsets:
            for hypernym_path in word_syn.hypernym_paths():
                for category_syn in category_synsets:
                    if category_syn in hypernym_path:
                        return True
        return False