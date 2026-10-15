# Sales Analytics Dashboard – End-to-End Portfolio Project

An enterprise-grade, end-to-end Data Engineering and Data Analytics pipeline. This project covers data generation, ETL processes, database management, SQL analytics, Python EDA, a multi-page Streamlit dashboard, Power BI specifications, and LLM-powered AI insights.

## Architecture

`mermaid
graph LR
    A[Raw Data] -->|ETL Python/Pandas| B[Cleaned Data]
    B -->|Feature Eng| C[Processed Data]
    C -->|SQLAlchemy| D[(MySQL Database)]
    D -->|SQL Queries| E[Streamlit Dashboard]
    C -->|API| F[OpenAI Insights]
    E --> G[End User]
`

## Setup & Installation

1. **Clone the repository**
2. **Create a Virtual Environment:**
   `ash
   python -m venv venv
   # On Windows: venv\Scripts\activate
   # On Mac/Linux: source venv/bin/activate
   `
3. **Install Dependencies:**
   `ash
   pip install -r requirements.txt
   `
4. **Environment Variables:**
   Copy .env.example to .env and fill in your MySQL credentials and OpenAI API Key.

## Usage Guide

1. **Generate Data:** python scripts/generate_data.py
2. **Clean Data:** python scripts/clean_data.py
3. **Feature Engineering:** python scripts/feature_engineering.py
4. **Load to Database:** python database/load_data.py
5. **Generate EDA Reports:** python scripts/eda.py
6. **Run Streamlit Dashboard:**
   `ash
   streamlit run streamlit_app/app.py
   `

## Modules Completed
- [x] Module 1: Folder Structure & Config
- [x] Module 2: Python ETL Pipeline
- [x] Module 3: MySQL Database Layer
- [x] Module 4: SQL Business Queries
- [x] Module 5: Exploratory Data Analysis (EDA)
- [x] Module 6: Streamlit Application
- [x] Module 7: Power BI Specification
- [x] Module 8: AI-Generated Insights
- [x] Module 9: Documentation

## LinkedIn / Resume Snippet
**Data Analytics Pipeline & Executive Dashboard**
*Designed and deployed an end-to-end data pipeline processing 5,000+ sales records. Built an automated ETL pipeline using Pandas and SQLAlchemy to load cleaned data into a MySQL data warehouse. Developed a multi-page interactive Streamlit dashboard featuring Plotly visualizations and integrated OpenAI's API to automatically generate executive insights. Created comprehensive SQL analysis queries and Power BI specifications.*
