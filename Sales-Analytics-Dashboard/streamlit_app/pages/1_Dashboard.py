import streamlit as st
import pandas as pd
import plotly.express as px
from utils.helpers import load_csv_data

st.set_page_config(page_title="Dashboard", layout="wide")
st.title("📈 Executive Dashboard")

try:
    df = load_csv_data("processed_sales.csv", "processed")
    
    st.subheader("Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Revenue", f"")
    col2.metric("Total Orders", f"{df['OrderID'].nunique():,}")
    col3.metric("Average Order Value", f"")
    col4.metric("Products Sold", f"{df['Quantity'].sum():,}")

    st.divider()

    colA, colB = st.columns(2)
    with colA:
        st.subheader("Revenue by Region")
        fig1 = px.bar(df.groupby("Region")["Revenue"].sum().reset_index(), x="Region", y="Revenue", color="Region")
        st.plotly_chart(fig1, use_container_width=True)

    with colB:
        st.subheader("Revenue Trend over Time")
        trend = df.groupby(["Year", "Month"])["Revenue"].sum().reset_index()
        trend["Date"] = pd.to_datetime(trend["Year"].astype(str) + "-" + trend["Month"].astype(str) + "-01")
        fig2 = px.line(trend, x="Date", y="Revenue", markers=True)
        st.plotly_chart(fig2, use_container_width=True)

except FileNotFoundError:
    st.error("Processed data not found. Please run the ETL pipeline first.")
