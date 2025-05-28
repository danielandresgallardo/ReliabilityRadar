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

# Calculate positive sentiment ratio
df["positive_ratio"] = df["positive"] / df["total"]

# Filter top 10 by positive sentiment ratio
df_top_positive = df.sort_values(by="positive_ratio", ascending=False).head(10)

# Save data to JSON
output_data = df_top_positive[["negative", "neutral", "positive", "total", "positive_ratio"]].to_dict(orient="index")
output_path = Path("data/visualizations")
output_path.mkdir(parents=True, exist_ok=True)
json_file = output_path / "top_positive_sentiment_brands_data.json"
with open(json_file, "w", encoding="utf-8") as f:
    json.dump(output_data, f, indent=2)

# Plot horizontal bar chart
df_top_positive[["positive_ratio"]].plot(
    kind="barh",
    figsize=(10, 6),
    color="green",
    legend=False
)

plt.xlabel("Positive Sentiment Ratio")
plt.title("Top 10 Car Brands by Positive Sentiment Ratio")
plt.tight_layout()

# Save plot image
img_file = output_path / "top_positive_sentiment_brands.png"
plt.savefig(img_file)
plt.show()

print(f"✅ Positive sentiment ratio chart saved to {img_file}")
print(f"✅ Data saved to {json_file}")