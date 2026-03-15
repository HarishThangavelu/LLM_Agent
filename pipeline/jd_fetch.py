import requests
import time
import random
import hashlib
import os


CACHE_DIR = "data/jd_cache"
os.makedirs(CACHE_DIR, exist_ok=True)


def jd_cache_path(url):

    h = hashlib.md5(url.encode()).hexdigest()
    return f"{CACHE_DIR}/{h}.txt"


def is_cached(url):

    return os.path.exists(jd_cache_path(url))


def save_cache(url, text):

    with open(jd_cache_path(url), "w", encoding="utf-8") as f:
        f.write(text)


def fetch_jd(url, max_retry=3):

    if is_cached(url):
        print("JD cached → skip")
        return True

    headers = {
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    for attempt in range(max_retry):

        try:

            r = requests.get(
                url,
                headers=headers,
                timeout=35
            )

            if r.status_code == 200 and len(r.text) > 4000:

                save_cache(url, r.text)

                print("JD fetched OK")

                return True

            else:
                print("JD small / bad status")

        except Exception as e:
            print("JD fetch error:", str(e))

        sleep_time = (2 ** attempt) + random.uniform(2,5)
        print(f"Retry sleep {sleep_time:.2f}s")

        time.sleep(sleep_time)

    print("JD failed after retries")

    return False