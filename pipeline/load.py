"""A script that inserts bulk data efficiently."""

from os import environ as ENV
import pymysql.cursors
from pymysql.connections import Connection


def get_db_connection() -> Connection:
    """Returns a live connection to the MySQL database."""

    return pymysql.connect(host=ENV['DB_HOST'],
                           user=ENV['DB_USER'],
                           password=ENV['DB_PASSWORD'],
                           database=ENV['DB_NAME'],
                           port=int(ENV['DB_PORT']),
                           local_infile=True,
                           cursorclass=pymysql.cursors.DictCursor)


def upload_transaction_data(conn: Connection):
    """Uploads transaction data to the database."""

    query = """
        LOAD DATA LOCAL INFILE 'data/truck_hist_cleaned.csv'
        INTO TABLE FACT_Transaction
        FIELDS TERMINATED BY ','
        LINES TERMINATED BY '\n'
        IGNORE 1 LINES
        (at, payment_method_id, total, truck_id);
    """
    with conn.cursor() as cur:
        cur.execute(query)
    conn.commit()


if __name__ == "__main__":

    upload_transaction_data(get_db_connection())
