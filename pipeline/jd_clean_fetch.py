import os
import hashlib
import asyncio
from playwright.async_api import async_playwright


CACHE_DIR = "data/jd_cache"
os.makedirs(CACHE_DIR, exist_ok=True)


def jd_cache_path(url):
    h = hashlib.md5(url.encode()).hexdigest()
    return f"{CACHE_DIR}/{h}.txt"


def is_cached(url):
    return os.path.exists(jd_cache_path(url))


def clean_text(text):
    text = text.replace("\n", " ")
    text = " ".join(text.split())
    return text


async def fetch_clean_jd(url):

    if is_cached(url):
        print("JD cached → skip")
        return True

    try:
        async with async_playwright() as p:

            browser = await p.chromium.launch(headless=True)

            context = await browser.new_context(
                viewport={"width":1280,"height":800}
            )

            page = await context.new_page()

            await page.goto(url, timeout=60000)

            await page.wait_for_timeout(3000)

            # cookie click
            try:
                await page.click('button:has-text("Akzeptieren")', timeout=3000)
            except:
                pass

            # ⭐ MAIN JD CONTAINER (StepStone stable selector)
            selectors = [
                "div[data-testid='jobdetails-description']",
                "section[class*='job-description']",
                "div[class*='listing-content']",
                "main"
            ]

            content_text = ""

            for sel in selectors:
                try:
                    el = await page.query_selector(sel)
                    if el:
                        content_text = await el.inner_text()
                        if len(content_text) > 800:
                            break
                except:
                    pass

            if len(content_text) < 500:
                print("JD extraction weak")
                await browser.close()
                return False

            content_text = clean_text(content_text)

            with open(jd_cache_path(url), "w", encoding="utf-8") as f:
                f.write(content_text[:8000])

            print("JD CLEAN fetched")

            await browser.close()

            return True

    except Exception as e:
        print("JD clean fetch error:", e)
        return False