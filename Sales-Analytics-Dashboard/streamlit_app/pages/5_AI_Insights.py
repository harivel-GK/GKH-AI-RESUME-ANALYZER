import streamlit as st
from scripts.ai_insights import generate_insights

st.set_page_config(page_title="AI Insights")
st.title("🤖 AI-Generated Business Insights")

st.markdown("Click the button below to generate a natural language summary and recommendations based on the current dataset.")

if st.button("Generate Insights"):
    with st.spinner("Analyzing data and generating insights via LLM..."):
        insights = generate_insights()
        st.markdown("### Executive Summary & Recommendations")
        st.write(insights)
