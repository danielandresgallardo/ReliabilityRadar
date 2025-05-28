import os
import json
from pathlib import Path
from collections import defaultdict, Counter
import matplotlib.pyplot as plt

# Input directories
DATA_DIR = Path("data/preprocessed_data")
CAR_DATA_FILE = Path("data/car_data.json") # Path to your car_data.json

# {brand: Counter({model: count})}
brand_model_counts = defaultdict(Counter)

# Load car_data.json for validation
def load_car_data(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        car_data = json.load(f)
    # Create a lookup structure: {brand: set_of_models}
    # Convert models to lowercase for case-insensitive matching
    car_model_lookup = {
        brand.lower(): {model.lower() for model in models_list}
        for brand, models_list in car_data.get("brands", {}).items()
    }
    return car_model_lookup

car_model_lookup = load_car_data(CAR_DATA_FILE)

def extract_brand_model_pairs(ner_entities):
    brands_in_segment = []
    models_in_segment = []
    for entity in ner_entities:
        for ent in entity: # Flatten the list of lists if necessary
            label = ent.get("entity_group")
            word = ent.get("word", "").lower()
            if label == "CAR_BRAND":
                # Only add brand if it's in our lookup (i.e., a known brand)
                if word in car_model_lookup:
                    brands_in_segment.append(word)
            elif label == "CAR_MODEL":
                models_in_segment.append(word)

    pairs = []
    # Iterate through identified models and try to link them to brands
    for model in models_in_segment:
        found_match = False
        # Prioritize brands mentioned closer to the model, or just check all available brands
        # We will try to link to any brand mentioned in the segment that has this model
        for brand in brands_in_segment:
            if brand in car_model_lookup and model in car_model_lookup[brand]:
                pairs.append((brand, model))
                found_match = True
                break # Found a valid brand for this model, move to next model
        # If no brand found for the model within the segment, or if it's a generic term, discard it
        # This implicitly handles cases like "air" if "air" is not a valid model for any identified brand
    return pairs


def process_file(file):
    with open(file, "r", encoding="utf-8") as f:
        posts = json.load(f)
        for post in posts:
            # Extract from title and selftext
            for section in ["preprocessed_title", "preprocessed_selftext"]:
                ner_entities = post.get(section, {}).get("ner_entities", [])
                # Ensure ner_entities is always a list of lists or empty list
                if not isinstance(ner_entities, list) or not all(isinstance(item, list) for item in ner_entities):
                    # Attempt to flatten if it's a single list of dicts, or skip if invalid
                    if isinstance(ner_entities, list) and all(isinstance(item, dict) for item in ner_entities):
                        ner_entities = [ner_entities] # Wrap it to match expected format
                    else:
                        continue # Skip if format is not as expected

                for brand, model in extract_brand_model_pairs(ner_entities):
                    brand_model_counts[brand][model] += 1

            # Extract from comments
            for comment in post.get("comments", []):
                ner_entities = comment.get("preprocessed_body", {}).get("ner_entities", [])
                # Ensure ner_entities is always a list of lists or empty list
                if not isinstance(ner_entities, list) or not all(isinstance(item, list) for item in ner_entities):
                    if isinstance(ner_entities, list) and all(isinstance(item, dict) for item in ner_entities):
                        ner_entities = [ner_entities]
                    else:
                        continue
                for brand, model in extract_brand_model_pairs(ner_entities):
                    brand_model_counts[brand][model] += 1

# Process all JSON files
for file in DATA_DIR.glob("*.json"):
    print(f"📥 Processing {file.name}")
    process_file(file)

# Plot for top 3 brands
top_brands = sorted(brand_model_counts.keys(), key=lambda b: sum(brand_model_counts[b].values()), reverse=True)[:3]

output_dir = Path("data/visualizations")
output_dir.mkdir(parents=True, exist_ok=True)

for brand in top_brands:
    # Filter out models that might have slipped through or are not in the lookup for this brand
    # (Though the new extract_brand_model_pairs should prevent this, it's a good safety)
    valid_models_for_brand = car_model_lookup.get(brand, set())
    filtered_models = {model: count for model, count in brand_model_counts[brand].items() if model in valid_models_for_brand}

    if not filtered_models:
        print(f"Skipping plot for '{brand.title()}' as no valid models were found.")
        continue

    models, counts = zip(*Counter(filtered_models).most_common(5))
    plt.figure(figsize=(8, 5))
    plt.barh(models[::-1], counts[::-1], color="orange")
    plt.title(f"Top Mentioned Models for '{brand.title()}'")
    plt.xlabel("Mentions")
    plt.tight_layout()
    out_file = output_dir / f"top_models_{brand}.png"
    plt.savefig(out_file)
    print(f"✅ Saved: {out_file}")
    plt.close()

# You can add a check here to see if "accord" or "air" are still being counted for Toyota
print("\n--- Validation Check ---")
toyota_models = brand_model_counts.get("toyota", {})
print(f"Toyota 'accord' mentions: {toyota_models.get('accord', 0)}")
print(f"Toyota 'air' mentions: {toyota_models.get('air', 0)}")
print("--- End Validation Check ---")