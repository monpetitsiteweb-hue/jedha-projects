"""The North Face - command-line product recommender (Part 2).
Usage: python recommender.py   (needs ../data/sample-data.csv)
"""
import re
from pathlib import Path
import pandas as pd
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import cosine_similarity

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "sample-data.csv"
EPS, MIN_SAMPLES = 0.65, 4

df = pd.read_csv(DATA_PATH)

nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])

def clean_text(text):
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[^a-zA-Z ]", " ", text).lower()
    return " ".join(t.lemma_ for t in nlp(text) if not t.is_stop and len(t) > 2 and t.lemma_.strip())

print("Preparing catalog...")
df["clean"] = df["description"].apply(clean_text)
X = TfidfVectorizer(min_df=2, max_df=0.8).fit_transform(df["clean"])
df["cluster"] = DBSCAN(eps=EPS, min_samples=MIN_SAMPLES, metric="cosine").fit_predict(X)
sim = cosine_similarity(X)
id_to_idx = pd.Series(df.index, index=df["id"])

def product_name(item_id):
    return df.loc[id_to_idx[item_id], "description"].split(" - ")[0].strip()

def find_similar_items(item_id, n=5):
    """Return up to n item ids from the same cluster as item_id, most similar first.
    Fewer than n when the cluster is too small; an outlier gets its n nearest neighbours."""
    idx = id_to_idx[item_id]
    cluster = df.loc[idx, "cluster"]
    mask = (df["cluster"] == cluster) if cluster != -1 else pd.Series(True, index=df.index)
    candidates = df.index[mask & (df.index != idx)]
    ranked = sorted(candidates, key=lambda j: sim[idx, j], reverse=True)[:n]
    return df.loc[ranked, "id"].tolist()

if __name__ == "__main__":
    while True:
        raw = input(f"\nProduct id ({df.id.min()}-{df.id.max()}, q to quit): ").strip()
        if raw.lower() in ("", "q", "quit"):
            break
        if not raw.isdigit() or int(raw) not in id_to_idx.index:
            print("Invalid id, try again.")
            continue
        item_id = int(raw)
        print(f"Selected: #{item_id} {product_name(item_id)}")
        print("You might also be interested by these products...")
        for rid in find_similar_items(item_id):
            print(f"  #{rid:<4} {product_name(rid)}")
