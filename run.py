import asyncio
from scraper.stepstone_playwright import scrape_stepstone
from pipeline.storage import update_master_csv
from pipeline.ats import run_ats


def load_keywords():
    with open("data/resume.txt") as f:
        return [k.strip() for k in f if k.strip()]


def build_queries(keywords):

    role_prefix = [
        "werkstudent",
        "praktikum",
        "abschlussarbeit"
    ]

    queries = []

    for role in role_prefix:
        for skill in keywords:
            q = f"{role}-{skill}".lower().replace(" ", "-")
            queries.append(q)

    return queries


def main():

    print("\n=== JOB PIPELINE START ===\n")

    keywords = load_keywords()
    queries = build_queries(keywords)

    all_jobs = []

    for q in queries[:5]:

        print(f"[RUNNER] Searching → {q}")

        jobs = asyncio.run(scrape_stepstone(query=q))

        all_jobs += jobs

    print(f"[RUNNER] Total scraped jobs: {len(all_jobs)}")

    if not all_jobs:
        return

    df = update_master_csv(all_jobs)

    print(f"[RUNNER] Master rows: {len(df)}")

    run_ats()

    print("\n=== JOB PIPELINE END ===\n")


if __name__ == "__main__":
    main()