"""Functions that transform the batch data prior to uploading."""

import os
import re
import logging
import pandas as pd
import numpy as np
from datetime import datetime
from dotenv import load_dotenv

from extract_2 import connect_to_s3, list_objects, check_objects, download_truck_data_files
from logger_config import setup_logging


def combine_transaction_data_files(files: list[str], batch: int = 1):
    """Loads and combines relevant files from the data/ folder.

    Produces a single combined file in the data/ folder."""

    truck_batch_df = []
    for f in files:
        filename = f.split('/')[-1]
        file_path = os.path.join("data/", filename)
        try:
            df = pd.read_csv(file_path)

            search = re.search(r"T3_T(\d)_", f)
            truck_id = search.group(1)
            df['truck_id'] = truck_id

            truck_batch_df.append(df)
            os.remove(file_path)
            logging.info("File '%s' deleted.", filename)
        except Exception as e:
            logging.error("%s", e)
            continue

    if not truck_batch_df:
        logging.error("No data files were loaded.")
        return

    combined_df = pd.concat(truck_batch_df, ignore_index=True)
    combined_df.to_csv(f'data/truck_batch_{batch}.csv', index=False)
    logging.info(
        "Combined transactional data saved to 'truck_batch_%s.csv'", batch)


def clean_truck_data(batch: int = 1):
    """Cleans the transactional data in the .csv file."""

    trucks = pd.read_csv(f'data/truck_batch_{batch}.csv')
    trucks['timestamp'] = pd.to_datetime(trucks['timestamp'])
    trucks['total'] = trucks['total'].replace(
        ['0', '0.00', 'VOID', 'blank', 'ERR'], np.nan)
    trucks = trucks.dropna(subset=['total'])
    trucks['total'] = trucks['total'].astype(float)
    trucks = trucks[trucks['total'] >= 0]
    trucks.loc[trucks['total'] > 50.00, 'total'] = trucks['total']/100
    trucks['total'] = trucks['total'].round(2)
    trucks = trucks[trucks['type'].isin(['cash', 'card'])]
    trucks['type'] = trucks['type'].apply(lambda x: 1 if x == 'cash' else 2)
    trucks.to_csv(f'data/cleaned_batch_{batch}.csv', index=False)
    logging.info("Batch data cleaned.")
    os.remove(f'data/truck_batch_{batch}.csv')
    logging.info("Raw data deleted.")


if __name__ == "__main__":

    # Extract
    setup_logging("console")
    load_dotenv()
    now = datetime.now()
    prefix = f'trucks/{now.year}-{now.month}/28/12/'

    s3 = connect_to_s3()
    contents = list_objects(s3, "sigma-resources-truck", prefix)
    all_contents = check_objects(contents, prefix)
    download_truck_data_files(s3, "sigma-resources-truck", all_contents)

    # Transform
    batch = 5
    combine_transaction_data_files(all_contents, batch)
    clean_truck_data(batch)
