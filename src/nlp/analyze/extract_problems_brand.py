import os
import json
from pathlib import Path
from collections import Counter
import matplotlib.pyplot as plt

# === Ask for input ===
brand = input("Enter car brand (e.g., toyota): ").strip().lower()
model = input("Enter car model (leave blank for whole brand): ").strip().lower()

# === Config ===
INPUT_DIR = Path("data/preprocessed_data")
OUTPUT_DIR = Path(f"data/issue_analysis/{brand}")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PROBLEM_KEYWORDS = {
    "stall", "leak", "fail", "noise", "noisy", "grind", "overheat", "jerk",
    "won't start", "not starting", "dies", "check engine", "misfire",
    "vibration", "rattle", "burning", "smell", "warning light", "drain", "hard shift"
}

normalized_keywords = {kw.lower(): kw for kw in PROBLEM_KEYWORDS}
single_keywords = {kw for kw in PROBLEM_KEYWORDS if " " not in kw}
multi_keywords = {kw for kw in PROBLEM_KEYWORDS if " " in kw}

issue_counter = Counter()

def contains_brand_model(entities):
    found_brand = False
    found_model = not model  # True if model is blank
    for sentence_entities in entities:
        for ent in sentence_entities:
            if ent.get("entity_group") == "CAR_BRAND" and ent.get("word", "").lower() == brand:
                found_brand = True
            if model and ent.get("entity_group") == "CAR_MODEL" and ent.get("word", "").lower() == model:
                found_model = True
    return found_brand and found_model

def check_sentence_for_issue(tokens):
    joined = " ".join(tokens)
    found = []
    for phrase in multi_keywords:
        if phrase in joined:
            found.append(phrase)
    for token in tokens:
        if token in single_keywords:
            found.append(token)
    return found

def process_post(post):
    if not (
        contains_brand_model(post.get("preprocessed_title", {}).get("ner_entities", [])) or
        contains_brand_model(post.get("preprocessed_selftext", {}).get("ner_entities", [])) or
        any(contains_brand_model(comment.get("preprocessed_body", {}).get("ner_entities", []))
            for comment in post.get("comments", []))
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
            issues = check_sentence_for_issue(tokens)
            for issue in issues:
                issue_counter[issue] += 1

# === Run on all preprocessed files ===
for file in INPUT_DIR.glob("*.json"):
    with open(file, "r", encoding="utf-8") as f:
        posts = json.load(f)
        for post in posts:
            process_post(post)

# === Save full issue frequencies ===
out_json = OUTPUT_DIR / (f"{model if model else 'all'}_issues.json")
with open(out_json, "w", encoding="utf-8") as f:
    json.dump(issue_counter.most_common(), f, indent=2)

# === Save top 10 issues to JSON (same as plotted) ===
if issue_counter:
    top_issues = issue_counter.most_common(10)
    top_issues_json = {issue: count for issue, count in top_issues}
    
    top_json_path = OUTPUT_DIR / (f"{model if model else 'all'}_top_issues.json")
    with open(top_json_path, "w", encoding="utf-8") as f:
        json.dump(top_issues_json, f, indent=2)

    # Plot top 10 issues
    labels, counts = zip(*top_issues)

    plt.figure(figsize=(10, 6))
    plt.barh(labels[::-1], counts[::-1], color="darkred")
    plt.xlabel("Mentions")
    plt.title(f"Top Vehicle Issues for {brand.title()} {'(' + model.title() + ')' if model else ''}")
    plt.tight_layout()

    viz_path = Path(f"data/visualizations/issues/{brand}")
    viz_path.mkdir(parents=True, exist_ok=True)
    out_img = viz_path / (f"{model if model else 'all'}_issues.png")
    plt.savefig(out_img)
    plt.show()

    print(f"Saved full analysis to {out_json}")
    print(f"Saved top 10 issues to {top_json_path}")
    print(f"Chart saved to {out_img}")
else:
    print(f"No issues found for brand '{brand}' and model '{model}'")