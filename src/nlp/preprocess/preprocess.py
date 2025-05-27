import os
import json
from pathlib import Path
import numpy as np
from tqdm import tqdm

from text_preprocessing import preprocess_sentences

RAW_REDDIT_DIR = Path("data/raw_data")
RAW_CARTALK_FILE = Path("data/raw_data/cartalk_general_discussion.json")
PREPROCESSED_DIR = Path("data/preprocessed_data")
PREPROCESSED_DIR.mkdir(parents=True, exist_ok=True)

def flatten_reddit_comments(comments):
    flat_comments = []
    def recursive_flatten(comments_list):
        for comment in comments_list:
            body = comment.get("body", "")
            if not body:
                continue
            flat_comments.append({
                "id": comment.get("id", ""),
                "body": body,
                "preprocessed_body": preprocess_sentences(body)
            })
            replies = comment.get("replies", [])
            if replies:
                recursive_flatten(replies)
    recursive_flatten(comments)
    return flat_comments

def preprocess_reddit_thread(thread):
    title = thread.get("title", "")
    selftext = thread.get("selftext", "")

    flat_comments = flatten_reddit_comments(thread.get("comments", []))
    processed_comments = []
    for comment in flat_comments:
        preprocessed = comment["preprocessed_body"]
        processed_comments.append({
            "id": comment["id"],
            "body": comment["body"],
            "preprocessed_body": {
                "cleaned_sentences_tokens": preprocessed["cleaned_sentences_tokens"],
                "ner_entities": preprocessed["ner_entities"]
            }
        })

    title_processed = preprocess_sentences(title)
    selftext_processed = preprocess_sentences(selftext)

    return {
        "id": thread.get("id", ""),
        "title": title,
        "selftext": selftext,
        "comments": processed_comments,
        "preprocessed_title": {
            "cleaned_sentences_tokens": title_processed["cleaned_sentences_tokens"],
            "ner_entities": title_processed["ner_entities"]
        },
        "preprocessed_selftext": {
            "cleaned_sentences_tokens": selftext_processed["cleaned_sentences_tokens"],
            "ner_entities": selftext_processed["ner_entities"]
        }
    }

def preprocess_cartalk_thread(thread):
    title = thread.get("title", "")
    selftext = thread.get("selftext", "")

    processed_comments = []
    for comment in thread.get("comments", []):
        body = comment.get("body", "")
        if not body:
            continue
        preprocessed = preprocess_sentences(body)
        processed_comments.append({
            "id": comment.get("id", ""),
            "body": body,
            "preprocessed_body": {
                "cleaned_sentences_tokens": preprocessed["cleaned_sentences_tokens"],
                "ner_entities": preprocessed["ner_entities"]
            }
        })

    title_processed = preprocess_sentences(title)
    selftext_processed = preprocess_sentences(selftext)

    return {
        "id": thread.get("id", ""),
        "title": title,
        "selftext": selftext,
        "comments": processed_comments,
        "preprocessed_title": {
            "cleaned_sentences_tokens": title_processed["cleaned_sentences_tokens"],
            "ner_entities": title_processed["ner_entities"]
        },
        "preprocessed_selftext": {
            "cleaned_sentences_tokens": selftext_processed["cleaned_sentences_tokens"],
            "ner_entities": selftext_processed["ner_entities"]
        }
    }

def make_json_serializable(obj):
    if isinstance(obj, dict):
        return {k: make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_serializable(v) for v in obj]
    elif isinstance(obj, (np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, (np.int32, np.int64)):
        return int(obj)
    else:
        return obj

def save_preprocessed(data, output_path):
    serializable_data = make_json_serializable(data)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(serializable_data, f, ensure_ascii=False, indent=2)

def main():
    # Process Reddit files
    reddit_files = list(RAW_REDDIT_DIR.glob("reddit_*.json"))
    for file_path in reddit_files:
        print(f"🧼 Preprocessing {file_path.name}...")
        with open(file_path, "r", encoding="utf-8") as f:
            threads = json.load(f)
        preprocessed = [preprocess_reddit_thread(t) for t in tqdm(threads, desc=f"Processing {file_path.name}")]
        output_path = PREPROCESSED_DIR / file_path.name
        save_preprocessed(preprocessed, output_path)
        print(f"✅ Done preprocessing {file_path.name}!")

    # Process CarTalk
    if RAW_CARTALK_FILE.exists():
        print(f"🧼 Preprocessing {RAW_CARTALK_FILE.name}...")
        with open(RAW_CARTALK_FILE, "r", encoding="utf-8") as f:
            threads = json.load(f)
        preprocessed = [preprocess_cartalk_thread(t) for t in tqdm(threads, desc="Processing CarTalk")]
        output_path = PREPROCESSED_DIR / RAW_CARTALK_FILE.name
        save_preprocessed(preprocessed, output_path)
        print(f"✅ Done preprocessing {RAW_CARTALK_FILE.name}!")

if __name__ == "__main__":
    main()