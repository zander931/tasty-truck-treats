"""A script that extracts data from an S3."""

import re
import logging
from os import environ as ENV
from boto3 import client


def connect_to_s3():
    """Connects to S3."""
    s3 = client("s3", aws_access_key_id=ENV["AWS_ACCESS_KEY"],
                aws_secret_access_key=ENV["AWS_SECRET_ACCESS_KEY"])
    logging.info("Successfully connected to s3 bucket.")
    return s3


def list_objects(s3_client, bucket_name: str) -> list[str]:
    """Returns a list of object names in a specific bucket."""
    all_objects = []
    for prefix in ['historical/', 'metadata/']:
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        if 'Contents' in response:
            all_objects.extend(response['Contents'])
    return [o["Key"] for o in all_objects]


def check_objects(objects: list[str]) -> bool:
    """Check if the object is relevant to the project."""

    new_contents = []
    pattern = r'^(historical/TRUCK_DATA_HIST_\d+\.parquet|metadata/details\.xlsx)$'
    for o in objects:
        if re.match(pattern, o):
            new_contents.append(o)
    return new_contents


def download_truck_data_files(s3_client, bucket_name: str, objects: list[str]):
    """Downloads relevant files from S3 to a data/ folder."""

    for o in objects:
        logging.info("Downloading from: %s", o)
        s3_client.download_file(
            bucket_name, o, f"data/{o.split('/')[1]}")
        logging.info("Downloaded file: %s", o.split('/')[1])


if __name__ == "__main__":

    s_three = connect_to_s3()
    contents = list_objects(s_three, "sigma-resources-truck")
    all_contents = check_objects(contents)
    download_truck_data_files(s_three, "sigma-resources-truck", all_contents)
