import re
import string
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk

# Download necessary NLTK data once
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')  # For WordNet lemmatizer support

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def clean_text(text):
    text = text.lower()
    # Remove standalone numbers of 1-3 digits (surrounded by spaces/punctuation), keep numbers attached to words/hyphens
    text = re.sub(r'(?<![\w-])\b\d{1,3}\b(?![\w-])', '', text)
    # Remove em dash and any spaces around it
    text = re.sub(r'\s*—\s*', ' ', text)
    # Remove ASCII apostrophes and curly right single quotes
    text = text.replace("'", "").replace("’", "")
    # Remove punctuation except hyphens between alphanumeric characters
    text = re.sub(rf"[{re.escape(string.punctuation.replace('-', ''))}]", " ", text)
    # Remove standalone hyphens not between word characters
    text = re.sub(r'(?<!\w)-(?!\w)', ' ', text)
    # Normalize spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def preprocess_sentences(text):
    sentences = sent_tokenize(text)  # Split text into sentences
    cleaned_tokenized_sentences = []
    for sentence in sentences:
        cleaned = clean_text(sentence)
        tokens = word_tokenize(cleaned)
        # Remove stopwords
        tokens = [token for token in tokens if token not in stop_words]
        # Lemmatize tokens
        tokens = [lemmatizer.lemmatize(token) for token in tokens]
        cleaned_tokenized_sentences.append(tokens)
    return cleaned_tokenized_sentences

# Example usage
sample_text = ("I just bought a 2018 Toyota Camry for $19,500, but I’m already noticing some problems. "
               "The transmission feels jerky at low speeds, and there’s a weird noise when I brake. "
               "My old 2008 Honda Civic (which had 175,000 miles) never gave me this much trouble! "
               "A mechanic quoted me $1,200 to replace the brake pads and rotors. Is that normal? "
               "Also, someone recommended switching to synthetic oil — should I do that now or wait until the next 5,000-mile service? "
               "For comparison, a friend picked up a 2020 Ford F-150 with 32,000 miles for just $28,000 — no issues so far. "
               "Meanwhile, my brother’s 2012 BMW 328i keeps having check engine lights pop up. Thoughts?")

cleaned_tokenized_sentences = preprocess_sentences(sample_text)
for i, tokens in enumerate(cleaned_tokenized_sentences, 1):
    print(f"Sentence {i} tokens: {tokens}")