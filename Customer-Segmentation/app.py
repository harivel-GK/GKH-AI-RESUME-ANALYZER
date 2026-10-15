import os
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA

# ==========================================
# 1. HELPER FUNCTIONS
# ==========================================

def preprocess_data(df):
    df_processed = df.copy()
    if 'Genre' in df_processed.columns:
        df_processed.rename(columns={'Genre': 'Gender'}, inplace=True)
    if 'CustomerID' in df_processed.columns:
        df_processed.drop('CustomerID', axis=1, inplace=True)
    
    if 'Gender' in df_processed.columns:
        df_processed['Gender'] = df_processed['Gender'].map({'Male': 0, 'Female': 1})
        
    features = ['Annual Income (k$)', 'Spending Score (1-100)']
    X = df_processed[features]
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    return df_processed, X, X_scaled, scaler

def cluster_summary(df):
    cols = ['Annual Income (k$)', 'Spending Score (1-100)', 'Age', 'Cluster']
    available_cols = [col for col in cols if col in df.columns]
    # Guarantee we return a dataframe where 'Cluster' is a standard column
    return df[available_cols].groupby('Cluster').mean().round(2).reset_index()

def generate_insights(cluster_summary_df):
    insights = {}
    for _, row in cluster_summary_df.iterrows():
        cluster = int(row['Cluster'])
        income = row.get('Annual Income (k$)', 0)
        spending = row.get('Spending Score (1-100)', 0)
        
        if income >= 60 and spending >= 60:
            profile = "High Income + High Spending"
            rec = "Premium Membership Offers"
        elif income >= 60 and spending < 60:
            profile = "High Income + Low Spending"
            rec = "Discount Campaigns"
        elif income < 60 and spending >= 60:
            profile = "Low Income + High Spending"
            rec = "Loyalty Programs"
        else:
            profile = "Low Income + Low Spending"
            rec = "Basic Marketing"
            
        insights[cluster] = {
            'profile': profile,
            'recommendation': rec
        }
    return insights

def plot_elbow_method(wcss_values, max_clusters):
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(range(1, max_clusters + 1), wcss_values, marker='o', linestyle='--')
    ax.set_title('Elbow Method')
    ax.set_xlabel('Number of Clusters')
    ax.set_ylabel('WCSS')
    return fig

def plot_clusters(X, labels, centroids):
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.scatterplot(x=X.iloc[:, 0], y=X.iloc[:, 1], hue=labels, palette='viridis', ax=ax, s=100)
    ax.scatter(centroids[:, 0], centroids[:, 1], s=300, c='red', label='Centroids', marker='X')
    ax.set_title('Customer Segments')
    ax.legend()
    return fig

def plot_pca_clusters(X_scaled, labels):
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)
    
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.scatterplot(x=X_pca[:, 0], y=X_pca[:, 1], hue=labels, palette='coolwarm', ax=ax, s=100)
    ax.set_title('PCA Cluster Visualization')
    ax.set_xlabel('Principal Component 1')
    ax.set_ylabel('Principal Component 2')
    return fig


# ==========================================
# 2. STREAMLIT APPLICATION
# ==========================================

st.set_page_config(page_title="Customer Segmentation Dashboard", layout="wide")
st.title("Customer Segmentation Dashboard")

# Sidebar
st.sidebar.header("Configuration")
uploaded_file = st.sidebar.file_uploader("Upload Dataset", type=["csv"])

if uploaded_file is None:
    default_path = os.path.join('data', 'Mall_Customers.csv')
    if os.path.exists(default_path):
        df = pd.read_csv(default_path)
    else:
        st.warning("Please upload a CSV file.")
        st.stop()
else:
    df = pd.read_csv(uploaded_file)

n_clusters = st.sidebar.slider("Select Number of Clusters", min_value=2, max_value=10, value=5)
run_btn = st.sidebar.button("Run Clustering")

