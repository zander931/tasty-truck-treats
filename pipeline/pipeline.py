"""ETL pipeline for T3."""

import argparse
import logging
from dotenv import load_dotenv
from os import environ as ENV

from logger_config import setup_logging
from extract import connect_to_s3, list_objects, check_objects, download_truck_data_files
from transform import combine_transaction_data_files, clean_truck_data


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


if __name__ == "__main__":

    # Configuration
    args = parse_args()
    setup_logging(args.log_output)
    load_dotenv()

    # Connect to s3 bucket, check relevant files and download
    s3 = connect_to_s3()
    contents = list_objects(s3, args.bucket)
    print(contents)
    new_contents = check_objects(contents)
    download_truck_data_files(s3, args.bucket, new_contents)

    combine_transaction_data_files(new_contents)
    clean_truck_data()
