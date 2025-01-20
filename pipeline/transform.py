import pandas as pd
import numpy as np
import os
import logging
import re


def combine_transaction_data_files(files: list[str]):
    """Loads and combines relevant files from the data/ folder.

    Produces a single combined file in the data/ folder."""

    truck_hist_df = []
    for f in files:
        filename = f.split('/')[1]
        file_path = os.path.join("historical_data/", filename)
        try:
            df = pd.read_parquet(file_path)

            match = re.match(r'^historical/TRUCK_DATA_HIST_(\d+)\.parquet$', f)
            truck_id = match.group(1)
            df['truck_id'] = truck_id

            truck_hist_df.append(df)
            os.remove(file_path)
            logging.info(f"File '{filename}' deleted.")
        except Exception as e:
            logging.error("%s", e)
            continue

    if not truck_hist_df:
        logging.error("No data files were loaded.")
        return

    combined_df = pd.concat(truck_hist_df, ignore_index=True)
    combined_df.to_csv("historical_data/truck_hist_combined.csv", index=False)
    logging.info(
        "Combined transactional data saved to 'truck_hist_combined.csv'")


def clean_truck_data():
    """Cleans the transactional data in the .csv file."""

    trucks = pd.read_csv('historical_data/truck_hist_combined.csv')
    trucks['timestamp'] = pd.to_datetime(trucks['timestamp'])
    trucks['total'] = trucks['total'].replace(
        ['0', '0.00', 'VOID', 'blank', 'ERR'], np.nan)
    trucks = trucks.dropna(subset=['total'])
    trucks['total'] = trucks['total'].astype(float)
    trucks.to_csv("historical_data/truck_hist_cleaned.csv", index=False)
    logging.info("Historical data cleaned.")
    os.remove('historical_data/truck_hist_combined.csv')
    logging.info("Raw data deleted.")


if __name__ == "__main__":
    pass
