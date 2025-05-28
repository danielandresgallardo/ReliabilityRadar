import json
from pathlib import Path

# Load file
with open("data/car_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

brands = data.get("brands", {})

# Count brands and models
num_brands = len(brands)
num_models = sum(len(models) for models in brands.values())

print(f"Number of car brands: {num_brands}")
print(f"Total number of car models: {num_models}")