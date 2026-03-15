import requests
import re
import time
import random
from bs4 import BeautifulSoup


BASE = "https://www.stepstone.de/jobs"


def is_recent(posted_text, max_days=2):

    if not posted_text:
        return False

    text = posted_text.lower()

    if "heute" in text or "gerade" in text:
        return True

    if "gestern" in text:
        return True

    m = re.search(r"(\d+)", text)
    if m:
        return int(m.group(1)) <= max_days

    return False


def scrape_stepstone(query="python", max_pages=2):

    jobs = []

    headers = {"User-Agent": "Mozilla/5.0"}

    for page in range(1, max_pages + 1):

        url = f"{BASE}/{query}?page={page}"

        print(f"[SCRAPER] Fetching page {page} → {query}")

        html = None

        # -------- retry block --------
        for attempt in range(3):
            try:
                r = requests.get(url, headers=headers, timeout=25)
                html = r.text
                break
            except Exception as e:
                print(f"[SCRAPER] Retry {attempt+1} failed:", e)
                time.sleep(3 + attempt * 2)

        if html is None:
            print("[SCRAPER] Page failed after retries → skipping")
            continue

        soup = BeautifulSoup(html, "html.parser")

        cards = soup.find_all("article")

        if not cards:
            print("[SCRAPER] No cards found → stop pagination")
            break

        for card in cards:

            a = card.find("a")
            if not a:
                continue

            title = a.text.strip()

            link = "https://www.stepstone.de" + a.get("href")

            company_tag = card.find("span")
            company = company_tag.text.strip() if company_tag else ""

            date_text = card.find(string=re.compile("vor|heute|gerade", re.I))
            posted = date_text.strip() if date_text else ""

            if not is_recent(posted):
                continue

            jobs.append({
                "title": title,
                "company": company,
                "link": link,
                "posted": posted,
                "source": "stepstone"
            })

        time.sleep(random.uniform(2, 4))

    print(f"[SCRAPER] Collected {len(jobs)} jobs")

    return jobs