import pandas as pd
import numpy as np
import requests
import time
import random
import os

from pipeline.jd_fetch import fetch_jd, jd_cache_path


OLLAMA_URL = "http://localhost:11434/api/embeddings"
MODEL = "nomic-embed-text"

CSV_PATH = "outputs/master_jobs.csv"
RESUME_PATH = "data/resume_full.txt"


# ---------- Embedding ----------

def embed(text):

    try:
        r = requests.post(
            OLLAMA_URL,
            json={"model": MODEL, "prompt": text},
            timeout=60
        )

        if r.status_code != 200:
            print("Embedding HTTP error")
            return None

        return np.array(r.json()["embedding"])

    except Exception as e:
        print("Embedding error:", e)
        return None


def cosine(a, b):

    try:
        val = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
        if np.isnan(val):
            return 0
        return val
    except:
        return 0


def load_cached_jd(link):

    path = jd_cache_path(link)

    if not os.path.exists(path):
        return None

    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# ---------- ATS Pipeline ----------

def run_ats():

    df = pd.read_csv(CSV_PATH)

    resume = open(RESUME_PATH, encoding="utf-8").read()

    print("\nEmbedding resume...")
    resume_vec = embed(resume)

    if resume_vec is None:
        print("Resume embedding failed")
        return

    ats_scores = []
    priority = []

    for i, row in df.iterrows():

        # skip already scored
        if not pd.isna(row.get("ats_score")):
            ats_scores.append(row["ats_score"])
            priority.append(row.get("priority", ""))
            continue

        link = row["link"]

        print(f"\nProcessing {i+1}/{len(df)}")

        # ---- JD FETCH V2 ----
        ok = fetch_jd(link)

        if not ok:
            ats_scores.append(None)
            priority.append("")
            continue

        jd = load_cached_jd(link)

        if not jd or len(jd) < 800:
            print("JD invalid size")
            ats_scores.append(None)
            priority.append("")
            continue

        # ---- EMBEDDING ----
        jd_vec = embed(jd)

        if jd_vec is None:
            ats_scores.append(None)
            priority.append("")
            continue

        sim = cosine(resume_vec, jd_vec)

        ats = round(sim * 100, 2)

        ats_scores.append(ats)

        if ats >= 85:
            priority.append("HIGH")
        elif ats >= 70:
            priority.append("MEDIUM")
        else:
            priority.append("LOW")

        sleep_time = random.uniform(2,4)
        print(f"Worker sleep {sleep_time:.2f}s")
        time.sleep(sleep_time)

    df["ats_score"] = ats_scores
    df["priority"] = priority

    df.to_csv(CSV_PATH, index=False)

    print("\nATS scoring complete")