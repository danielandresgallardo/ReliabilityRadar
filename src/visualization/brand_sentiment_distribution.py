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

def extract_brands(ner_entities):
    brands = set()
    for sentence_entities in ner_entities:
        for ent in sentence_entities:
            if ent.get("entity_group") == "CAR_BRAND":
                brands.add(ent["word"].lower())
    return brands

def process_post(post):
    # Sentiment sections
    sections = [
        ("title_sentiment", post.get("title_sentiment")),
        ("selftext_sentiment", post.get("selftext_sentiment")),
    ]

    for section_key, section in sections:
        if not section:
            continue
        sentiment = section.get("sentiment", {}).get("aggregate_sentiment", {}).get("overall_category")
        entities = section.get("ner_entities", [])
        for brand in extract_brands(entities):
            brand_sentiments[brand][sentiment] += 1

    for comment in post.get("comments_sentiment", []):
        sentiment = comment.get("sentiment", {}).get("aggregate_sentiment", {}).get("overall_category")
        entities = comment.get("ner_entities", [])
        for brand in extract_brands(entities):
            brand_sentiments[brand][sentiment] += 1

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
df = df.sort_values(by="total", ascending=False).head(10)  # Top 10 brands

# Plot stacked bar chart
df[["positive", "neutral", "negative"]].plot(
    kind="barh",
    stacked=True,
    figsize=(10, 6),
    color=["green", "gray", "red"]
)

plt.xlabel("Mentions")
plt.title("Sentiment Distribution by Top 10 Car Brands")
plt.tight_layout()

# Save image
output_path = Path("data/visualizations")
output_path.mkdir(parents=True, exist_ok=True)
plt.savefig(output_path / "brand_sentiment_distribution.png")
plt.show()

print("✅ Sentiment distribution chart saved to data/visualizations/brand_sentiment_distribution.png")