# Section 1. Dataset Overview
st.header("1. Dataset Overview")
col1, col2, col3 = st.columns(3)
col1.metric("Shape", f"{df.shape[0]} rows, {df.shape[1]} cols")
col2.metric("Missing Values", df.isnull().sum().sum())
col3.metric("Features", len(df.columns))

st.subheader("Top 10 Rows")
st.dataframe(df.head(10))

st.subheader("Data Types")
st.dataframe(df.dtypes.astype(str).reset_index().rename(columns={"index": "Column", 0: "Type"}))


# Section 2. EDA
st.header("2. Exploratory Data Analysis")
df_processed, X, X_scaled, scaler = preprocess_data(df)

col1, col2 = st.columns(2)
with col1:
    st.subheader("Distribution Plot")
    fig, ax = plt.subplots()
    sns.histplot(df_processed['Annual Income (k$)'], kde=True, ax=ax)
    st.pyplot(fig)

with col2:
    st.subheader("Correlation Heatmap")
    fig, ax = plt.subplots()
    sns.heatmap(df_processed.corr(numeric_only=True), annot=True, cmap='coolwarm', ax=ax)
    st.pyplot(fig)

st.subheader("Scatter Plot (Income vs Spending)")
fig, ax = plt.subplots()
hue_col = 'Gender' if 'Gender' in df_processed.columns else ('Genre' if 'Genre' in df_processed.columns else None)
if hue_col:
    sns.scatterplot(x='Annual Income (k$)', y='Spending Score (1-100)', hue=hue_col, data=df_processed, ax=ax)
else:
    sns.scatterplot(x='Annual Income (k$)', y='Spending Score (1-100)', data=df_processed, ax=ax)
st.pyplot(fig)


# Section 3. Clustering Analysis
if run_btn or True:
    st.header("3. Clustering Analysis")
    
    wcss = []
    for i in range(1, 11):
        km = KMeans(n_clusters=i, init='k-means++', random_state=42)
        km.fit(X_scaled)
        wcss.append(km.inertia_)
        
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Elbow Method Graph")
        fig = plot_elbow_method(wcss, 10)
        st.pyplot(fig)
        
    kmeans = KMeans(n_clusters=n_clusters, init='k-means++', random_state=42)
    labels = kmeans.fit_predict(X_scaled)
    df_processed['Cluster'] = labels
    
    sil_score = silhouette_score(X_scaled, labels)
    
    with col2:
        st.subheader("Silhouette Score")
        st.metric("Silhouette Score", round(sil_score, 3))


    # Section 4. Cluster Visualization
    st.header("4. Cluster Visualization")
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("PCA Plot")
        fig = plot_pca_clusters(X_scaled, labels)
        st.pyplot(fig)
        
    with col4:
        st.subheader("Cluster Scatter Plot")
        centroids = kmeans.cluster_centers_ 
        centroids_orig = scaler.inverse_transform(centroids)
        fig = plot_clusters(X, labels, centroids_orig)
        st.pyplot(fig)
        

    # Section 5. Statistics & Insights
    st.header("5. Cluster Statistics & Business Recommendations")
    
    summary = cluster_summary(df_processed)
    insights = generate_insights(summary)
    
    for cluster_id in sorted(insights.keys()):
        st.subheader(f"Cluster {cluster_id}")
        stat_col, insight_col = st.columns(2)
        
        with stat_col:
            st.markdown(f"**Income:** {summary[summary['Cluster'] == cluster_id]['Annual Income (k$)'].values[0]:.0f}k")
            st.markdown(f"**Spending:** {summary[summary['Cluster'] == cluster_id]['Spending Score (1-100)'].values[0]:.0f}")
                
        with insight_col:
            st.markdown(f"**Profile:** {insights[cluster_id]['profile']}")
            st.markdown(f"**Recommendation:** {insights[cluster_id]['recommendation']}")
        
        st.divider()

    # Model Saving
    os.makedirs('models', exist_ok=True)
    joblib.dump(kmeans, os.path.join('models', 'kmeans_model.pkl'))
    joblib.dump(scaler, os.path.join('models', 'scaler.pkl'))
