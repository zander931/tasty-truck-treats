"""A script to run a Streamlit dashboard for financial analysis."""

import streamlit as st
import altair as alt
import pandas as pd
from pymysql.connections import Connection

from load import get_db_connection


@st.cache_data
def get_data(_conn: Connection) -> pd.DataFrame:
    """Run a query on the database."""
    query = """
        SELECT
            ti.truck_name,
            ti.total,
            ti.payment_method,
            ti.at,
            t.fsa_rating
        FROM transaction_info ti
        JOIN DIM_Truck t USING(truck_id);
        """
    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()
    df = pd.DataFrame(rows, columns=[
        "truck_id", "truck_name", "total", "payment_method", "at", "fsa_rating"])
    df['total'] = df['total'].astype(float)
    df['truck_name'] = df['truck_name'].astype('category')
    df['payment_method'] = df['payment_method'].astype('category')
    return df


def homepage():
    st.title("T3 Financial Dashboard")

    st.sidebar.header("Filters")
    trucks = st.sidebar.multiselect(
        "Select Trucks", df['truck_name'].unique(), default=df['truck_name'].unique())
    payment_methods = st.sidebar.multiselect(
        "Select Payment Methods", df['payment_method'].unique(), default=df['payment_method'].unique())

    min_datetime = df['at'].min().to_pydatetime()
    max_datetime = df['at'].max().to_pydatetime()
    date_range = st.sidebar.slider(
        "Select Date Range", min_value=min_datetime, max_value=max_datetime,
        value=(min_datetime, max_datetime),
        step=pd.Timedelta(minutes=1),
        format="YYYY-MM-DD HH:mm"
    )
    fsa_ratings = st.sidebar.multiselect(
        "Select FSA Ratings", df['fsa_rating'].unique(), default=df['fsa_rating'].unique())

    start_datetime, end_datetime = date_range
    return df[
        (df['truck_name'].isin(trucks)) &
        (df['payment_method'].isin(payment_methods)) &
        (df['at'] >= start_datetime) &
        (df['at'] <= end_datetime) &
        (df['fsa_rating'].isin(fsa_ratings))
    ]


def total_revenue_bar(filtered_df: pd.DataFrame) -> alt.Chart:
    st.subheader("Total Revenue by Truck")
    truck_revenue = filtered_df.groupby(['truck_name', 'payment_method'])[
        'total'].sum().reset_index()

    return alt.Chart(truck_revenue).mark_bar().encode(
        x=alt.X('truck_name:N', title='Truck Name'),
        y=alt.Y('total:Q', title='Total Revenue'),
        color=alt.Color('payment_method:N', title='Payment Method')
    ).properties(width=800, height=500)


def transactions_time(filtered_df: pd.DataFrame) -> alt.Chart:
    st.subheader("Transactions over Time")
    filtered_df['date'] = filtered_df['at']
    tot = filtered_df.groupby(['date', 'truck_name', 'payment_method'])[
        'total'].count().reset_index()

    return alt.Chart(tot).mark_line().encode(
        x=alt.X('date:T', title='Date'),
        y=alt.Y('total:Q', title='Transaction Count'),
        color=alt.Color('truck_name:N', title='Truck')
    ).properties(width=800, height=500)


def payment_method_pie(filtered_df: pd.DataFrame) -> alt.Chart:
    st.subheader("Payment Method Distribution")
    pay_dist = filtered_df['payment_method'].value_counts().reset_index()
    pay_dist['percentage'] = round(
        (pay_dist['count'] / pay_dist['count'].sum()) * 100, 2)

    return alt.Chart(pay_dist).mark_arc().encode(
        theta=alt.Theta('count:Q', title='Total Payments'),
        color=alt.Color('payment_method:N', title='Payment Method'),
        tooltip=['payment_method:N',
                 'count:Q',
                 'percentage:Q']
    ).properties(width=500, height=500)


if __name__ == '__main__':

    conn = get_db_connection()
    df = get_data(conn)

    filtered_df = homepage()

    st.altair_chart(total_revenue_bar(filtered_df))
    st.altair_chart(transactions_time(filtered_df))
    st.altair_chart(payment_method_pie(filtered_df))
