import streamlit as st

st.set_page_config(page_title="Sales Analytics Dashboard", layout="wide", page_icon="📊")

st.title("📊 Sales Analytics Dashboard")
st.markdown("""
Welcome to the End-to-End Sales Analytics Portfolio Project.

Use the sidebar to navigate through the application:
- **Dashboard**: High-level KPIs and Interactive Visualizations.
- **Upload Data**: Upload new raw sales datasets.
- **SQL Analysis**: Run custom SQL queries against the database.
- **Charts**: Deep dive into specific visual metrics.
- **AI Insights**: View LLM-generated business recommendations.
""")

st.info("👈 Please select a page from the sidebar to begin.")
