import json
from pathlib import Path
from statistics import mean

DATA_DIR = Path("data/preprocessed_data")

post_lengths = []
comment_lengths = []

for file in DATA_DIR.glob("*.json"):
    with open(file, "r", encoding="utf-8") as f:
        posts = json.load(f)
        for post in posts:
            # Calculate length of post (title + selftext tokens)
            title_tokens = sum(len(sent) for sent in post.get("preprocessed_title", {}).get("cleaned_sentences_tokens", []))
            selftext_tokens = sum(len(sent) for sent in post.get("preprocessed_selftext", {}).get("cleaned_sentences_tokens", []))
            total_post_tokens = title_tokens + selftext_tokens
            if total_post_tokens > 0:
                post_lengths.append(total_post_tokens)

            # Calculate length of each comment
            for comment in post.get("comments", []):
                comment_tokens = sum(len(sent) for sent in comment.get("preprocessed_body", {}).get("cleaned_sentences_tokens", []))
                if comment_tokens > 0:
                    comment_lengths.append(comment_tokens)

print(f"Average post length (tokens): {mean(post_lengths):.2f} based on {len(post_lengths)} posts")
print(f"Average comment length (tokens): {mean(comment_lengths):.2f} based on {len(comment_lengths)} comments")