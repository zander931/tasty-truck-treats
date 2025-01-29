"""Script for generating HTML for the daily report."""
# pylint: disable=line-too-long

from datetime import date, timedelta
import json
import logging
from dotenv import load_dotenv

from report_data import get_db_connection, define_queries, get_data, download_json


def setup_logging(output: str, filename="daily_report.log", level=20):
    """Setup the basicConfig."""
    log_format = "{asctime} - {levelname} - {message}"
    log_datefmt = "%Y-%m-%d %H:%M"
    if output == "file":
        logging.basicConfig(
            filename=filename,
            encoding="utf-8",
            filemode="a",
            level=level,
            format=log_format,
            style="{",
            datefmt=log_datefmt
        )
        logging.info("Logging to file: %s", filename)
    else:
        logging.basicConfig(
            level=level,
            format=log_format,
            style="{",
            datefmt=log_datefmt
        )
        logging.info("Logging to console.")


def get_json_data(the_date: str):
    """Load json query data."""

    with open(f'report_data_{the_date}.json', 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_table(headers, rows):
    """Create a table."""

    table = "<table border='1' style='border-collapse: collapse; width: 100%; margin-bottom: 20px;'>"
    table += "<tr>"

    for header in headers:
        table += f"<th style='padding: 10px; background-color: #f2f2f2; text-align: left;'>{
            header}</th>"
    table += "</tr>"

    for row in rows:
        table += "<tr>"
        for cell in row:
            table += f"<td style='padding: 10px; text-align: left;'>{
                cell}</td>"
        table += "</tr>"
    table += "</table>"
    return table


def write_head():
    """Writes the header of the HTML file."""

    return """
    <html>
    <head>
        <title>Daily Report</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
            }
            h1 {
                color: #2c3e50;
            }
            h2 {
                color: #34495e;
            }
        </style>
    </head>
    <body>
        <h1>Daily Report: Key Metrics</h1>
    
    """


def write_total_revenue(total_rev: list[dict]):
    """Total revenue data."""

    html_content = "<h2>Total Revenue</h2>"
    total_revenue_headers = ['Date', 'Total Revenue']
    total_revenue_rows = [
        [entry['date'], f"£{entry['total']:.2f}"] for entry in total_rev]
    html_content += generate_table(total_revenue_headers, total_revenue_rows)
    logging.info("Total revenue written successfully")
    return html_content


def write_revenue_by_truck(rev_by_truck: list[dict]):
    """Total revenue by truck."""

    html_content = "<h2>Revenue by Truck</h2>"
    revenue_by_truck_headers = ['Truck ID', 'FSA Rating',
                                'Total Revenue', 'Transaction Count', 'Avg Transaction Amount']
    revenue_by_truck_rows = [
        [entry['truck_id'], entry['fsa_rating'], f"£{
            entry['total']:.2f}", entry['count'], f"£{entry['avg_amount']:.2f}"]
        for entry in rev_by_truck
    ]
    html_content += generate_table(revenue_by_truck_headers,
                                   revenue_by_truck_rows)
    logging.info("Total revenue by truck written successfully")
    return html_content


def write_payment_method(pay_method: list[dict]):
    """Payment method distribution."""

    html_content = "<h2>Payment Method Breakdown</h2>"
    payment_method_headers = ['Payment Method', 'Total Revenue']
    payment_method_rows = [
        [entry['payment_method'], f"£{entry['total']:.2f}"] for entry in pay_method
    ]
    html_content += generate_table(payment_method_headers, payment_method_rows)
    logging.info("Payment method distribution written successfully")
    return html_content


def write_payment_method_by_truck(pay_method_by_truck: list[dict]):
    """Payment method distribution by truck"""

    html_content = "<h2>Payment Method by Truck</h2>"
    payment_method_by_truck_headers = [
        'Truck ID', 'Payment Method', 'Total Revenue', 'Avg Transaction Amount']
    payment_method_by_truck_rows = [
        [entry['truck_id'], entry['payment_method'], f"£{
            entry['total']:.2f}", f"£{entry['avg_amount']:.2f}"]
        for entry in pay_method_by_truck
    ]
    html_content += generate_table(payment_method_by_truck_headers,
                                   payment_method_by_truck_rows)
    logging.info("Payment method distribution by truck written successfully")
    return html_content


def download_html(content: str, the_date: str):
    """Write HTML content to a file."""

    content += """
    </body>
</html>
    """

    with open(f'daily_report_{the_date}.html', 'w', encoding='utf-8') as html_file:
        html_file.write(content)

    logging.info(
        "HTML report has been generated and saved as 'daily_report_%s.html'.", the_date)


def lambda_handler(event, context):
    """AWS Lambda handler function."""
    try:
        setup_logging("console")
        load_dotenv()

        conn = get_db_connection()
        logging.info("Established connection with MySQL.")
        queries, titles = define_queries()

        info = get_data(conn, queries, titles)
        logging.info("Loaded daily info.")
        conn.close()

        HEAD = write_head()
        total_revenue = write_total_revenue(info['total_revenue'])
        revenue_by_truck = write_revenue_by_truck(info['revenue_by_truck'])
        payment_method = write_payment_method(info['payment_method'])
        pay_meth_by_truck = write_payment_method_by_truck(
            info['payment_method_by_truck'])
        html = HEAD + '\n\n' + total_revenue + '\n\n' + revenue_by_truck + '\n\n' + \
            payment_method + '\n\n' + pay_meth_by_truck

        return {
            'status_code': 200,
            'body': json.dumps({'html_report': html})
        }
    except Exception as e:
        logging.error(f"Error generating report: {e}")
        return {
            'status_code': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }


if __name__ == '__main__':

    setup_logging("console")
    load_dotenv()
    conn = get_db_connection()
    logging.info("Established connection with MySQL.")
    queries, titles = define_queries()
    info = get_data(conn, queries, titles)
    conn.close()
    download_json(info)
    logging.info("Loaded daily info.")

    yesterday = date.today() - timedelta(days=1)
    form_date = yesterday.strftime('%Y-%m-%d')
    info = get_json_data(form_date)

    HEAD = write_head()
    total_revenue = write_total_revenue(info['total_revenue'])
    revenue_by_truck = write_revenue_by_truck(info['revenue_by_truck'])
    payment_method = write_payment_method(info['payment_method'])
    pay_meth_by_truck = write_payment_method_by_truck(
        info['payment_method_by_truck'])
    html = HEAD + '\n\n' + total_revenue + '\n\n' + revenue_by_truck + '\n\n' + \
        payment_method + '\n\n' + pay_meth_by_truck
    download_html(html, form_date)
