import streamlit as st
import streamlit_authenticator as stauth
from google.cloud import bigquery
from google.oauth2 import service_account
import json

# --- Page Configuration ---
st.set_page_config(
    page_title="Water Treatment App",
    page_icon="💧",
    layout="centered"
)

st.title("🔴 App Debugging Mode")

# --- BigQuery Connection Test ---
st.header("1. Checking for Secret")
if "GCP_CREDENTIALS" in st.secrets:
    st.success("✅ GCP_CREDENTIALS secret found.")
else:
    st.error("❌ GCP_CREDENTIALS secret NOT found. Check the name in your secrets settings.")
    st.stop()

st.header("2. Trying to Connect to BigQuery")
try:
    creds_json_str = st.secrets["GCP_CREDENTIALS"]
    
    # Let's check if the string looks like a valid JSON
    st.write("Checking if secret is valid JSON...")
    creds_dict = json.loads(creds_json_str)
    st.success("✅ Secret was successfully parsed as JSON.")
    
    # Now, try to authenticate with it
    st.write("Attempting to authenticate with Google Cloud...")
    creds = service_account.Credentials.from_service_account_info(creds_dict)
    client = bigquery.Client(credentials=creds, project=creds.project_id)
    st.success("✅ Successfully authenticated and created BigQuery client!")
    
    # --- If successful, we can remove the debugging code later ---

except Exception as e:
    st.error("❌ An error occurred during connection:")
    st.exception(e) # This will print the full detailed error
