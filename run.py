from scraper.job_scraper import scrape_stepstone
from pipeline.matcher import match_jobs
from pipeline.writer import save_jobs


def load_resume():
    with open("data/resume.txt", "r") as f:
        return f.read()


def main():

    resume = load_resume()

    jobs = scrape_stepstone(
        query="working-student-python",
        pages=1
    )

    print("Scraped jobs:", len(jobs))

    if not jobs:
        print("No jobs scraped. Check connectivity, query, or StepStone availability.")
        return

    ranked = match_jobs(resume, jobs)

    save_jobs(ranked)

    print("Saved ranked jobs")


if __name__ == "__main__":
    main()