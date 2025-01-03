import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import urllib
from babel.numbers import format_currency


class DataAnalyze:
    def __init__(self, df):
        self.df = df

    def create_daily_orders_df(self):
        daily_orders_df = self.df.resample(rule='D', on='order_approved_at').agg({
            "order_id": "nunique",
            "payment_value": "sum"
        })
        daily_orders_df = daily_orders_df.reset_index()
        daily_orders_df.rename(columns={
            "order_id": "order_count",
            "payment_value": "revenue"
        }, inplace=True)
        
        return daily_orders_df
    
    def create_sum_spend_df(self):
        sum_spend_df = self.df.resample(rule='D', on='order_approved_at').agg({
            "payment_value": "sum"
        })
        sum_spend_df = sum_spend_df.reset_index()
        sum_spend_df.rename(columns={
            "payment_value": "total_spend"
        }, inplace=True)

        return sum_spend_df

    def create_sum_order_items_df(self):
        sum_order_items_df = self.df.groupby("product_category_name_english")["product_id"].count().reset_index()
        sum_order_items_df.rename(columns={
            "product_id": "product_count"
        }, inplace=True)
        sum_order_items_df = sum_order_items_df.sort_values(by='product_count', ascending=False)

        return sum_order_items_df

    def create_bystate_df(self):
        bystate_df = self.df.groupby(by="customer_state").customer_id.nunique().reset_index()
        bystate_df.rename(columns={
            "customer_id": "customer_count"
        }, inplace=True)
        most_common_state = bystate_df.loc[bystate_df['customer_count'].idxmax(), 'customer_state']
        bystate_df = bystate_df.sort_values(by='customer_count', ascending=False)

        return bystate_df, most_common_state
    
    def create_bycity_df(self):
        bycity_df = self.df.groupby(by="customer_city").customer_id.nunique().reset_index()
        bycity_df.rename(columns={
            "customer_id": "customer_count"
        }, inplace=True)
        most_common_city = bycity_df.loc[bycity_df['customer_count'].idxmax(), 'customer_city']
        bycity_df = bycity_df.sort_values(by='customer_count', ascending=False)

        return bycity_df, most_common_city

    def create_order_status(self):
        order_status_df = self.df["order_status"].value_counts().sort_values(ascending=False)
        most_common_status = order_status_df.idxmax()

        return order_status_df, most_common_status


# Dataset
datetime = ["order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date", "order_purchase_timestamp", "shipping_limit_date"]
all_df = pd.read_csv("all_data.csv")
all_df.sort_values(by="order_approved_at", inplace=True)
all_df.reset_index(inplace=True)

for col in datetime:
    all_df[col] = pd.to_datetime(all_df[col])

min_date = all_df["order_approved_at"].min()
max_date = all_df["order_approved_at"].max()

# Sidebar
with st.sidebar:
    # Title
    st.title("Laurensia Vira Farindra")

    # Date Range
    start_date, end_date = st.date_input(
        label="Pilih Rentang Waktu",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

# Main
main_df = all_df[(all_df["order_approved_at"] >= str(start_date)) & 
                 (all_df["order_approved_at"] <= str(end_date))]

function = DataAnalyze(main_df)

daily_orders_df = function.create_daily_orders_df()
sum_spend_df = function.create_sum_spend_df()
sum_order_items_df = function.create_sum_order_items_df()
state, most_common_state = function.create_bystate_df()
city, most_common_city = function.create_bycity_df()
order_status, common_status = function.create_order_status()

# Title
st.header("E-Commerce Dashboard: Convenience_store")

# Daily Orders
st.subheader("Order Harian")

col1, col2 = st.columns(2)

with col1:
    total_order = daily_orders_df["order_count"].sum()
    st.markdown(f"Total Order: **{total_order}**")

with col2:
    total_revenue = format_currency(daily_orders_df["revenue"].sum(), "IDR", locale="id_ID")
    st.markdown(f"Total Revenue: **{total_revenue}**")

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(
    daily_orders_df["order_approved_at"],
    daily_orders_df["order_count"],
    marker="o",
    linewidth=2,
    color="#FFC0CB"
)
ax.tick_params(axis="x", rotation=45)
ax.tick_params(axis="y", labelsize=15)
st.pyplot(fig)

# Customer Demographic
st.subheader("Demografis Customer")
tab1, tab2, tab3 = st.tabs(["Negara Bagian", "Kota", "Status Order"])

with tab1:
    most_common_state = state.customer_state.value_counts().index[0]
    st.markdown(f"Negara Bagian dengan Customer Terbanyak: **{most_common_state}**")

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x=state.customer_state.value_counts().index,
                y=state.customer_count.values, 
                data=state,
                palette=["#FF0000" if score == most_common_state else "#D3D3D3" for score in state.customer_state.value_counts().index]
                    )

    plt.title("Jumlah Customer Berdasarkan Negara Bagian", fontsize=15)
    plt.xlabel("Negara Bagian")
    plt.ylabel("Jumlah Customer")
    plt.xticks(fontsize=12)
    st.pyplot(fig)

with tab2:
    # Mendapatkan 10 kota dengan customer terbanyak
    top_10_cities = city.customer_city.value_counts().head(10)
    
    most_common_city = top_10_cities.index[0]
    st.markdown(f"Kota dengan Customer Terbanyak: **{most_common_city}**")

    # Membuat plot
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(
        x=top_10_cities.index,  # Top 10 city names
        y=top_10_cities.values, # Top 10 city counts
        palette=["#FF0000" if score == most_common_city else "#D3D3D3" for score in top_10_cities.index]
    )
    
    # Customize plot appearance
    plt.xticks(rotation=45)
    plt.xlabel("Kota")
    plt.ylabel("Jumlah Customer")
    plt.title("Top 10 Kota dengan Customer Terbanyak")
    st.pyplot(fig)

with tab3:
    common_status_ = order_status.value_counts().index[0]
    st.markdown(f"Order Status Terbanyak: **{common_status_}**")

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x=order_status.index,
                y=order_status.values,
                order=order_status.index,
                palette=["#FF0000" if score == common_status else "#D3D3D3" for score in order_status.index]
                )
    
    plt.title("Order Status", fontsize=15)
    plt.xlabel("Status")
    plt.ylabel("Jumlah")
    plt.xticks(fontsize=12)
    st.pyplot(fig)

st.caption('by Laurensia Vira Farindra - 2024')