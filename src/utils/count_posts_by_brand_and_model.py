import os
import json
import re
from collections import defaultdict
import pandas as pd
from tqdm import tqdm

# Paths
PREPROCESSED_DIR = "data/preprocessed_data"
CAR_DATA_PATH = "data/car_data.json"

# Load car brand-model dictionary
with open(CAR_DATA_PATH, "r", encoding="utf-8") as f:
    car_data = json.load(f)

# Build lowercase brand/model lists
all_brands = set()
all_models = set()

for brand, models in car_data["brands"].items():
    brand_lc = brand.lower()
    all_brands.add(brand_lc)
    for model in models:
        model_lc = model.lower()
        all_models.add(model_lc)

# Compile regex patterns
brand_patterns = {brand: re.compile(rf"\b{re.escape(brand)}\b", re.IGNORECASE) for brand in all_brands}
model_patterns = {model: re.compile(rf"\b{re.escape(model)}\b", re.IGNORECASE) for model in all_models}

# Initialize counters
brand_post_counts = defaultdict(int)
brand_comment_counts = defaultdict(int)
model_post_counts = defaultdict(int)
model_comment_counts = defaultdict(int)

# Process each JSON file in the preprocessed directory
for filename in tqdm(os.listdir(PREPROCESSED_DIR), desc="Processing files"):
    if not filename.endswith(".json"):
        continue
    with open(os.path.join(PREPROCESSED_DIR, filename), "r", encoding="utf-8") as f:
        posts = json.load(f)

    for post in posts:
        post_text = f"{post.get('title', '')} {post.get('selftext', '')}".lower()
        comments = post.get("comments", [])

        # Set to track which brands/models are mentioned in this post
        matched_brands_post = set()
        matched_models_post = set()

        # Check brand mentions in post
        for brand, pattern in brand_patterns.items():
            if pattern.search(post_text):
                matched_brands_post.add(brand)

        # Check model mentions in post
        for model, pattern in model_patterns.items():
            if pattern.search(post_text):
                matched_models_post.add(model)

        for brand in matched_brands_post:
            brand_post_counts[brand] += 1
        for model in matched_models_post:
            model_post_counts[model] += 1

        # Count mentions in individual comments
        for comment in comments:
            body = comment.get("body", "").lower()
            matched_brands_comment = set()
            matched_models_comment = set()

            for brand, pattern in brand_patterns.items():
                if pattern.search(body):
                    matched_brands_comment.add(brand)
            for model, pattern in model_patterns.items():
                if pattern.search(body):
                    matched_models_comment.add(model)

            for brand in matched_brands_comment:
                brand_comment_counts[brand] += 1
            for model in matched_models_comment:
                model_comment_counts[model] += 1

# Save to CSVs
def save_counts_to_csv(counts_dict, label, filename):
    df = pd.DataFrame(
        [(key.title(), count) for key, count in counts_dict.items()],
        columns=[label, "Mentions"]
    ).sort_values(by="Mentions", ascending=False)
    df.to_csv(filename, index=False)

save_counts_to_csv(brand_post_counts, "Brand", "brand_post_counts.csv")
save_counts_to_csv(brand_comment_counts, "Brand", "brand_comment_counts.csv")
save_counts_to_csv(model_post_counts, "Model", "model_post_counts.csv")
save_counts_to_csv(model_comment_counts, "Model", "model_comment_counts.csv")

print("✅ Saved brand/model mention stats in posts and comments.")
