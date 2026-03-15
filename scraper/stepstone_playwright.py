import asyncio
from playwright.async_api import async_playwright

BASE = "https://www.stepstone.de"

SKILL_FILTER = [
    "python","data","ai","ml","software",
    "backend","vision","automation","engineer"
]

def is_recent(posted_text):

    if not posted_text:
        return False

    t = posted_text.lower()

    return any(x in t for x in [
        "heute","gestern","1 tag","2 tag","3 tag"
    ])

def is_relevant(title):
    return any(k in title.lower() for k in SKILL_FILTER)


async def scrape_stepstone(query):

    print("RUNNING STEPSTONE V3")

    jobs = []

    url = f"{BASE}/jobs/{query}"

    async with async_playwright() as p:

        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        print("[PW] Opening:", url)

        await page.goto(url, timeout=60000)
        await page.wait_for_timeout(4000)

        try:
            await page.click('button:has-text("Akzeptieren")', timeout=4000)
        except:
            pass

        for _ in range(6):
            await page.mouse.wheel(0, 5000)
            await page.wait_for_timeout(1500)

        await page.wait_for_selector("article")

        cards = await page.query_selector_all("article")

        print("[PW] Articles:", len(cards))

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

        await browser.close()

    jobs = list({j["link"]: j for j in jobs}.values())

    print("[PW] Final jobs:", len(jobs))

    return jobs