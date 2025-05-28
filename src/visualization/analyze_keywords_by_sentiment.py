import os
import json
from pathlib import Path
from collections import defaultdict, Counter
import matplotlib.pyplot as plt

# Constants
SENTIMENT_DIR = Path("data/sentiment_analysis")
CAR_DATA_PATH = Path("data/car_data.json")
TOP_N = 10

# Input
brand_input = input("Enter car brand: ").strip().lower()
model_input = input("Enter model (leave blank to include all models): ").strip().lower() or None

# Track keywords by sentiment
keywords_by_sentiment = {
    "positive": Counter(),
    "neutral": Counter(),
    "negative": Counter()
}

# Load known car brand/model names
with open(CAR_DATA_PATH, "r", encoding="utf-8") as f:
    car_data = json.load(f)

brand_names = set(brand.lower() for brand in car_data.get("brands", {}))
model_names = set(model.lower() for models in car_data.get("brands", {}).values() for model in models)

# Words to exclude manually
MANUAL_EXCLUDES = {"car", "im", "dont", "get", "want", "would", "lol", "yeah", "oh", "like", "thing", "know"}

def extract_keywords_by_sentiment(section):
    """Extract tokens grouped by sentiment for matched brand/model in one section (title/selftext/comment)."""
    if not section or "sentiment" not in section:
        return

    token_lists = section["sentiment"].get("sentence_sentiments", [])
    ner_lists = section.get("ner_entities", [])
    
    for sent_idx, (sent_data, ner_data) in enumerate(zip(token_lists, ner_lists)):
        sentiment_category = sent_data.get("category")
        sentence_tokens = sent_data.get("sentence", "").split()

        if not sentiment_category or not sentence_tokens:
            continue

        mentioned_brand = False
        mentioned_model = not model_input  # If model not specified, allow all

        for entity in ner_data:
            entity_word = entity.get("word", "").lower()
            entity_type = entity.get("entity_group", "")

            if entity_type == "CAR_BRAND" and entity_word == brand_input:
                mentioned_brand = True
            if model_input and entity_type == "CAR_MODEL" and entity_word == model_input:
                mentioned_model = True

        if mentioned_brand and mentioned_model:
            # Exclude known brand/model words and other irrelevant tokens
            for token in sentence_tokens:
                token_lower = token.lower()
                if (
                    token_lower not in brand_names and
                    token_lower not in model_names and
                    token_lower not in MANUAL_EXCLUDES and
                    len(token_lower) > 2 and
                    not token_lower.isdigit()
                ):
                    keywords_by_sentiment[sentiment_category][token_lower] += 1

# Process all files
for file in SENTIMENT_DIR.glob("*.json"):
    with open(file, "r", encoding="utf-8") as f:
        posts = json.load(f)
        for post in posts:
            extract_keywords_by_sentiment(post.get("title_sentiment"))
            extract_keywords_by_sentiment(post.get("selftext_sentiment"))
            for comment in post.get("comments_sentiment", []):
                extract_keywords_by_sentiment(comment)

# Plot separate figure for each sentiment, sorted by frequency
output_dir = Path("data/visualizations/keywords") / brand_input.lower()
output_dir.mkdir(parents=True, exist_ok=True)

for sentiment, color in [("positive", "green"), ("neutral", "gray"), ("negative", "red")]:
    counter = keywords_by_sentiment[sentiment]
    if not counter:
        print(f"No keywords found for sentiment: {sentiment}")
        continue

    keywords, counts = zip(*counter.most_common(TOP_N))
    plt.figure(figsize=(8, 5))
    plt.barh(keywords[::-1], counts[::-1], color=color)
    plt.xlabel("Mentions")
    plt.title(f"{sentiment.capitalize()} Keywords\nBrand: {brand_input.title()}" + (f", Model: {model_input.title()}" if model_input else ""))
    plt.tight_layout()

    filename = f"keywords_{sentiment}_{brand_input}" + (f"_{model_input}" if model_input else "") + ".png"
    plt.savefig(output_dir / filename)
    plt.show()

    print(f"Saved: {output_dir / filename}")

# Save raw keyword data as JSON
summary_json = {
    sentiment: keywords_by_sentiment[sentiment].most_common(TOP_N)
    for sentiment in keywords_by_sentiment
}
json_filename = f"keywords_summary_{brand_input}" + (f"_{model_input}" if model_input else "") + ".json"
with open(output_dir / json_filename, "w", encoding="utf-8") as f:
    json.dump(summary_json, f, indent=2)
print(f"Saved keywords JSON: {output_dir / json_filename}")