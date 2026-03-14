import pandas as pd


def save_jobs(jobs, path="outputs/jobs.csv"):
    df = pd.DataFrame(jobs)
    df.to_csv(path, index=False)