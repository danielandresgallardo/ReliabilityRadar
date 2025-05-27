import os
import json
import re
from collections import defaultdict
from tqdm import tqdm

# Paths
PREPROCESSED_DIR = "data/preprocessed_data"
CAR_DATA_PATH = "data/car_data.json"

# Load car brand-model dictionary
with open(CAR_DATA_PATH, "r", encoding="utf-8") as f:
    car_data = json.load(f)

# Build lowercase (brand, model) pairs for easy matching
brand_model_pairs = []
for brand, models in car_data["brands"].items():
    for model in models:
        brand_model_pairs.append((brand.lower(), model.lower()))

# Compile a regex pattern to find brand+model mentions
def build_pattern(brand, model):
    brand_escaped = re.escape(brand)
    model_escaped = re.escape(model)
    return re.compile(rf"\b{brand_escaped}\s+{model_escaped}\b", re.IGNORECASE)

brand_model_patterns = {
    (brand, model): build_pattern(brand, model) for brand, model in brand_model_pairs
}

# Count posts containing brand-model mentions
brand_model_counts = defaultdict(int)

# Process all JSON files in preprocessed_data/
for filename in tqdm(os.listdir(PREPROCESSED_DIR), desc="Processing files"):
    if filename.endswith(".json"):
        with open(os.path.join(PREPROCESSED_DIR, filename), "r", encoding="utf-8") as f:
            posts = json.load(f)

        for post in posts:
            text_blobs = []

            # Collect all text from the post and its comments
            if post.get("title"):
                text_blobs.append(post["title"])
            if post.get("selftext"):
                text_blobs.append(post["selftext"])
            if "comments" in post:
                for comment in post["comments"]:
                    text_blobs.append(comment.get("body", ""))

            full_text = " ".join(text_blobs).lower()

            # Check if any brand-model pair appears in the full text
            for (brand, model), pattern in brand_model_patterns.items():
                if pattern.search(full_text):
                    brand_model_counts[(brand, model)] += 1
                    break  # Count only once per post

# Save the result to CSV
import pandas as pd

df = pd.DataFrame(
    [(brand.title(), model.title(), count) for (brand, model), count in brand_model_counts.items()],
    columns=["Brand", "Model", "Post Count"]
)

df.sort_values(by="Post Count", ascending=False, inplace=True)
df.to_csv("brand_model_post_counts.csv", index=False)

print("✅ Saved brand_model_post_counts.csv")