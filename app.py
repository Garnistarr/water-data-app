# app.py
import json
import uuid
from datetime import datetime, timezone

import streamlit as st
import streamlit_authenticator as stauth
from google.cloud import bigquery
from google.oauth2 import service_account

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Water Treatment App",
    page_icon="💧",
    layout="centered",
)

# -----------------------------
# Helpers
# -----------------------------
def normalize_email(value: str) -> str:
    return (value or "").strip().lower()

def coerce_wtws(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return parsed
        except Exception:
            pass
        return [w.strip() for w in value.split(",") if w.strip()]
    return []

def email_key_variants(email: str):
    e_orig = (email or "").strip()
    e_low = e_orig.lower()
    variants = {
        e_orig, e_low,
        e_orig + " ", " " + e_orig, " " + e_orig + " ",
        e_low + " ", " " + e_low, " " + e_low + " ",
    }
    return {v for v in variants if v}

# -----------------------------
# BigQuery Connection
# -----------------------------
@st.cache_resource
def get_db_connection():
    try:
        creds_json_str = st.secrets["GCP_CREDENTIALS"]
        creds_dict = json.loads(creds_json_str)
        credentials = service_account.Credentials.from_service_account_info(creds_dict)
        client = bigquery.Client(credentials=credentials, project=credentials.project_id)
        return client
    except Exception as e:
        st.error("Could not connect to BigQuery. Check GCP_CREDENTIALS in secrets.")
        st.exception(e)
        st.stop()

client = get_db_connection()

# -----------------------------
# Load users from BigQuery
# -----------------------------
@st.cache_data(ttl=600)
def fetch_users_from_db():
    query = """
        SELECT email, name, password, role, assigned_wtws
        FROM protapp_water_data.user_permissions
    """
    try:
        df = client.query(query).to_dataframe()
        creds = {"usernames": {}}

        for _, row in df.iterrows():
            email_orig = (row.get("emai_




