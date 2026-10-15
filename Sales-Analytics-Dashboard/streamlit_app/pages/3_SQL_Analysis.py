import streamlit as st
import pandas as pd
from database.database import get_engine

st.set_page_config(page_title="SQL Analysis")
st.title("🗄️ SQL Analysis")

st.markdown("Run custom SQL queries directly against the MySQL database.")

query = st.text_area("Enter your SQL query:", value="SELECT * FROM sales LIMIT 10;")

if st.button("Execute Query"):
    engine = get_engine()
    if engine:
        try:
            df = pd.read_sql(query, con=engine)
            st.dataframe(df)
            
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Download Results", csv, "query_results.csv", "text/csv")
        except Exception as e:
            st.error(f"Query Error: {e}")
    else:
        st.error("Database connection failed. Check your config.")
