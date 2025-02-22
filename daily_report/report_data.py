"""A script to retrieve the daily report data for stakeholders of T3."""

from datetime import date, timedelta
from decimal import Decimal
import json
from os import environ as ENV
from dotenv import load_dotenv
import pymysql.cursors
from pymysql.cursors import DictCursor
from pymysql.connections import Connection


def get_db_connection() -> Connection:
    """Establish connection to remote DB."""

    return pymysql.connect(host=ENV['DB_HOST'],
                           user=ENV['DB_USER'],
                           password=ENV['DB_PASSWORD'],
                           database=ENV['DB_NAME'],
                           port=int(ENV['DB_PORT']),
                           cursorclass=DictCursor)


def define_queries() -> tuple[list, list]:
    """Define queries and titles."""

    query_one = """
        SELECT 
            DATE(at) date,
            SUM(total) total
        FROM transaction_info
        WHERE DATE(at) = CURDATE() - INTERVAL 1 DAY;
    """

    query_two = """
        SELECT
            t.truck_name,
            t.fsa_rating,
            SUM(total) total,
            COUNT(transaction_id) count,
            ROUND(AVG(total),2) avg_amount
        FROM transaction_info
        JOIN DIM_Truck t USING(truck_id)
        WHERE DATE(at) = CURDATE() - INTERVAL 1 DAY
        GROUP BY truck_id
        ORDER BY truck_id ASC;
    """

    query_three = """
        SELECT
            payment_method,
            SUM(total) total
        FROM transaction_info
        WHERE DATE(at) = CURDATE() - INTERVAL 1 DAY
        GROUP BY payment_method;
    """

    query_four = """
        SELECT
            t.truck_name,
            payment_method,
            SUM(total) total,
            ROUND(AVG(total),2) avg_amount
        FROM transaction_info
        JOIN DIM_Truck t USING(truck_id)
        WHERE DATE(at) = CURDATE() - INTERVAL 1 DAY
        GROUP BY payment_method, truck_id
        ORDER BY truck_id ASC;
    """

    return ([query_one, query_two, query_three, query_four], ["total_revenue",
                                                              "revenue_by_truck",
                                                              "payment_method",
                                                              "payment_method_by_truck"
                                                              ]
            )


def get_data(con: Connection, query: list[str], title: list[str]) -> dict:
    """Retrieve data and reformat to dict."""

    results = {}
    with con.cursor() as cur:
        for i, q in enumerate(query):
            cur.execute(q)
            result = cur.fetchall()
            for row in result:
                for key, val in row.items():
                    if isinstance(val, date):
                        row[key] = val.strftime('%Y-%m-%d')
                    if isinstance(val, Decimal):
                        row[key] = float(val)
            results[title[i]] = result
    return results


def download_json(results: dict):
    """Download data as json file."""

    yesterday = date.today() - timedelta(days=1)
    form_date = yesterday.strftime('%Y-%m-%d')
    with open(f'report_data_{form_date}.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4)


if __name__ == '__main__':

    load_dotenv()
    conn = get_db_connection()
    [queries, titles] = define_queries()
    download_json(get_data(conn, queries, titles))
    conn.close()
