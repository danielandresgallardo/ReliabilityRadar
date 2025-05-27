import os
import json
from pathlib import Path
from typing import Dict, List
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

# Uncomment if running for the first time
# nltk.download('vader_lexicon')

# Initialize sentiment analyzer
sia = SentimentIntensityAnalyzer()

# Paths
INPUT_DIR = Path("data/preprocessed_data")
OUTPUT_DIR = Path("data/sentiment_analysis")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def categorize_sentiment(compound_score: float, pos_threshold=0.05, neg_threshold=-0.05) -> str:
    if compound_score >= pos_threshold:
        return "positive"
    elif compound_score <= neg_threshold:
        return "negative"
    else:
        return "neutral"

def analyze_tokenized_sentences(token_lists: List[List[str]]) -> Dict:
    sentence_sentiments = []
    compound_scores = []

    for tokens in token_lists:
        sentence = " ".join(tokens)
        scores = sia.polarity_scores(sentence)
        compound_scores.append(scores["compound"])
        category = categorize_sentiment(scores["compound"])
        sentence_sentiments.append({
            "sentence": sentence,
            "scores": scores,
            "category": category
        })

    avg_compound = sum(compound_scores) / len(compound_scores) if compound_scores else 0.0
    overall_category = categorize_sentiment(avg_compound)

    return {
        "sentence_sentiments": sentence_sentiments,
        "aggregate_sentiment": {
            "average_compound": round(avg_compound, 4),
            "overall_category": overall_category
        }
    }

def has_car_entity(ner_data: List[List[Dict]]) -> bool:
    for sentence_entities in ner_data:
        for ent in sentence_entities:
            if ent.get("entity_group") in {"CAR_BRAND", "CAR_MODEL"}:
                return True
    return False

def is_car_related(post: Dict) -> bool:
    if has_car_entity(post.get("preprocessed_title", {}).get("ner_entities", [])):
        return True
    if has_car_entity(post.get("preprocessed_selftext", {}).get("ner_entities", [])):
        return True
    for comment in post.get("comments", []):
        if has_car_entity(comment.get("preprocessed_body", {}).get("ner_entities", [])):
            return True
    return False

def analyze_post_sentiment(post: Dict) -> Dict:
    result = {
        "id": post.get("id", ""),
        "title_sentiment": {},
        "selftext_sentiment": {},
        "comments_sentiment": []
    }

    title_data = post.get("preprocessed_title", {})
    selftext_data = post.get("preprocessed_selftext", {})

    result["title_sentiment"] = {
        "sentiment": analyze_tokenized_sentences(title_data.get("cleaned_sentences_tokens", [])),
        "ner_entities": title_data.get("ner_entities", [])
    }

    result["selftext_sentiment"] = {
        "sentiment": analyze_tokenized_sentences(selftext_data.get("cleaned_sentences_tokens", [])),
        "ner_entities": selftext_data.get("ner_entities", [])
    }

    for comment in post.get("comments", []):
        body_data = comment.get("preprocessed_body", {})
        sentiment = analyze_tokenized_sentences(body_data.get("cleaned_sentences_tokens", []))
        ner = body_data.get("ner_entities", [])
        result["comments_sentiment"].append({
            "id": comment.get("id", ""),
            "sentiment": sentiment,
            "ner_entities": ner
        })

    return result

def process_file(input_file: Path):
    print(f"📥 Processing {input_file.name}")
    with open(input_file, "r", encoding="utf-8") as f:
        posts = json.load(f)

    results = []
    for post in posts:
        if is_car_related(post):
            results.append(analyze_post_sentiment(post))

    output_file = OUTPUT_DIR / input_file.name
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"✅ Saved to {output_file}")

if __name__ == "__main__":
    for input_file in INPUT_DIR.glob("*.json"):
        process_file(input_file)