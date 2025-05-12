import os
import requests
import zipfile
import io
import nltk
import spacy


import os
import io
import zipfile
import requests
import nltk
import spacy

nltk_data_dir = os.path.join(os.getcwd(), "nltk_data")
corpora_dir = os.path.join(nltk_data_dir, "corpora")
wordnet_dir = os.path.join(corpora_dir, "wordnet")
omw_dir = os.path.join(corpora_dir, "omw-1.4")
spacy_model_name = "en_core_web_md"

os.makedirs(corpora_dir, exist_ok=True)

if not os.path.exists(wordnet_dir):
    print("Downloading WordNet...")
    wordnet_url = "https://github.com/nltk/nltk_data/raw/gh-pages/packages/corpora/wordnet.zip"
    response = requests.get(wordnet_url, stream=True)
    if response.status_code == 200:
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            z.extractall(corpora_dir)
        print(f"WordNet installed to {wordnet_dir}")
    else:
        print(f"Failed to download WordNet. Status: {response.status_code}")

if not os.path.exists(omw_dir):
    print("Downloading OMW-1.4...")
    omw_url = "https://github.com/nltk/nltk_data/raw/gh-pages/packages/corpora/omw-1.4.zip"
    response = requests.get(omw_url, stream=True)
    if response.status_code == 200:
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            z.extractall(corpora_dir)
        print(f"OMW-1.4 installed to {omw_dir}")
    else:
        print(f"Failed to download OMW-1.4. Status: {response.status_code}")

nltk.data.path.append(nltk_data_dir)

try:
    spacy.load(spacy_model_name)
    print(f"spaCy model '{spacy_model_name}' уже установлен")
except OSError:
    print(f"Установка spaCy модели '{spacy_model_name}'...")
    os.system(f"python -m spacy download {spacy_model_name}")

print("\nВсе зависимости успешно установлены!")
