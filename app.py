# app.py
import json
import uuid
from datetime import datetime, timezone

import pandas as pd  # optional, but harmless
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
# Small helpers
# -----------------------------
def normalize_email(value: str) -> str:
    """Trim and lowercase emails for case-insensitive matching."""
    return (value or "").strip().lower()

def coerce_wtws(value):
    """Ensure assigned_wtws is a list."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        # try JSON first, fallback to comma-separated
        try:
            maybe_json = json.loads(value)
            if isinstance(maybe_json, list):
                return maybe_json
        except Exception:
            pass
        return [w.strip() for w in value.split(",") if w.strip()]
    return []

# -----------------------------
# BigQuery Connection
# -----------------------------
@st.cache_resource
def get_db_connection():
    try:
        # In .streamlit/secrets.toml: GCP_CREDENTIALS = "<entire JSON string>"
        creds_json_str = st.secrets["GCP_CREDENTIALS"]
        creds_dict = json.loads(creds_json_str)
        credentials = service_account.Credentials.from_service_account_info(creds_dict)
        client = bigquery.Client(credentials=credentials, project=credentials.project_id)
        return client
    except Exception as e:
        st.error("Could not connect to BigQuery. Check GCP_CREDENTIALS in Secrets.")
        st.exception(e)
        st.stop()

client = get_db_connection()

# -----------------------------
# Load users from BigQuery
# -----------------------------
@st.cache_data(ttl=600)
def fetch_users_from_db():
    query = """
        SELECT
          email,
          name,
          password,
          role,
          assigned_wtws
        FROM protapp_water_data.user_permissions
    """
    try:
        df = client.query(query).to_dataframe()

        creds = {"usernames": {}}

        for _, row in df.iterrows():
            email_orig = (row.get("email") or "").strip()
            if not email_orig:
                continue  # skip invalid rows

            email_norm = normalize_email(email_orig)

            user_block = {
                "email": email_orig,                             # shown by the library
                "name": row.get("name") or email_orig,           # display name
                "password": row.get("password") or "",           # prefer hashed
                "role": row.get("role") or "Process Controller",
                "wtws": coerce_wtws(row.get("assigned_wtws")),
            }

            # Map both original and normalized emails to the same user dict
            creds["usernames"][email_orig] = user_block
            creds["usernames"][email_norm] = user_block

        return creds

    except Exception as e:
        st.error("Could not fetch user data from BigQuery.")
        st.exception(e)
        return {"usernames": {}}

users_from_db = fetch_users_from_db()

# -----------------------------
# Authentication
# -----------------------------
if not users_from_db or not users_from_db.get("usernames"):
    st.error("No users found. Please populate protapp_water_data.user_permissions.")
    st.stop()

config = {
    "credentials": users_from_db,
    "cookie": {"name": "WaterAppCookie", "key": "abcdef", "expiry_days": 30},
    "preauthorized": {"emails": []},
}

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
    config["preauthorized"],
)

authenticator.login()  # writes to st.session_state internally

# -----------------------------
# Main App
# -----------------------------
auth_status = st.session_state.get("authentication_status", None)

if auth_status:
    authenticator.logout("Logout", "sidebar")
    display_name = st.session_state.get("name") or st.session_state.get("username", "")
    st.sidebar.title(f"Welcome, {display_name}!")

    username_key = normalize_email(st.session_state.get("username", ""))
    current_user_data = users_from_db["usernames"].get(username_key)

    if not current_user_data:
        st.error("Logged-in user not found in credentials map. Contact the administrator.")
        st.stop()

    user_role = current_user_data.get("role", "Process Controller")
    assigned_wtws = current_user_data.get("wtws", [])

    if user_role == "Process Controller":
        st.header("Water Quality Data Entry")

        with st.form("water_quality_form", clear_on_submit=True):
            entry_timestamp = datetime.now(timezone.utc)

            wtw_name = st.selectbox("Select WTW*", assigned_wtws)

            sampling_point = st.selectbox(
                "Sampling Point*",
                ["Raw", "Settling", "Filter 1", "Filter 2", "Final"],
            )

            st.markdown("---")
            ph = st.number_input("pH Value", min_value=0.0, max_value=14.0, value=7.0, step=0.1)
            ph_image = st.camera_input("Take pH Reading Picture")

            turbidity = st.number_input("Turbidity (NTU)", min_value=0.0, step=0.01)
            turbidity_image = st.camera_input("Take Turbidity Reading Picture")

            free_chlorine = st.number_input("Free Chlorine (mg/L)", min_value=0.0, step=0.1)
            free_chlorine_image = st.camera_input("Take Free Chlorine Picture")

            passcode = st.text_input("Enter Your Passcode*", type="password")

            submitted = st.form_submit_button("Submit Record")

            if submitted:
                if not passcode or not wtw_name:
                    st.error("Passcode and WTW selection are required.")
                else:
                    entry_id = str(uuid.uuid4())
                    rows_to_insert = [
                        {
                            "entry_id": entry_id,
                            "entry_timestamp": entry_timestamp.isoformat(),
                            "wtw_name": wtw_name,
                            "sampling_point": sampling_point,
                            "user_email": st.session_state.get("username", ""),
                            "passcode_used": passcode,
                            "ph": ph,
                            "turbidity": turbidity,
                            "free_chlorine": free_chlorine,
                        }
                    ]
                    table_id = "protapp_water_data.water_quality_log"
                    try:
                        errors = client.insert_rows_json(table_id, rows_to_insert)
                        if not errors:
                            st.success("Record submitted successfully!")
                        else:
                            st.error(f"Error submitting record: {errors}")
                    except Exception as e:
                        st.error("Error while inserting into BigQuery.")
                        st.exception(e)

    elif user_role == "Manager":
        st.header("Manager Dashboard")
        st.info("Manager dashboard coming soon.")

elif auth_status is False:
    st.error("Username/password is incorrect")
else:
    st.title("Water Treatment App")
    st.warning("Please enter your username and password")







