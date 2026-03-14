import pandas as pd
import os


def update_master_csv(new_jobs, path="outputs/master_jobs.csv"):

    new_df = pd.DataFrame(new_jobs)

    if os.path.exists(path):

        master = pd.read_csv(path)

        combined = pd.concat([master, new_df])

        combined = combined.drop_duplicates(subset=["link"])

    else:

        combined = new_df
        combined["status"] = ""
        combined["ats_score"] = ""

    combined.to_csv(path, index=False)

    return combined