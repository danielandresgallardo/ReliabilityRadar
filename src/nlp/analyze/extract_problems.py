import os
import json
from pathlib import Path
from collections import defaultdict, Counter

# Config
INPUT_DIR = Path("data/preprocessed_data")
OUTPUT_DIR = Path("data/issue_analysis")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PROBLEM_KEYWORDS = {
    "stall", "leak", "fail", "noise", "noisy", "grind", "overheat", "jerk",
    "won't start", "not starting", "dies", "check engine", "misfire",
    "vibration", "rattle", "burning", "smell", "warning light", "drain", "hard shift"
}

# Normalize multi-word expressions
normalized_keywords = {kw.lower(): kw for kw in PROBLEM_KEYWORDS}
single_keywords = {kw for kw in PROBLEM_KEYWORDS if " " not in kw}
multi_keywords = {kw for kw in PROBLEM_KEYWORDS if " " in kw}

issue_counter = Counter()

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

# Run on all preprocessed files
for file in INPUT_DIR.glob("*.json"):
    with open(file, "r", encoding="utf-8") as f:
        posts = json.load(f)
        for post in posts:
            process_post(post)

# Save output
output_file = OUTPUT_DIR / "issue_frequencies.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(issue_counter.most_common(), f, indent=2)

print(f"✅ Saved issue analysis to {output_file}")

import json
import matplotlib.pyplot as plt

with open("data/issue_analysis/issue_frequencies.json", "r") as f:
    issues = json.load(f)

top_issues = issues[:10]
labels, counts = zip(*top_issues)

plt.figure(figsize=(10, 6))
plt.barh(labels[::-1], counts[::-1], color="darkred")
plt.xlabel("Mentions")
plt.title("Top Reported Vehicle Issues")
plt.tight_layout()

Path("data/visualizations").mkdir(parents=True, exist_ok=True)
plt.savefig("data/visualizations/top_vehicle_issues.png")
plt.show()