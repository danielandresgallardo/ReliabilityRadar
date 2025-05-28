import re
import string
import json
from pathlib import Path
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk

from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline

# Download necessary NLTK data once
# nltk.download('punkt')
# nltk.download('stopwords')
# nltk.download('wordnet')
# nltk.download('omw-1.4')

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

# Load pretrained BERT NER model and tokenizer
ner_model_name = "dslim/bert-base-NER"
tokenizer = AutoTokenizer.from_pretrained(ner_model_name)
model = AutoModelForTokenClassification.from_pretrained(ner_model_name)
ner_pipeline = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")

# Load car brands and models dictionary for augmentation
car_data_path = Path("data/car_data.json")
with open(car_data_path, "r", encoding="utf-8") as f:
    car_data = json.load(f)

brands = car_data.get("brands", {})
brand_names = set(brand.lower() for brand in brands.keys())
model_names = set()
for models_list in brands.values():
    for model in models_list:
        model_names.add(model.lower())

# Set of ambiguous tokens to exclude unless strong context found
AMBIGUOUS_TOKENS = {
    "i", "is", "go", "do", "on", "at", "it", "me", "my", "no", "up",
    "a", "an", "to", "of", "in", "so", "we", "he", "she", "us"
}

ALWAYS_EXCLUDE = {"i", "is"}

def clean_text(text: str) -> str:
    # Lowercase the text
    text = text.lower()

    # Remove standalone 1- to 3-digit numbers (not part of words or hyphenated strings)
    text = re.sub(r'(?<![\w-])\b\d{1,3}\b(?![\w-])', '', text)

    # Replace em-dashes and isolated hyphens with a space
    text = re.sub(r'[—–]', ' ', text)                     # Covers em-dash and en-dash
    text = re.sub(r'(?<!\w)-(?!\w)', ' ', text)           # Remove isolated ASCII hyphens

    # Remove all punctuation (except hyphens between words)
    text = re.sub(rf"[{re.escape(string.punctuation.replace('-', ''))}]", " ", text)

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    return text

def is_valid_car_context(token: str, sentence: str, entity_group: str) -> bool:
    if token in AMBIGUOUS_TOKENS:
        window_size = 3
        words = sentence.lower().split()
        if token not in words:
            return False
        idxs = [i for i, w in enumerate(words) if w == token]
        for idx in idxs:
            start = max(0, idx - window_size)
            end = min(len(words), idx + window_size + 1)
            context_window = words[start:end]
            for w in context_window:
                if w.isdigit() and 1900 <= int(w) <= 2030:
                    return True
            if any(w in brand_names or w in model_names for w in context_window):
                return True
        return False
    return True

def fix_entity_group(ent, word: str) -> str:
    word_lower = word.lower()
    if word_lower in brand_names:
        return "CAR_BRAND"
    elif word_lower in model_names:
        return "CAR_MODEL"
    return ent.get("entity_group", "")

def find_car_entities(text: str):
    bert_entities = ner_pipeline(text)
    tokens = word_tokenize(text)
    
    for ent in bert_entities:
        ent["entity_group"] = fix_entity_group(ent, ent["word"])

    tokens_lower = [t.lower() for t in tokens]
    matched_brands = [t for t in tokens_lower if t in brand_names]
    matched_models = [t for t in tokens_lower if t in model_names]

    existing_words = set(ent['word'].lower() for ent in bert_entities)

    for brand in matched_brands:
        if brand not in existing_words:
            bert_entities.append({"word": brand, "entity_group": "CAR_BRAND", "score": 1.0})
            existing_words.add(brand)
    for model in matched_models:
        if model not in existing_words:
            bert_entities.append({"word": model, "entity_group": "CAR_MODEL", "score": 1.0})
            existing_words.add(model)

    filtered_entities = []
    for ent in bert_entities:
        token = ent['word'].lower()
        if token in ALWAYS_EXCLUDE:
            continue
        if token.startswith("##"):
            continue
        if len(token) <= 2 or token in AMBIGUOUS_TOKENS:
            if not is_valid_car_context(token, text, ent['entity_group']):
                continue
        if all(c in string.punctuation for c in token):
            continue
        if token.isdigit():
            continue
        filtered_entities.append(ent)

    return filtered_entities

def preprocess_sentences(text: str):
    sentences = sent_tokenize(text)
    cleaned_sentences_tokens = []
    ner_entities_per_sentence = []

    for sentence in sentences:
        cleaned = clean_text(sentence)
        tokens = word_tokenize(cleaned)
        tokens = [token for token in tokens if token not in stop_words]
        tokens = [lemmatizer.lemmatize(token) for token in tokens]

        if tokens:
            cleaned_sentences_tokens.append(tokens)
            entities = find_car_entities(sentence)
            ner_entities_per_sentence.append(entities)

    return {
        "cleaned_sentences_tokens": cleaned_sentences_tokens,
        "ner_entities": ner_entities_per_sentence
    }