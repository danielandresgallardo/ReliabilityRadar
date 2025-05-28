import os
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd

# Path to preprocessed data
DATA_DIR = Path("data/preprocessed_data")

# Mention tracker: {("brand", "month"): count}
mention_counts = defaultdict(int)

def extract_brands(ner_entities):
    brands = set()
    for sentence_entities in ner_entities:
        for ent in sentence_entities:
            if ent.get("entity_group") == "CAR_BRAND":
                brands.add(ent.get("word", "").lower())
    return brands

def get_month(utc_ts):
    try:
        return datetime.utcfromtimestamp(utc_ts).strftime("%Y-%m")
    except Exception:
        return None

def process_post(post):
    post_time = get_month(post.get("created_utc", 0))
    if post_time:
        for brand in extract_brands(post.get("preprocessed_title", {}).get("ner_entities", [])):
            mention_counts[(brand, post_time)] += 1
        for brand in extract_brands(post.get("preprocessed_selftext", {}).get("ner_entities", [])):
            mention_counts[(brand, post_time)] += 1

    for comment in post.get("comments", []):
        comment_time = get_month(comment.get("created_utc", 0))
        if comment_time:
            for brand in extract_brands(comment.get("preprocessed_body", {}).get("ner_entities", [])):
                mention_counts[(brand, comment_time)] += 1

# Load all files
for file in DATA_DIR.glob("*.json"):
    print(f"📥 Processing {file.name}")
    with open(file, "r", encoding="utf-8") as f:
        posts = json.load(f)
        for post in posts:
            process_post(post)

# Create DataFrame
records = [
    {"brand": brand, "month": month, "count": count}
    for (brand, month), count in mention_counts.items()
]
df = pd.DataFrame(records)

# Pivot to get monthly time series for top brands
top_brands = df.groupby("brand")["count"].sum().nlargest(5).index
df = df[df["brand"].isin(top_brands)]

pivot_df = df.pivot_table(index="month", columns="brand", values="count", aggfunc="sum").fillna(0)
pivot_df = pivot_df.sort_index()  # Sort by month

# Plot
pivot_df.plot(figsize=(12, 6), marker="o")
plt.title("Mentions Over Time for Top 5 Car Brands")
plt.xlabel("Month")
plt.ylabel("Mentions")
plt.grid(True)
plt.tight_layout()

# Save chart
output_path = Path("data/visualizations")
output_path.mkdir(parents=True, exist_ok=True)
plt.savefig(output_path / "mentions_over_time.png")
plt.show()

print("✅ Saved chart to data/visualizations/mentions_over_time.png")