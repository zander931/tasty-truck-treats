import streamlit as st
import pandas as pd


@st.cache_data
def load_data():

    data = pd.read_csv('data/truck_hist_cleaned.csv')
    data['timestamp'] = pd.to_datetime(data['timestamp'])
    data['truck_id'] = pd.to_numeric(data['truck_id'])
    data['total'] = pd.to_numeric(data['total'])
    return data


if __name__ == '__main__':

    st.title('Total number of transactions for each truck')
    data = load_data()

    transaction_counts = data.groupby(
        'truck_id').size().reset_index(name='num_transactions')

    st.bar_chart(transaction_counts)
