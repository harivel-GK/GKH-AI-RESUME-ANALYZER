import streamlit as st
import pandas as pd
from config.settings import RAW_DATA_DIR

st.set_page_config(page_title="Upload Data")
st.title("📤 Upload Raw Data")

uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.write("Data Preview:")
        st.dataframe(df.head())
        
        if st.button("Save to Raw Folder"):
            save_path = RAW_DATA_DIR / uploaded_file.name
            df.to_csv(save_path, index=False)
            st.success(f"File saved successfully to {save_path}")
    except Exception as e:
        st.error(f"Error reading file: {e}")
