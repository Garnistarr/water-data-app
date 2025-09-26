import streamlit as st
import streamlit_authenticator as stauth
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
from datetime import datetime, timezone
import uuid
import json

# --- Page Configuration ---
st.set_page_config(page_title="Water Treatment App", page_icon="💧", layout="centered")

# --- BigQuery Connection ---
try:
    creds_json_str = st.secrets["GCP_CREDENTIALS"]
    creds_dict = json.loads(creds_json_str)
    creds = service_account.Credentials.from_service_account_info(creds_dict)
    client = bigquery.Client(credentials=creds, project=creds.project_id)
    st.session_state.db_connection = True
except Exception as e:
    st.error("🔴 Could not connect to BigQuery. Please check your credentials.")
    st.stop()

# =========================
#  FIX: hash passwords once
# =========================
hashed_passwords = stauth.Hasher(['abc', 'def']).generate()  # returns list[str]

# --- User Authentication ---
users = {
    "usernames": {
        "jsmith": {
            "email": "jsmith@example.com",
            "name": "John Smith",
            "password": hashed_passwords[0],  # <-- use precomputed hash
        },
        "rjones": {
            "email": "rjones@example.com",
            "name": "Rebecca Jones",
            "password": hashed_passwords[1],  # <-- use precomputed hash
        },
    }
}

authenticator = stauth.Authenticate(
    users,
    "WaterAppCookie",  # cookie name
    "abcdef",          # signature key
    cookie_expiry_days=30,
)

name, authentication_status, username = authenticator.login("Login", "main")

# --- Main Application ---
if authentication_status:
    authenticator.logout("Logout", "sidebar")
    st.sidebar.title(f"Welcome, {name}!")

    # Save email for later inserts
    st.session_state["email"] = users["usernames"][username]["email"]

    # TODO: Replace with role from BigQuery later
    user_role = "Process Controller"

    if user_role == "Process Controller":
        st.header("💧 Water Quality Data Entry")
        with st.form("water_quality_form", clear_on_submit=True):
            entry_timestamp = datetime.now(timezone.utc)  # UTC is best for BigQuery
            wtw_name = st.selectbox("Select WTW*", ["Ashton WTW", "Clearwater WTW"])
            sampling_point = st.selectbox("Sampling Point*", ["Raw", "Settling", "Filter 1", "Filter 2", "Final"])

            st.markdown("---")

            ph = st.number_input("pH Value", 0.0, 14.0, 7.0, step=0.1)
            ph_image = st.camera_input("Take pH Reading Picture")

            turbidity = st.number_input("Turbidity (NTU)", 0.0, step=0.01)
            turbidity_image = st.camera_input("Take Turbidity Reading Picture")

            free_chlorine = st.number_input("Free Chlorine (mg/L)", 0.0, step=0.1)
            free_chlorine_image = st.camera_input("Take Free Chlorine Picture")

            passcode = st.text_input("Enter Your Passcode*", type="password")
            submitted = st.form_submit_button("Submit Record")

            if submitted:
                if not passcode:
                    st.error("Passcode is required to submit.")
                else:
                    entry_id = str(uuid.uuid4())
                    rows_to_insert = [{
                        "entry_id": entry_id,
                        "entry_timestamp": entry_timestamp.isoformat(),
                        "wtw_name": wtw_name,
                        "sampling_point": sampling_point,
                        "user_email": st.session_state["email"],
                        "passcode_used": passcode,
                        "ph": ph,
                        "turbidity": turbidity,
                        "free_chlorine": free_chlorine,
                    }]
                    table_id = "protapp_water_data.water_quality_log"
                    errors = client.insert_rows_json(table_id, rows_to_insert)
                    if not errors:
                        st.success("✅ Record submitted successfully!")
                    else:
                        st.error(f"Error submitting record: {errors}")

    elif user_role == "Manager":
        st.header("📈 Manager Dashboard")
        st.write("Dashboard view to be built here.")

elif authentication_status is False:
    st.error("Username/password is incorrect")
elif authentication_status is None:   # FIX: typo 'authentication_satus'
    st.warning("Please enter your username and password")
