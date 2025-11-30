import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import os
import sys
from pathlib import Path

# Add app modules to path for importing services
sys.path.append(str(Path(__file__).parent.parent / "app"))

# Configuration
API_URL = os.getenv("ML_API_URL", "http://127.0.0.1:8000")

st.set_page_config(
    page_title="ML Dashboard",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 ML Dashboard")
st.markdown("Machine Learning Service Dashboard with S3 Storage")

# ---- Service Status ----
st.header("📊 Service Status")

col1, col2, col3 = st.columns(3)

with col1:
    try:
        health_response = requests.get(f"{API_URL}/health", timeout=5)
        if health_response.status_code == 200:
            st.success("✅ API Service: Online")
            health_data = health_response.json()
            st.json(health_data)
        else:
            st.error("❌ API Service: Error")
    except requests.exceptions.RequestException:
        st.error("❌ API Service: Offline")

with col2:
    # Check S3/MinIO status
    s3_bucket = os.getenv("S3_BUCKET", "ml-datasets-bucket")
    s3_endpoint = os.getenv("S3_ENDPOINT_URL", "http://localhost:9000")
    st.info(f"🗄️ S3 Storage: {s3_bucket}")
    st.write(f"Endpoint: {s3_endpoint}")

with col3:
    # Show environment info
    st.info("🔧 Environment")
    st.write(f"API URL: {API_URL}")
    st.write(f"S3 Bucket: {s3_bucket}")

st.divider()

# ---- Dataset Management ----
st.header("📁 Dataset Management")

# Dataset upload
st.subheader("Upload Dataset")
uploaded_file = st.file_uploader(
    "Choose a CSV or JSON file",
    type=["csv", "json"],
    help="Upload datasets that will be stored in S3"
)

if uploaded_file is not None:
    if st.button("Upload Dataset"):
        with st.spinner("Uploading to S3..."):
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                response = requests.post(f"{API_URL}/datasets/upload", files=files)

                if response.status_code == 200:
                    result = response.json()
                    st.success(f"✅ Dataset '{result['filename']}' uploaded successfully to S3!")
                else:
                    st.error(f"❌ Upload failed: {response.text}")
            except requests.exceptions.RequestException as e:
                st.error(f"❌ Connection error: {e}")

st.divider()

# Dataset list
st.subheader("Available Datasets")

if st.button("🔄 Refresh Dataset List"):
    try:
        response = requests.get(f"{API_URL}/datasets/")
        if response.status_code == 200:
            datasets = response.json()["datasets"]

            if datasets:
                st.success(f"Found {len(datasets)} datasets in S3:")

                # Display as a table
                df = pd.DataFrame({"Dataset Name": datasets})
                st.dataframe(df, use_container_width=True)

                # Dataset preview
                selected_dataset = st.selectbox("Select dataset to preview:", datasets)

                if selected_dataset and st.button("Preview Dataset"):
                    st.info(f"Showing preview of: {selected_dataset}")
                    # Note: We'd need an API endpoint to download/preview datasets
                    st.write("Dataset preview functionality can be added by implementing a download endpoint")

            else:
                st.info("No datasets found in S3 storage")
        else:
            st.error(f"❌ Failed to fetch datasets: {response.text}")

    except requests.exceptions.RequestException as e:
        st.error(f"❌ Connection error: {e}")

st.divider()

# ---- Model Management ----
st.header("🧠 Model Management")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Available Model Types")
    try:
        # This would need a model types endpoint
        model_types = ["logistic_regression", "random_forest"]
        for model_type in model_types:
            st.write(f"• {model_type}")
    except:
        st.error("Could not fetch model types")

with col2:
    st.subheader("Trained Models")
    if st.button("🔄 Refresh Models"):
        try:
            # This would need a models list endpoint
            st.info("Model listing functionality can be added by implementing models API")
        except:
            st.error("Could not fetch models")

st.divider()

# ---- System Information ----
st.header("ℹ️ System Information")

info_col1, info_col2 = st.columns(2)

with info_col1:
    st.subheader("Configuration")
    config_info = {
        "API URL": API_URL,
        "S3 Bucket": os.getenv("S3_BUCKET", "Not set"),
        "S3 Endpoint": os.getenv("S3_ENDPOINT_URL", "Not set"),
        "AWS Region": os.getenv("AWS_REGION", "Not set"),
    }

    for key, value in config_info.items():
        st.write(f"**{key}:** {value}")

with info_col2:
    st.subheader("Quick Actions")

    if st.button("🧪 Test S3 Connection"):
        st.info("S3 connection test functionality can be integrated")

    if st.button("📊 Show System Stats"):
        st.info("System statistics can be added via API endpoints")

# Footer
st.divider()
st.markdown(
    """
    <div style='text-align: center'>
        <p>🚀 ML Service with S3 Storage • Built with Streamlit</p>
    </div>
    """,
    unsafe_allow_html=True
)

# ---- List datasets ----
st.header("Available datasets")
datasets = requests.get(f"{API_URL}/datasets").json()
st.write(datasets)

# ---- Train model ----
st.header("Train a model")

model_type = st.selectbox("Model type", ["logistic_regression", "random_forest"])
dataset_name = st.text_input("Dataset file name (e.g., iris.csv)")
target_column = st.text_input("Target column name")

params_raw = st.text_area("Model parameters (Python dict)", value="{}")

if st.button("Train"):
    try:
        params = eval(params_raw)  # простое решение в рамках учебного задания
        payload = {
            "model_type": model_type,
            "dataset_name": dataset_name,
            "target_column": target_column,
            "params": params,
        }
        resp = requests.post(f"{API_URL}/models/train", json=payload)
        st.write(resp.json())
    except Exception as e:
        st.error(str(e))

# ---- List models ----
st.header("Available models")
models = requests.get(f"{API_URL}/models").json()
st.write(models)

# ---- Predict ----
st.header("Predict")

model_id = st.text_input("Model ID for prediction")
features_raw = st.text_area("Features (list of dicts)", value="[{}]")

if st.button("Predict"):
    try:
        features = eval(features_raw)
        payload = {"features": features}
        resp = requests.post(f"{API_URL}/models/" + model_id + "/predict", json=payload)
        st.write(resp.json())
    except Exception as e:
        st.error(str(e))