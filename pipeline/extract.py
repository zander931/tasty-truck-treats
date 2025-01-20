import re
import logging
import pandas as pd
import os
from os import environ as ENV
import argparse
from boto3 import client
from dotenv import load_dotenv

from logger_config import setup_logging


def parse_args():
    """Command line arguments to modify the pipeline."""
    parser = argparse.ArgumentParser(description="T3 ETL Pipeline")
    parser.add_argument("-b", "--bucket",
                        type=str, default="sigma-resources-truck",
                        help="Set the AWS S3 bucket name for where the data is stored. (default=sigma-resources-truck)"
                        )
    parser.add_argument("-l", "--log_output",
                        type=str, choices=["file", "console"],
                        default="console",
                        help="Specify where to log output: 'file' or 'console' (default='console')"
                        )
    return parser.parse_args()


def connect_to_s3():
    """Connects to S3."""
    s3 = client("s3", aws_access_key_id=ENV["AWS_ACCESS_KEY"],
                aws_secret_access_key=ENV["AWS_SECRET_ACCESS_KEY"])
    logging.info("Successfully connected to s3 bucket.")
    return s3


def list_objects(s3_client, bucket_name: str) -> list[str]:
    """Returns a list of object names in a specific bucket."""
    objects = s3_client.list_objects_v2(
        Bucket=bucket_name, Prefix='historical/')['Contents']
    return [o["Key"] for o in objects]


def download_truck_data_files(s3_client, bucket_name: str, objects: list[str]):
    """Downloads relevant files from S3 to a data/ folder."""

    for o in objects:
        logging.info(f"Downloading from: {o}")
        s3_client.download_file(
            bucket_name, o, f"historical_data/{o.split('/')[1]}")
        logging.info("Downloaded file: %s", o.split('/')[1])


def check_objects(objects: list[str]) -> bool:
    """Check if the object is relevant to the project."""

    new_contents = []
    pattern = r'^historical/TRUCK_DATA_HIST_\d+\.parquet$'
    for o in objects:
        if re.match(pattern, o):
            new_contents.append(o)
    return new_contents


def collate_trans_data(files: list[str]):
    """Collate transactional data to a csv file."""

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


if __name__ == "__main__":

    # Configuration
    args = parse_args()
    setup_logging(args.log_output)
    load_dotenv()

    # Connect to s3 bucket, check relevant files and download
    s3 = connect_to_s3()
    contents = list_objects(s3, args.bucket)
    new_contents = check_objects(contents)
    download_truck_data_files(s3, args.bucket, new_contents)
    collate_trans_data(new_contents)
