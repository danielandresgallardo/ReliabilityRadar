import json
from pathlib import Path

DATA_DIR = Path("data/preprocessed_data")

unique_brands = set()
unique_models = set()

for file in DATA_DIR.glob("*.json"):
    with open(file, "r", encoding="utf-8") as f:
        posts = json.load(f)
        for post in posts:
            # Collect brands and models from title and selftext ner_entities
            for section in ["preprocessed_title", "preprocessed_selftext"]:
                ner_entities = post.get(section, {}).get("ner_entities", [])
                for sentence_entities in ner_entities:
                    for ent in sentence_entities:
                        if ent.get("entity_group") == "CAR_BRAND":
                            unique_brands.add(ent.get("word", "").lower())
                        elif ent.get("entity_group") == "CAR_MODEL":
                            unique_models.add(ent.get("word", "").lower())

            # Collect from comments ner_entities
            for comment in post.get("comments", []):
                ner_entities = comment.get("preprocessed_body", {}).get("ner_entities", [])
                for sentence_entities in ner_entities:
                    for ent in sentence_entities:
                        if ent.get("entity_group") == "CAR_BRAND":
                            unique_brands.add(ent.get("word", "").lower())
                        elif ent.get("entity_group") == "CAR_MODEL":
                            unique_models.add(ent.get("word", "").lower())

print(f"Number of unique car brands detected: {len(unique_brands)}")
print(f"Number of unique car models detected: {len(unique_models)}")