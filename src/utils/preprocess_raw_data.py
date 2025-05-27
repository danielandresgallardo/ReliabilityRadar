import os
import json
import re
from pathlib import Path

RAW_REDDIT_DIR = Path("data/raw_data")
RAW_CARTALK_FILE = Path("data/raw_data/cartalk_general_discussion.json")
PREPROCESSED_DIR = Path("data/preprocessed_data")
PREPROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# === Text Cleaning ===
def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\[deleted\]|\[removed\]", "", text, flags=re.IGNORECASE)
    return text

# === Preprocess Reddit Thread ===
def preprocess_reddit_thread(thread):
    thread["selftext"] = clean_text(thread.get("selftext", ""))
    thread["title"] = clean_text(thread.get("title", ""))
    thread["author"] = thread.get("author", "unknown")
    thread["score"] = int(thread.get("score", 0))
    thread["created_utc"] = float(thread.get("created_utc", 0))
    thread["comments"] = flatten_reddit_comments(thread.get("comments", []))
    return thread

def flatten_reddit_comments(comments):
    flat_comments = []
    def recursive_flatten(comments_list):
        for comment in comments_list:
            body = clean_text(comment.get("body", ""))
            if not body:
                continue
            flat_comments.append({
                "id": comment.get("id", ""),
                "author": comment.get("author", "unknown"),
                "body": body,
                "score": int(comment.get("score", 0)),
                "created_utc": float(comment.get("created_utc", 0))
            })
            replies = comment.get("replies", [])
            if replies:
                recursive_flatten(replies)
    recursive_flatten(comments)
    return flat_comments

# === Preprocess CarTalk Thread ===
def preprocess_cartalk_thread(thread):
    thread["selftext"] = clean_text(thread.get("selftext", ""))
    thread["title"] = clean_text(thread.get("title", ""))
    thread["author"] = thread.get("author", "unknown")
    thread["score"] = int(thread.get("score", 0))
    thread["created_utc"] = float(thread.get("created_utc", 0))
    processed_comments = []
    for c in thread.get("comments", []):
        body = clean_text(c.get("body", ""))
        if not body:
            continue
        processed_comments.append({
            "id": c.get("id", ""),
            "author": c.get("author", "unknown"),
            "body": body,
            "score": int(c.get("score", 0)),
            "created_utc": float(c.get("created_utc", 0))
        })
    thread["comments"] = processed_comments
    return thread

# === Save Function ===
def save_preprocessed(data, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# === Main Runner ===
def main():
    # Process Reddit
    for file_path in RAW_REDDIT_DIR.glob("reddit_*.json"):
        print(f"🧼 Preprocessing {file_path.name}...")
        with open(file_path, "r", encoding="utf-8") as f:
            threads = json.load(f)
        preprocessed = [preprocess_reddit_thread(t) for t in threads]
        output_path = PREPROCESSED_DIR / file_path.name
        save_preprocessed(preprocessed, output_path)

    # Process CarTalk
    if RAW_CARTALK_FILE.exists():
        print(f"🧼 Preprocessing {RAW_CARTALK_FILE.name}...")
        with open(RAW_CARTALK_FILE, "r", encoding="utf-8") as f:
            threads = json.load(f)
        preprocessed = [preprocess_cartalk_thread(t) for t in threads]
        output_path = PREPROCESSED_DIR / RAW_CARTALK_FILE.name
        save_preprocessed(preprocessed, output_path)

    print("✅ Done preprocessing all files!")

if __name__ == "__main__":
    main()
