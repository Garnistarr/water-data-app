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
# We remove the main title here because the login form provides its own.

# -----------------------------
# BigQuery Connection
# -----------------------------
try:
    creds_json_str = st.secrets["GCP_CREDENTIALS"]
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

# --- THIS IS THE CORRECTED SECTION ---
# The new version of the library expects a single configuration dictionary.
config = {
    'credentials': users,
    'cookie': {
        'name': 'WaterAppCookie',
        'key': 'abcdef',
        'expiry_days': 30
    }
}

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# Render the login widget
authenticator.login()
# --- END OF CORRECTION ---

# -----------------------------
# Main App
# -----------------------------
if st.session_state["authentication_status"]:
    authenticator.logout("Logout", "sidebar")
    st.sidebar.title(f"Welcome, {st.session_state['name']}!")

    # Save the email for later DB inserts
    st.session_state["email"] = users["usernames"][st.session_state["username"]]["email"]

    # TODO: Later, fetch role & assigned WTWs from BigQuery user_permissions.
    user_role = "Process Controller"

    if user_role == "Process Controller":
        st.header("📝 Water Quality Data Entry")

        with st.form("water_quality_form", clear_on_submit=True):
            entry_timestamp = datetime.now(timezone.utc)
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

elif st.session_state["authentication_status"] is False:
    st.error("Username/password is incorrect")
elif st.session_state["authentication_status"] is None:
    st.title("💧 Water Treatment App")
    st.warning("Please enter your username and password")


