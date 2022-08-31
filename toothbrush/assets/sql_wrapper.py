# Postgres wrapper

import psycopg2
import pandas as pd
from uuid import uuid4
from typing import List, Optional


class SQLConnection:
    def __init__(
        self,
        dbname,
        user,
        password,
        host='database-data-eng-instance-1.c9gelistqio1.us-east-1.rds.amazonaws.com',
        port=5432,
    ):
        self.current_cursor = str(uuid4())
        self.db_name = f''
        self.auth = dict(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port,
        )

    def q(self, query: str):
        with psycopg2.connect(**self.auth) as conn:
            return pd.read_sql(query, conn)
