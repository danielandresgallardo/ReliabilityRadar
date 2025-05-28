import os
import json
from pathlib import Path
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from tqdm import tqdm

# Paths
SENTIMENT_DIR = Path("data/sentiment_analysis")
OUTPUT_PATH = Path("data/visualizations")
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

# Collect compound scores per brand
brand_scores = defaultdict(list)

def extract_brands(entities):
    return {ent["word"].lower() for ent in entities if ent.get("entity_group") == "CAR_BRAND"}

def process_section(sentiments, entities):
    for sent_data, ner_data in zip(sentiments, entities):
        compound = sent_data.get("scores", {}).get("compound")
        if compound is None:
            continue
        brands = extract_brands(ner_data)
        for brand in brands:
            brand_scores[brand].append(compound)

def process_post(post):
    title = post.get("title_sentiment", {})
    selftext = post.get("selftext_sentiment", {})
    process_section(
        title.get("sentiment", {}).get("sentence_sentiments", []),
        title.get("ner_entities", []),
    )
    process_section(
        selftext.get("sentiment", {}).get("sentence_sentiments", []),
        selftext.get("ner_entities", []),
    )
    for comment in post.get("comments_sentiment", []):
        process_section(
            comment.get("sentiment", {}).get("sentence_sentiments", []),
            comment.get("ner_entities", []),
        )

# Load and process all sentiment data
print("📊 Collecting sentiment scores...")
for file in tqdm(SENTIMENT_DIR.glob("*.json")):
    with open(file, "r", encoding="utf-8") as f:
        posts = json.load(f)
        for post in posts:
            process_post(post)

# Get top 10 brands by volume
top_brands = sorted(brand_scores.items(), key=lambda x: len(x[1]), reverse=True)[:10]

# Prepare DataFrame
records = []
for brand, scores in top_brands:
    for score in scores:
        records.append({"brand": brand, "compound": score})
df = pd.DataFrame(records)

# Plot violin chart
plt.figure(figsize=(12, 6))
sns.violinplot(data=df, x="brand", y="compound", palette="Set2", inner="quartile")
plt.title("Distribution of Sentence-Level Sentiment Scores by Car Brand")
plt.ylabel("VADER Compound Score")
plt.xlabel("Car Brand")
plt.ylim(-1, 1)
plt.xticks(rotation=45)
plt.tight_layout()

# Save and show
plot_path = OUTPUT_PATH / "violin_sentiment_distribution.png"
plt.savefig(plot_path)
plt.show()

print(f"✅ Violin plot saved to {plot_path}")