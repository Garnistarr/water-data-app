import json
import uuid
from datetime import datetime, timezone

import pandas as pd
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
        st.error("🔴 Could not connect to BigQuery. Please check your credentials in Secrets.")
        st.exception(e)
        st.stop()

client = get_db_connection()

# -----------------------------
# Function to Fetch Users from BigQuery (keys use email as-is)
# -----------------------------
@st.cache_data(ttl=600) # Cache the user list for 10 minutes
def fetch_users_from_db():
    query = "SELECT email, name, password, role, assigned_wtws FROM protapp_water_data.user_permissions"
    try:
        df = client.query(query).to_dataframe()

        users = {"usernames": {}}
        for index, row in df.iterrows():
            # Use lower-case email for the dictionary key to avoid case issues
            email_key = row["email"].lower()
            assigned_wtws = row['assigned_wtws'] if row['assigned_wtws'] is not None else []

            users["usernames"][email_key] = {
                "email": row["email"],
                "name": row["name"],
                "password": row["password"],
                "role": row["role"],
                "wtws": assigned_wtws
            }
        return users
    except Exception as e:
        st.error("🔴 Could not fetch user data from BigQuery.")
        st.exception(e)
        return {"usernames": {}}

users_from_db = fetch_users_from_db()

# -----------------------------
# Authentication (Using latest library pattern)
# -----------------------------
if not users_from_db or not users_from_db["usernames"]:
    st.error("No user data found in the database. Please add users to the user_permissions table.")
    st.stop()

config = {
    'credentials': users_from_db,
    'cookie': {
        'name': 'WaterAppCookie',
        'key': 'abcdef',
        'expiry_days': 30
    },
    'preauthorized': {
        'emails': []
    }
}

# -----------------------------
# PATCH: Try to enable case-insensitive login if supported
# If you get a TypeError, remove username_case_sensitive=False
# -----------------------------
try:
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized'],
        username_case_sensitive=False  # Try this for case-insensitive, remove if error!
    )
except TypeError:
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
    )

authenticator.login()

# -----------------------------
# Main App
# -----------------------------
if st.session_state.get("authentication_status"):
    authenticator.logout("Logout", "sidebar")
    st.sidebar.title(f"Welcome, {st.session_state['name']}!")

    # --- PATCHED SECTION ---
    # Use username from session_state as lower-case for lookup
    username = st.session_state["username"].lower()
    # Defensive: Check if username exists in the dictionary
    if username not in users_from_db["usernames"]:
        st.error("Authenticated user not found in the database. Please contact admin.")
        st.stop()
    current_user_data = users_from_db["usernames"][username]
    # --- END PATCHED SECTION ---

    user_role = current_user_data["role"]
    assigned_wtws = current_user_data["wtws"]

    if user_role == "Process Controller":
        st.header("📝 Water Quality Data Entry")

        with st.form("water_quality_form", clear_on_submit=True):
            entry_timestamp = datetime.now(timezone.utc)

            # Ensure assigned_wtws is not empty before creating the selectbox
            if not assigned_wtws:
                st.warning("You are not assigned to any Water Treatment Works. Please contact an administrator.")
                wtw_name = None
            else:
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
                            "user_email": username,  # Use lower-case email
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
                            st.success("✅ Record submitted successfully!")
                        else:
                            st.error(f"Error submitting record: {errors}")
                    except Exception as e:
                        st.error("Error while inserting into BigQuery.")
                        st.exception(e)

    elif user_role == "Manager":
        st.header("📈 Manager Dashboard")
        st.info("Manager dashboard coming soon.")

elif st.session_state.get("authentication_status") is False:
    st.error("Username/password is incorrect")
elif st.session_state.get("authentication_status") is None:
    st.title("💧 Water Treatment App")
    st.warning("Please enter your username and password")







