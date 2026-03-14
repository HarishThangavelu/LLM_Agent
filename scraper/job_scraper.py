import os
import requests
import re
from bs4 import BeautifulSoup


def is_recent(posted_text, max_days=1):

    if not posted_text:
        return False

    text = posted_text.lower()

    if "heute" in text or "gerade" in text:
        return True

    # Treat "gestern" as within 24 hours
    if "gestern" in text:
        return max_days >= 1

    match = re.search(r"(\d+)", text)

    if match:
        days = int(match.group(1))
        return days <= max_days

    return False


def is_target_role(title):

    title = title.lower()

    keywords = [
        "intern",
        "praktikum",
        "werkstudent",
        "working student",
        "thesis",
        "abschlussarbeit"
    ]

    return any(k in title for k in keywords)


def _fetch_page(url):
    """Fetch a page, preferring curl (works even when requests times out)."""

    import subprocess

    curl_cmd = [
        "curl",
        "--silent",
        "--show-error",
        "--fail",
        "--location",
        "--http1.1",
        "--compressed",
        "--max-time",
        "20",
        url,
        "-H",
        "User-Agent: Mozilla/5.0",
    ]

    try:
        return subprocess.check_output(curl_cmd, stderr=subprocess.STDOUT, text=True)
    except subprocess.CalledProcessError as e:
        print(f"curl failed (code={e.returncode}), output:\n{e.output}")
    except Exception as e:
        print("curl failed with exception:", e)

    # Fallback to requests when curl is not available or fails
    import requests

    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        return requests.get(url, headers=headers, timeout=(5, 60)).text
    except Exception as e:
        print(f"requests fetch failed: {e}")
        raise


def scrape_stepstone(query="python", pages=1):
    import random
    import time

    jobs = []

    cache_path = "data/stepstone_cache.html"
    for page in range(1, pages + 1):
        url = f"https://www.stepstone.de/jobs/{query}?page={page}"

        try:
            html = _fetch_page(url)
        except Exception as e:
            print(f"Failed to fetch page {page} (url={url}): {e}")
            if os.path.exists(cache_path):
                print(f"Using cached HTML at {cache_path} instead.")
                with open(cache_path, "r", encoding="utf-8") as f:
                    html = f.read()
            else:
                continue

        soup = BeautifulSoup(html, "html.parser")

        # be polite / avoid rate-limits
        time.sleep(random.uniform(1, 2))

        cards = soup.find_all("article")

        for card in cards:

            a = card.find("a")

            if not a:
                continue

            title = a.text.strip()

            if not is_target_role(title):
                continue

            link = "https://www.stepstone.de" + a.get("href")

            company_tag = card.find("span")
            company = company_tag.text.strip() if company_tag else "NA"

            date_text = card.find(string=re.compile("vor|heute|gerade", re.I))
            posted = date_text.strip() if date_text else "NA"

            if posted != "NA" and not is_recent(posted):
                continue

            jobs.append({
                "title": title,
                "company": company,
                "link": link,
                "posted": posted
            })

    return jobs