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
st.title("💧 Water Treatment App")

# -----------------------------
# BigQuery Connection
# -----------------------------
try:
    creds_json_str = st.secrets["GCP_CREDENTIALS"]  # JSON string in Secrets (triple-quoted)
    creds_dict = json.loads(creds_json_str)
    credentials = service_account.Credentials.from_service_account_info(creds_dict)
    client = bigquery.Client(credentials=credentials, project=credentials.project_id)
    st.session_state.db_connection = True
except Exception as e:
    st.error("🔴 Could not connect to BigQuery. Please check your credentials in Secrets.")
    st.exception(e)
    st.stop()

# -----------------------------
# Authentication (demo users)
# NOTE: We avoid stauth.Hasher() to prevent cloud runtime errors.
# These are bcrypt hashes for:
#   jsmith / abc
#   rjones / def
# -----------------------------
users = {
    "usernames": {
        "jsmith": {
            "email": "jsmith@example.com",
            "name": "John Smith",
            "password": "$2b$12$o9MoKdEy3VuB5an623IFG.OR2txgFTFV9XrGBEYTIK.7U/GmVU3mK",
        },
        "rjones": {
            "email": "rjones@example.com",
            "name": "Rebecca Jones",
            "password": "$2b$12$Q6QFIW9fRf74GMdjcHmsbuTvdb11tVCIpVaTavrmAxVwB7L6iklyS",
        },
    }
}

authenticator = stauth.Authenticate(
    users,
    cookie_name="WaterAppCookie",   # any name
    key="abcdef",                   # any random string for signing cookies
    cookie_expiry_days=30,
)

name, authentication_status, username = authenticator.login("Login", "main")

# -----------------------------
# Main App
# -----------------------------
if authentication_status:
    authenticator.logout("Logout", "sidebar")
    st.sidebar.title(f"Welcome, {name}!")

    # Save the email for later DB inserts
    st.session_state["email"] = users["usernames"][username]["email"]

    # TODO: Later, fetch role & assigned WTWs from BigQuery user_permissions.
    user_role = "Process Controller"

    if user_role == "Process Controller":
        st.header("📝 Water Quality Data Entry")

        with st.form("water_quality_form", clear_on_submit=True):
            # Timestamp in UTC for BigQuery
            entry_timestamp = datetime.now(timezone.utc)

            # TODO: Populate WTW list from user_permissions in BigQuery
            wtw_name = st.selectbox("Select WTW*", ["Ashton WTW", "Clearwater WTW"])

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
                if not passcode:
                    st.error("Passcode is required to submit.")
                else:
                    entry_id = str(uuid.uuid4())

                    # NOTE: Image upload to Cloud Storage not implemented yet.
                    # When you add it, store the returned filenames in the *_image_filename fields.
                    rows_to_insert = [
                        {
                            "entry_id": entry_id,
                            "entry_timestamp": entry_timestamp.isoformat(),
                            "wtw_name": wtw_name,
                            "sampling_point": sampling_point,
                            "user_email": st.session_state["email"],
                            "passcode_used": passcode,
                            "ph": ph,
                            "turbidity": turbidity,
                            "free_chlorine": free_chlorine,
                            # "ph_image_filename": "...",
                            # "turbidity_image_filename": "...",
                            # "free_chlorine_image_filename": "...",
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

elif authentication_status is False:
    st.error("Username/password is incorrect")
elif authentication_status is None:
    st.warning("Please enter your username and password")


