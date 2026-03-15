import os
import hashlib
import re
import requests
from bs4 import BeautifulSoup


JD_CACHE_DIR = "data/jd_cache"


def ensure_cache_dir():
    os.makedirs(JD_CACHE_DIR, exist_ok=True)


def jd_hash(link: str) -> str:
    return hashlib.md5(link.encode()).hexdigest()


def jd_file_path(link: str) -> str:
    ensure_cache_dir()
    return os.path.join(JD_CACHE_DIR, jd_hash(link) + ".txt")


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def fetch_jd_from_web(link: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(link, headers=headers, timeout=20)
    except Exception as e:
        print("JD fetch error:", e)
        return ""

    soup = BeautifulSoup(r.text, "html.parser")

    text = soup.get_text(" ", strip=True)

    text = clean_text(text)

    return text[:7000]


def get_jd(link: str) -> str:
    """
    Main API:
    → returns JD text
    → uses cache if exists
    → otherwise fetch + store
    """

    path = jd_file_path(link)

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    text = fetch_jd_from_web(link)

    if text:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)

    return text