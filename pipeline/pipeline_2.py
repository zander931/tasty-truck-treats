"""ETL pipeline for T3 batch data."""

import argparse
import logging
from datetime import datetime
from dotenv import load_dotenv

from logger_config import setup_logging
from extract_2 import connect_to_s3, list_objects, check_objects, download_truck_data_files
from transform_2 import combine_transaction_data_files, clean_truck_data
from load import get_db_connection, upload_transaction_data


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

    now = datetime.now()
    hour = (now.hour // 3) * 3
    prefix = f'trucks/{now.year}-{now.month}/{now.day}/{hour}/'

    # Connect to s3 bucket, check relevant files and download
    s3 = connect_to_s3()
    contents = list_objects(s3, args.bucket, prefix)
    all_contents = check_objects(contents, prefix)
    download_truck_data_files(s3, args.bucket, all_contents)

    # Transform data ready for insertion to the database
    batch = 6
    combine_transaction_data_files(all_contents, batch)
    clean_truck_data(batch)

    # Load into MySQL database
    conn = get_db_connection()
    logging.info("Successfully connected to T3 database.")
    upload_transaction_data(conn, f'data/cleaned_batch_{batch}.csv')
    logging.info("Successfully inserted transactional data into database.")
    conn.close()
