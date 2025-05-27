import os
import json
from pathlib import Path

RAW_DATA_DIR = Path("data/raw_data")
PREPROCESSED_DIR = Path("data/old_preprocessed_data")

def count_posts_and_comments(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    num_posts = len(data)
    num_comments = sum(len(thread.get("comments", [])) for thread in data)

    return num_posts, num_comments

def main():
    print("RAW_DATA")
    print(f"{'File':<40} {'Posts':>10} {'Comments':>12}")
    print("-" * 65)

    for file in RAW_DATA_DIR.glob("*.json"):
        num_posts, num_comments = count_posts_and_comments(file)
        print(f"{file.name:<40} {num_posts:>10,} {num_comments:>12,}")

    print("\n")
    print("PROPROCESSED_DATA")
    print(f"{'File':<40} {'Posts':>10} {'Comments':>12}")
    print("-" * 65)

    for file in PREPROCESSED_DIR.glob("*.json"):
        num_posts, num_comments = count_posts_and_comments(file)
        print(f"{file.name:<40} {num_posts:>10,} {num_comments:>12,}")

if __name__ == "__main__":
    main()
