
# from csv import DictReader
import pymysql.cursors
from pymysql.connections import Connection
from datetime import datetime
from dotenv import load_dotenv
from os import environ as ENV


def get_db_connection() -> Connection:
    """Returns a live connection to the MySQL database."""

    return pymysql.connect(host=ENV['DB_HOST'],
                           user=ENV['DB_USER'],
                           password=ENV['DB_PASSWORD'],
                           database=ENV['DB_NAME'],
                           port=int(ENV['DB_PORT']),
                           cursorclass=pymysql.cursors.DictCursor)


# def load_truck_data() -> list[tuple]:
#     """Loads and transforms the data into a list of tuples."""

#     with open('truck_hist_cleaned.csv', 'r', encoding='utf-8') as f:
#         data = []
#         reader = DictReader(f)
#         for row in reader:
#             data.append((
#                 int(row['truck_id']),
#                 int(row['type']),
#                 float(row['total']),
#                 datetime.strptime(row['timestamp'], "%Y-%m-%d %H:%M:%S")
#             ))
#         return data


def upload_transaction_data(conn: Connection):
    """Uploads transaction data to the database."""

    query = """
        LOAD DATA LOCAL INFILE '{data/truck_hist_cleaned.csv}'
        INTO TABLE FACT_Transaction
        FIELDS TERMINATED BY ','
        LINES TERMINATED BY '\n'
        (truck_id, payment_method_id, total, at);
    """
    with conn.cursor() as cur:
        cur.execute(query)
        conn.commit()


if __name__ == "__main__":

    load_dotenv()

    upload_transaction_data(load_truck_data())
