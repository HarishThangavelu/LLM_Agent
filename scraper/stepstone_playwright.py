import asyncio
import random
from playwright.async_api import async_playwright


BASE = "https://www.stepstone.de"

SKILL_FILTER = [
    "python", "data", "ai", "ml", "software",
    "backend", "vision", "automation", "engineer"
]


def is_recent(posted_text):

    if not posted_text:
        return False

    t = posted_text.lower()

    return any(x in t for x in [
        "heute", "gestern", "1 tag", "2 tag", "3 tag"
    ])


def is_relevant(title):
    return any(k in title.lower() for k in SKILL_FILTER)


# ---------- Navigation Stabilizer ----------

async def safe_goto(page, url, retry=2):

    for attempt in range(retry):

        try:
            await page.goto(
                url,
                timeout=60000,
                wait_until="domcontentloaded"
            )
            return True

        except Exception as e:
            print(f"[PW] goto retry {attempt+1} → {e}")
            await page.wait_for_timeout(3000 + attempt * 2000)

    return False


# ---------- Main Scraper ----------

async def scrape_stepstone(query, max_pages=2):

    print("RUNNING STEPSTONE V4")

    jobs = []

    async with async_playwright() as p:

        browser = await p.chromium.launch(headless=True)
        for page_no in range(max_pages):
            context = await browser.new_context(
            viewport={"width": random.randint(1100,1400),
                  "height": random.randint(700,900)},
            user_agent=random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Mozilla/5.0 (X11; Linux x86_64)",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
        ])
    )
        page = await context.new_page()
        url = (
        f"{BASE}/jobs/{query}"
        if page_no == 0
        else f"{BASE}/jobs/{query}?page={page_no+1}"
    )
        print(f"[PW] Opening page {page_no+1}: {url}")


            # random jitter before navigation
            await page.wait_for_timeout(random.randint(2000, 4000))

            ok = await safe_goto(page, url)

            if not ok:
                print("[PW] Pagination navigation failed → stopping crawl")
                await context.close()
                break
            await page.wait_for_timeout(4000)

            await page.wait_for_timeout(4000)

            # cookie
            try:
                await page.click('button:has-text("Akzeptieren")', timeout=3000)
            except:
                pass

            # lazy load scroll
            for _ in range(5):
                await page.mouse.wheel(0, 4000)
                await page.wait_for_timeout(1200)

            try:
                await page.wait_for_selector("article", timeout=15000)
            except:
                print("[PW] No articles found → stop")
                await context.close()
                break

            cards = await page.query_selector_all("article")

            print("[PW] Articles:", len(cards))

            page_relevant = 0

            for card in cards:

                link_el = await card.query_selector('a[href*="/stellenangebote"]')
                if not link_el:
                    continue

                title = (await link_el.inner_text()).strip()

                if not is_relevant(title):
                    continue

                href = await link_el.get_attribute("href")

                date_el = await card.query_selector("time, span[class*='date']")
                posted = ""

                if date_el:
                    posted = (await date_el.inner_text()).strip()

                if not is_recent(posted):
                    continue

                if not href.startswith("http"):
                    href = BASE + href

                jobs.append({
                    "title": title,
                    "link": href,
                    "posted": posted,
                    "source": "stepstone"
                })

                page_relevant += 1

            print("[PW] Relevant jobs this page:", page_relevant)

            # ----- Crawl Stop Logic -----
            if page_relevant == 0:
                print("[PW] Stop pagination → no relevant jobs")
                break

            sleep = random.uniform(3, 6)
            print(f"[PW] Page sleep {sleep:.2f}s")
            await page.wait_for_timeout(int(sleep * 1000))
            await context.close()

        await browser.close()

    # ----- Cross-page dedupe -----
    jobs = list({j["link"]: j for j in jobs}.values())

    print("[PW] Final jobs:", len(jobs))

    return jobs


# ----- Debug Run -----
if __name__ == "__main__":
    res = asyncio.run(scrape_stepstone("werkstudent-python", max_pages=2))
    print(res[:5])