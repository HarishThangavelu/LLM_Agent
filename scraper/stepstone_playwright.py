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


async def scrape_stepstone(query, max_pages=2):

    print("RUNNING STEPSTONE V4")

    jobs = []

    async with async_playwright() as p:

        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        for page_no in range(max_pages):

            url = f"{BASE}/jobs/{query}" if page_no == 0 else f"{BASE}/jobs/{query}?page={page_no+1}"

            print(f"[PW] Opening page {page_no+1}: {url}")

            await page.goto(url, timeout=60000)
            await page.wait_for_timeout(4000)

            # cookie
            try:
                await page.click('button:has-text("Akzeptieren")', timeout=3000)
            except:
                pass

            # lazy load
            for _ in range(5):
                await page.mouse.wheel(0, 4000)
                await page.wait_for_timeout(1200)

            await page.wait_for_selector("article")

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

            # crawl stop logic
            if page_relevant == 0:
                print("[PW] Stop pagination → no relevant jobs")
                break

            sleep = random.uniform(3, 6)
            print(f"[PW] Page sleep {sleep:.2f}s")
            await page.wait_for_timeout(int(sleep * 1000))

        await browser.close()

    # cross-page dedupe
    jobs = list({j["link"]: j for j in jobs}.values())

    print("[PW] Final jobs:", len(jobs))

    return jobs


# optional standalone debug run
if __name__ == "__main__":
    res = asyncio.run(scrape_stepstone("werkstudent-python", max_pages=2))
    print(res[:5])