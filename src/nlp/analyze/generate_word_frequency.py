import os
import json
from pathlib import Path
from collections import Counter
import pandas as pd

# Paths
INPUT_DIR = Path("data/preprocessed_data")
OUTPUT_FILE = Path("data/analysis/word_frequencies.csv")
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

word_counter = Counter()

def process_tokens(token_lists):
    for sentence_tokens in token_lists:
        for token in sentence_tokens:
            word_counter[token] += 1

def process_post(post):
    process_tokens(post.get("preprocessed_title", {}).get("cleaned_sentences_tokens", []))
    process_tokens(post.get("preprocessed_selftext", {}).get("cleaned_sentences_tokens", []))

    for comment in post.get("comments", []):
        process_tokens(comment.get("preprocessed_body", {}).get("cleaned_sentences_tokens", []))

# Iterate over all files
for file in INPUT_DIR.glob("*.json"):
    print(f"📥 Processing {file.name}")
    with open(file, "r", encoding="utf-8") as f:
        posts = json.load(f)
        for post in posts:
            process_post(post)

# Convert to DataFrame
df = pd.DataFrame(word_counter.items(), columns=["word", "frequency"])
df = df.sort_values(by="frequency", ascending=False)

# Save
df.to_csv(OUTPUT_FILE, index=False)
print(f"✅ Word frequency table saved to {OUTPUT_FILE}")