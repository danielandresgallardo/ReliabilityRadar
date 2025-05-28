import os
import json
from pathlib import Path
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
import pandas as pd

# Path to sentiment analysis data
SENTIMENT_DIR = Path("data/sentiment_analysis")

# Collect brand sentiment counts
brand_sentiments = defaultdict(Counter)

def extract_brands_from_sentence(entities):
    return {ent["word"].lower() for ent in entities if ent.get("entity_group") == "CAR_BRAND"}

def process_section(sentiments, entities):
    # Match sentence sentiment to sentence NER entities
    for sent_data, ner_data in zip(sentiments, entities):
        sentiment = sent_data.get("category")
        brands = extract_brands_from_sentence(ner_data)
        for brand in brands:
            brand_sentiments[brand][sentiment] += 1

def process_post(post):
    # Process title
    title_data = post.get("title_sentiment", {})
    title_sentiments = title_data.get("sentiment", {}).get("sentence_sentiments", [])
    title_entities = title_data.get("ner_entities", [])
    process_section(title_sentiments, title_entities)

    # Process selftext
    selftext_data = post.get("selftext_sentiment", {})
    selftext_sentiments = selftext_data.get("sentiment", {}).get("sentence_sentiments", [])
    selftext_entities = selftext_data.get("ner_entities", [])
    process_section(selftext_sentiments, selftext_entities)

    # Process comments
    for comment in post.get("comments_sentiment", []):
        sentiments = comment.get("sentiment", {}).get("sentence_sentiments", [])
        entities = comment.get("ner_entities", [])
        process_section(sentiments, entities)

# Load all JSON files
for file in SENTIMENT_DIR.glob("*.json"):
    print(f"📥 Processing {file.name}")
    with open(file, "r", encoding="utf-8") as f:
        posts = json.load(f)
        for post in posts:
            process_post(post)

# Convert to DataFrame
df = pd.DataFrame(brand_sentiments).T.fillna(0).astype(int)
df["total"] = df.sum(axis=1)
df = df.sort_values(by="total", ascending=False).head(10)

# Plot stacked bar chart
df[["positive", "neutral", "negative"]].plot(
    kind="barh",
    stacked=True,
    figsize=(10, 6),
    color=["green", "gray", "red"]
)

plt.xlabel("Mentions")
plt.title("Sentence-Level Sentiment Distribution by Top 10 Car Brands")
plt.tight_layout()

# Save image
output_path = Path("data/visualizations")
output_path.mkdir(parents=True, exist_ok=True)
plt.savefig(output_path / "brand_sentiment_distribution_sentence_level.png")
plt.show()

print("✅ Sentence-level sentiment distribution chart saved to data/visualizations/brand_sentiment_distribution_sentence_level.png")