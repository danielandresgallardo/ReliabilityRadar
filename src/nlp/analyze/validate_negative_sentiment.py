import os
import json
from pathlib import Path
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# --- Config ---
SENTIMENT_DIR = Path("data/sentiment_analysis")
TARGET_BRAND = input("🔍 Enter car brand to validate (e.g., kia): ").strip().lower()
VISUAL_PATH = Path(f"data/visualizations/brand_validation")
VISUAL_PATH.mkdir(parents=True, exist_ok=True)

# --- Storage ---
negative_sentences = []
negative_keywords = Counter()

def extract_sentences_and_entities(section):
    sentiments = section.get("sentiment", {}).get("sentence_sentiments", [])
    entities = section.get("ner_entities", [])
    # Ensure alignment
    min_len = min(len(sentiments), len(entities))
    return zip(sentiments[:min_len], entities[:min_len])

def match_brand(ent):
    word = ent.get("word", "").lower()
    return word == TARGET_BRAND and ent.get("entity_group") in {"CAR_BRAND", "ORG", "MISC"}

def process_post(post):
    for key in ["title_sentiment", "selftext_sentiment"]:
        section = post.get(key, {})
        for sent, ents in extract_sentences_and_entities(section):
            if sent.get("category") == "negative":
                if any(match_brand(e) for e in ents):
                    negative_sentences.append(sent["sentence"])
                    for word in sent["sentence"].split():
                        negative_keywords[word.lower()] += 1

    for comment in post.get("comments_sentiment", []):
        sentiments = comment.get("sentiment", {}).get("sentence_sentiments", [])
        entities = comment.get("ner_entities", [])
        min_len = min(len(sentiments), len(entities))
        for sent, ents in zip(sentiments[:min_len], entities[:min_len]):
            if sent.get("category") == "negative":
                if any(match_brand(e) for e in ents):
                    negative_sentences.append(sent["sentence"])
                    for word in sent["sentence"].split():
                        negative_keywords[word.lower()] += 1

# --- Run ---
print(f"\n📂 Scanning {SENTIMENT_DIR} for mentions of: {TARGET_BRAND}\n")
for file in SENTIMENT_DIR.glob("*.json"):
    with open(file, "r", encoding="utf-8") as f:
        posts = json.load(f)
        for post in posts:
            process_post(post)

total = len(negative_sentences)
print(f"\n🔎 Found {total} negative sentence(s) mentioning '{TARGET_BRAND}'\n")

# Print sample
for s in negative_sentences[:20]:
    print("•", s)

# --- Word Cloud ---
if total > 0:
    wc = WordCloud(width=800, height=400, background_color="white")
    wc.generate_from_frequencies(negative_keywords)
    out_path = VISUAL_PATH / f"{TARGET_BRAND}_negative_wordcloud.png"
    wc.to_file(out_path)
    print(f"\n✅ Saved word cloud to {out_path}")
else:
    print("⚠️ No negative mentions found. Try another brand or check your NER alignment.")