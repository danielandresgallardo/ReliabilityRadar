import os
import json
from pathlib import Path
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import matplotlib.pyplot as plt
import pandas as pd
from tqdm import tqdm

# Paths
DATA_DIR = Path("data/preprocessed_data")
OUTPUT_DIR = Path("data/topic_modeling")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Collect all sentences from cleaned_sentences_tokens
corpus = []

for file in tqdm(list(DATA_DIR.glob("*.json")), desc="🔍 Loading data"):
    with open(file, "r", encoding="utf-8") as f:
        posts = json.load(f)
        for post in posts:
            for section in ["preprocessed_title", "preprocessed_selftext"]:
                for sent in post.get(section, {}).get("cleaned_sentences_tokens", []):
                    corpus.append(" ".join(sent))
            for comment in post.get("comments", []):
                for sent in comment.get("preprocessed_body", {}).get("cleaned_sentences_tokens", []):
                    corpus.append(" ".join(sent))

if not corpus:
    print("⚠️ No sentences found in corpus. Please check your preprocessed data.")
    exit()

print("🧠 Vectorizing...")
# Vectorize the text data
vectorizer = CountVectorizer(max_df=0.95, min_df=5, stop_words='english')
X = vectorizer.fit_transform(corpus)

print("🚀 Training LDA model...")
# Train LDA model
lda = LatentDirichletAllocation(n_components=6, random_state=42)
lda.fit(X)

print("📊 Extracting and saving topics...")
# Get feature names
feature_names = vectorizer.get_feature_names_out()

# Save and display top words per topic
topics = {}
for topic_idx, topic in enumerate(lda.components_):
    top_words = [feature_names[i] for i in topic.argsort()[:-11:-1]]
    topics[f"Topic {topic_idx+1}"] = top_words

# Save topics to JSON
with open(OUTPUT_DIR / "lda_topics.json", "w", encoding="utf-8") as f:
    json.dump(topics, f, indent=2)

# Plot topics as table
plt.figure(figsize=(10, 6))
topic_df = pd.DataFrame.from_dict(topics, orient='index', columns=[f"Word {i+1}" for i in range(10)])
plt.table(cellText=topic_df.values, rowLabels=topic_df.index, colLabels=topic_df.columns, loc='center')
plt.axis('off')
plt.title("LDA Topics from Car Discussions")
plt.tight_layout()
plt.savefig("data/visualizations/lda_topics.png")

print("✅ LDA topic modeling completed and saved to data/topic_modeling/ and data/visualizations/lda_topics.png")