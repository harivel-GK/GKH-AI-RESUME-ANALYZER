import streamlit as st
import plotly.express as px
from utils.helpers import load_csv_data

st.set_page_config(page_title="Charts")
st.title("📊 Detailed Charts")

try:
    df = load_csv_data("processed_sales.csv", "processed")
    
    st.subheader("Product Performance")
    prod_df = df.groupby("Product")["Revenue"].sum().reset_index().sort_values(by="Revenue", ascending=False)
    fig_prod = px.bar(prod_df, x="Revenue", y="Product", orientation="h", color="Product")
    st.plotly_chart(fig_prod, use_container_width=True)

    st.subheader("Discount Impact on Quantity")
    fig_disc = px.box(df, x="Discount", y="Quantity", color="Discount")
    st.plotly_chart(fig_disc, use_container_width=True)

except FileNotFoundError:
    st.error("Data not found.")
