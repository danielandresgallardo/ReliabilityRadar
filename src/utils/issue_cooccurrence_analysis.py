import os
import json
from pathlib import Path
from collections import Counter, defaultdict
from itertools import combinations

# === Config ===
brand = input("Enter car brand (e.g., toyota): ").strip().lower()
model = input("Enter car model (leave blank for whole brand): ").strip().lower()

INPUT_DIR = Path("data/preprocessed_data")
OUTPUT_DIR = Path(f"data/issue_analysis/{brand}")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PROBLEM_KEYWORDS = {
    "stall", "leak", "fail", "noise", "noisy", "grind", "overheat", "jerk",
    "won't start", "not starting", "dies", "check engine", "misfire",
    "vibration", "rattle", "burning", "smell", "warning light", "drain", "hard shift"
}

single_keywords = {kw for kw in PROBLEM_KEYWORDS if " " not in kw}
multi_keywords = {kw for kw in PROBLEM_KEYWORDS if " " in kw}

def contains_brand_model(entities):
    found_brand = False
    found_model = not model
    for sentence_entities in entities:
        for ent in sentence_entities:
            if ent.get("entity_group") == "CAR_BRAND" and ent.get("word", "").lower() == brand:
                found_brand = True
            if model and ent.get("entity_group") == "CAR_MODEL" and ent.get("word", "").lower() == model:
                found_model = True
    return found_brand and found_model

def find_issues_in_tokens(tokens):
    found = set()
    joined = " ".join(tokens)
    # check multi-word keywords
    for phrase in multi_keywords:
        if phrase in joined:
            found.add(phrase)
    # check single-word keywords
    for token in tokens:
        if token in single_keywords:
            found.add(token)
    return found

cooccurrence_counter = Counter()

def process_post(post):
    if not (
        contains_brand_model(post.get("preprocessed_title", {}).get("ner_entities", [])) or
        contains_brand_model(post.get("preprocessed_selftext", {}).get("ner_entities", [])) or
        any(contains_brand_model(comment.get("preprocessed_body", {}).get("ner_entities", [])) for comment in post.get("comments", []))
    ):
        return

    all_sections = [
        post.get("preprocessed_title", {}).get("cleaned_sentences_tokens", []),
        post.get("preprocessed_selftext", {}).get("cleaned_sentences_tokens", []),
    ]
    for comment in post.get("comments", []):
        all_sections.append(comment.get("preprocessed_body", {}).get("cleaned_sentences_tokens", []))

    for section in all_sections:
        for tokens in section:
            issues_found = find_issues_in_tokens(tokens)
            # Count all pairs of co-occurring issues
            for issue_pair in combinations(sorted(issues_found), 2):
                cooccurrence_counter[issue_pair] += 1

# === Run on all preprocessed files ===
for file in INPUT_DIR.glob("*.json"):
    with open(file, "r", encoding="utf-8") as f:
        posts = json.load(f)
        for post in posts:
            process_post(post)

# === Save co-occurrence counts ===
output_file = OUTPUT_DIR / (f"{model if model else 'all'}_issue_cooccurrences.json")
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(cooccurrence_counter.most_common(), f, indent=2)

print(f"✅ Saved issue co-occurrence counts to {output_file}")