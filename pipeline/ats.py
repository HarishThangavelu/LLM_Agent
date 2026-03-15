import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import time
import hashlib
import os
import re


OLLAMA_URL = "http://localhost:11434/api/embeddings"
MODEL = "nomic-embed-text"

JD_CACHE_DIR = "data/jd_cache"
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
        return np.array(r.json()["embedding"])
    except Exception as e:
        print("Embedding error:", e)
        return None


def cosine(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


# ---------- JD Cache ----------

def jd_cache_path(link):
    h = hashlib.md5(link.encode()).hexdigest()
    return os.path.join(JD_CACHE_DIR, h + ".txt")


def clean_text(text):
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def fetch_and_cache_jd(link):

    path = jd_cache_path(link)

    # Already cached
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(link, headers=headers, timeout=20)
    except Exception as e:
        print("JD fetch failed:", e)
        return ""

    soup = BeautifulSoup(r.text, "html.parser")

    text = soup.get_text(" ", strip=True)
    text = clean_text(text)

    text = text[:7000]

    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

    return text


# ---------- ATS Pipeline ----------

def run_ats():

    df = pd.read_csv(CSV_PATH)

    resume = open(RESUME_PATH).read()

    print("Embedding resume...")
    resume_vec = embed(resume)

    if resume_vec is None:
        print("Resume embedding failed")
        return

    ats_scores = []
    priority = []

    for i, row in df.iterrows():

        if not pd.isna(row.get("ats_score")):
            ats_scores.append(row["ats_score"])
            priority.append(row.get("priority", ""))
            continue

        print(f"Processing {i+1}/{len(df)}")

        jd = fetch_and_cache_jd(row["link"])

        if len(jd) < 500:
            print("JD too small → skip")
            ats_scores.append(None)
            priority.append("")
            continue

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

        time.sleep(1)

    df["ats_score"] = ats_scores
    df["priority"] = priority

    df.to_csv(CSV_PATH, index=False)

    print("ATS scoring complete")


if __name__ == "__main__":
    run_ats()