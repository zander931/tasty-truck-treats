# Tasty Truck Treats (T3) Pipeline

This project aims to extract, transform, and load data from **Tasty Truck Treats**, which includes _transactional data_, as well as _(master) metadata_.  
A database is designed to hold data within a **Star schema**, as a combination of `fact` and `dimension` tables. This schema is optimised to be lightweight, containing only the information _directly_ related to the event in the `fact` table, whereas the `dimension` tables store wider data about those events.  
This lightweight functionality is ideal for aggregate analysis on the event data, as the `fact` table is designed to handle high traffic and speed when querying the database.

## Database Model

![T3 ERD Star Schema](https://github.com/zander931/tasty-truck-treats/blob/main/images/T3_ERD.png?raw=true)

Above is the Entity Relationship Diagram for the T3 data, designed as a star schema.

## Files:

* **schema.sql**: Creates required database tables and seeds them with initial data
* **extract.py**: Functions to connect to an S3 and download relevant files
* **transform.py**: Functions to transform the data prior to uploading
* **load.py**: Functions to load csv data, and upload transformed data
* **pipeline.py**: Manages the ETL process from extraction from S3 to uploading to the database
* **logger_config.py**: Handles configuration for logging
* **analysis.ipynb**: connects to, and explores the database for EDA on the transactional truck data

## Data

The data for T3 includes the truck transactional data `.parquet` files, which are combined, cleaned, and transformed into a `truck_hist_cleaned.csv` file.  
Also, the master data sourced from S3 is the `details.xlsx` file that contains details of the trucks, as well as location data.  
The data is loaded into a remote **MySQL** database.

## Running the project files

The process is centrally controlled via the _`pipeline.py`_ script. The following should display optional options to control the output of the process, including **where the output should be logged**.

```bash
python3 pipeline.py --help
```

**Connecting** to the remote database should be simple with a `.env` file, containing sensitive login credentials.  
```bash
bash connect.sh
```
Similarly, **resetting** the database is as simple as running the command below:
```bash
bash reset.sh schema.sql
```

### `.env` file requirements

An `.env` file is required to hold sensitive configuration information to connect to the S3 bucket. The `.env` file should also hold to configuration details to connect to the database.

For connecting to the S3 bucket, you will require:
```bash
AWS_ACCESS_KEY=XXXXX
AWS_SECRET_ACCESS_KEY=XXXXX
```

For connecting to the RDS database, you will require:
```bash
DB_HOST=XXXXX
DB_NAME=XXXXX
DB_PORT=XXXXX
DB_USER=XXXXX
DB_PASSWORD=XXXXX
```

## Database Views

A view has been pre-instantiated for ease of querying the database:
* **transaction_info**
```sql
SELECT * FROM transaction_info;
```

## Financial Dashboard wireframe design

![T3 Dashboard Wireframe](https://github.com/zander931/tasty-truck-treats/blob/main/images/T3_financial_dashboard_wireframe.jpg?raw=true)

### Recommendations

1. Truck #3 has the highest number of transactions (1444) and the highest total transaction value (£8470.56), indicating strong customer demand and operational efficiency. Ideally, further analysis should be done on this truck to find out what factors are optimising demand and efficiency, and hopefully translate this to the other trucks' strategies.

2. Truck #4 has the lowest number of transactions (283) and the lowest total transaction value (£770.17), showing it is underperforming both in terms of transaction volume and revenue generation. It also has the lowest average transaction value (£2.72), which could be a signal that the truck may be offering lower-priced items or has lower customer spending. In order to optimise this truck, Hiram might consider retraining staff, improve customer service, or redesigning the menu to make it more appealing. It could also be a consideration to investigate for any inefficiencies in operational costs compared to the other trucks.

3. Consider experimenting with price increases on popular menu items for trucks with lower average transaction values, to increase the average transaction value without affecting customer satisfaction, hoping to boost performance. Similarly, due to more than half of all transactions being paid in cash, you might consider offering discounts for card payments to encourage card usage. This analysis is based on the fact that significant cash usage may suggest that customers are more likely to spend smaller amounts on each transaction, and hopefully implementing this discount on card purchases may possibly increase average transaction value for the lower-performing trucks.