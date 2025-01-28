"""Functions to extract batch data from time-partitioned S3."""

from dotenv import load_dotenv
import re
import logging
import os
from datetime import datetime
from os import environ as ENV
from boto3 import client

from logger_config import setup_logging


def connect_to_s3():
    """Connects to S3."""
    s3 = client("s3", aws_access_key_id=ENV["AWS_ACCESS_KEY"],
                aws_secret_access_key=ENV["AWS_SECRET_ACCESS_KEY"])
    logging.info("Successfully connected to s3 bucket.")
    return s3


def list_objects(s3_client, bucket_name: str, prefix: str) -> list[str]:
    """Returns a list of object names in a specific bucket."""
    all_objects = []
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    if 'Contents' in response:
        all_objects.extend(response['Contents'])
    return [o["Key"] for o in all_objects]


def check_objects(objects: list[str], prefix: str) -> bool:
    """Check if the object is relevant to the project."""

    new_contents = []
    pattern = fr"^{prefix}T3_T(\d)_([A-Z]\d)\.csv$"
    for o in objects:
        if re.match(pattern, o):
            new_contents.append(o)
    return new_contents


def download_truck_data_files(s3_client, bucket_name: str, objects: list[str]):
    """Downloads relevant files from S3 to a data/ folder."""

    if not os.path.exists('data'):
        os.makedirs('data')
    for o in objects:
        logging.info("Downloading from: %s", o)
        s3_client.download_file(
            bucket_name, o, f"data/{o.split('/')[-1]}")
        logging.info("Downloaded file: %s", o.split('/')[-1])


if __name__ == "__main__":

    setup_logging("console")
    load_dotenv()

    s3 = connect_to_s3()

    now = datetime.now()
    prefix = f'trucks/{now.year}-{now.month}/27/12/'

    contents = list_objects(s3, "sigma-resources-truck", prefix)
    logging.info(f'{contents}')
    all_contents = check_objects(contents, prefix)
    logging.info(f'{all_contents}')
    download_truck_data_files(s3, "sigma-resources-truck", all_contents)

    # f'trucks/{now.year}-{now.month}/{now.day}/{now.hour}/'
