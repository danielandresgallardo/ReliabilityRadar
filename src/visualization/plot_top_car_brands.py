import os
import json
from pathlib import Path
from collections import Counter
import matplotlib.pyplot as plt

# Paths
DATA_DIR = Path("data/preprocessed_data")
OUTPUT_DIR = Path("outputs/plots")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Counter for car brands
brand_counter = Counter()

def extract_brands_from_entities(entities):
    for sentence_entities in entities:
        for ent in sentence_entities:
            if ent.get("entity_group") == "CAR_BRAND":
                brand = ent.get("word", "").lower()
                brand_counter[brand] += 1

# Process each file
for file in DATA_DIR.glob("*.json"):
    with open(file, "r", encoding="utf-8") as f:
        posts = json.load(f)
        for post in posts:
            extract_brands_from_entities(post.get("preprocessed_title", {}).get("ner_entities", []))
            extract_brands_from_entities(post.get("preprocessed_selftext", {}).get("ner_entities", []))
            for comment in post.get("comments", []):
                extract_brands_from_entities(comment.get("preprocessed_body", {}).get("ner_entities", []))

# Top 10 brands
top_brands = brand_counter.most_common(10)
brands, counts = zip(*top_brands)

# Plot
plt.figure(figsize=(10, 6))
plt.barh(brands[::-1], counts[::-1], color="steelblue")
plt.xlabel("Mentions")
plt.title("Top 10 Most Mentioned Car Brands")
plt.tight_layout()

# Save plot
plot_path = OUTPUT_DIR / "top_10_car_brands.png"
plt.savefig(plot_path)
print(f"✅ Saved plot to: {plot_path}")

plt.show()