import pandas as pd
import os
import logging
from datetime import datetime


CSV_PATH = "outputs/master_jobs.csv"

REQUIRED_COLUMNS = [
    "title",
    "company",
    "link",
    "posted",
    "status",
    "ats_score",
    "priority",
    "source",
    "scraped_at"
]


logging.basicConfig(level=logging.INFO)


def update_master_csv(new_jobs: list[dict]) -> pd.DataFrame:

    if not new_jobs:
        logging.info("No new jobs received.")
        if os.path.exists(CSV_PATH):
            return pd.read_csv(CSV_PATH)
        return pd.DataFrame(columns=REQUIRED_COLUMNS)

    new_df = pd.DataFrame(new_jobs)

    # add ingestion timestamp
    new_df["scraped_at"] = datetime.now().isoformat()

    # ensure metadata schema
    for col in REQUIRED_COLUMNS:
        if col not in new_df.columns:
            new_df[col] = ""

    if os.path.exists(CSV_PATH):

        master_df = pd.read_csv(CSV_PATH)

        initial_count = len(master_df)

        combined = pd.concat([master_df, new_df], ignore_index=True)

        combined = combined.drop_duplicates(subset=["link"], keep="first")

        new_added = len(combined) - initial_count

    else:

        combined = new_df
        new_added = len(new_df)

    # ensure all required columns exist after merge
    for col in REQUIRED_COLUMNS:
        if col not in combined.columns:
            combined[col] = ""

    combined = combined[REQUIRED_COLUMNS]

    total_after = len(combined)

    logging.info(f"Added {new_added} new jobs. Total jobs now: {total_after}")

    # safe write
    tmp_path = CSV_PATH + ".tmp"
    combined.to_csv(tmp_path, index=False)
    os.replace(tmp_path, CSV_PATH)

    return combined