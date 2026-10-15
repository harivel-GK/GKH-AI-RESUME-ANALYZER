# Customer Segmentation using K-Means Clustering

## Project Overview
Developed an end-to-end customer segmentation system using K-Means clustering, StandardScaler, PCA, and Streamlit. Determined optimal clusters using Elbow Method and Silhouette Score, generated business insights, and deployed an interactive dashboard for customer analytics.

## Features
- **Data Preprocessing**: Standard scaling and feature encoding.
- **Exploratory Data Analysis**: Histograms, heatmaps, and scatter plots.
- **Clustering**: K-Means with Elbow Method and Silhouette Score.
- **Dimensionality Reduction**: PCA visualization of clusters.
- **Business Insights**: Dynamic recommendations based on cluster profiles.
- **Deployment**: Interactive Streamlit dashboard.

## Technologies Used
- Python, Pandas, NumPy
- Scikit-Learn (K-Means, PCA, StandardScaler, Silhouette Score)
- Matplotlib, Seaborn
- Streamlit
- Joblib

## Installation Steps
1. Clone this repository.
2. Install dependencies:
   `pip install -r requirements.txt`

## How to Run
1. Train the model:
   `python train_model.py`
2. Run the Streamlit dashboard:
   `streamlit run app.py`
