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
# Function to Fetch Users (Hardened for Case-Insensitivity)
# -----------------------------
@st.cache_data(ttl=600)
def fetch_users_from_db():
    query = "SELECT email, name, password, role, assigned_wtws FROM protapp_water_data.user_permissions"
    try:
        df = client.query(query).to_dataframe()
        if df.empty:
            return None
            
        df['email'] = df['email'].str.lower()
        
        users = {"usernames": {}}
        for index, row in df.iterrows():
            email_lower = row["email"]
            assigned_wtws = row['assigned_wtws'] if row['assigned_wtws'] is not None else []
            
            users["usernames"][email_lower] = {
                "email": email_lower,
                "name": row["name"],
                "password": row["password"],
                "role": row["role"], 
                "wtws": assigned_wtws
            }
        return users
    except Exception as e:
        st.error("🔴 Could not fetch user data from BigQuery.")
        st.exception(e)
        return None

users_from_db = fetch_users_from_db()

# -----------------------------
# Authentication
# -----------------------------
if not users_from_db:
    st.error("No user data found in the database. Please add a user to the user_permissions table.")
    st.stop()

config = {
    'credentials': users_from_db,
    'cookie': {'name': 'WaterAppCookie', 'key': 'abcdef', 'expiry_days': 30},
    'preauthorized': {'emails': []}
}

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

# --- This is the key change to prevent user confusion ---
st.title("💧 Water Treatment App")
st.info("Please use your email address in all lowercase letters to log in.")
# ---

authenticator.login(fields={'Username': 'Email'})

# -----------------------------
# Main App
# -----------------------------
if st.session_state["authentication_status"]:
    authenticator.logout("Logout", "sidebar")
    st.sidebar.title(f"Welcome, {st.session_state['name']}!")

    username_lower = st.session_state["username"].lower()
    current_user_data = users_from_db["usernames"].get(username_lower)
    
    if not current_user_data:
        st.error("Could not find user data after login. Please clear cache and try again.")
        if st.button("Clear Cache and Rerun"):
            st.cache_data.clear()
            st.rerun()
        st.stop()

    user_role = current_user_data.get("role")
    assigned_wtws = current_user_data.get("wtws", [])

    if user_role == "Process Controller":
        st.header("📝 Water Quality Data Entry")

        with st.form("water_quality_form", clear_on_submit=True):
            entry_timestamp = datetime.now(timezone.utc)
            
            if not assigned_wtws:
                st.warning("You are not assigned to any WTWs. Please contact an administrator.")
                wtw_name = None
            else:
                wtw_name = st.selectbox("Select WTW*", assigned_wtws)

            sampling_point = st.selectbox("Sampling Point*", ["Raw", "Settling", "Filter 1", "Filter 2", "Final"])
            st.markdown("---")
            ph = st.number_input("pH Value", min_value=0.0, max_value=14.0, value=7.0, step=0.1)
            # Image inputs omitted for brevity in this section
            turbidity = st.number_input("Turbidity (NTU)", min_value=0.0, step=0.01)
            free_chlorine = st.number_input("Free Chlorine (mg/L)", min_value=0.0, step=0.1)
            passcode = st.text_input("Enter Your Passcode*", type="password")
            submitted = st.form_submit_button("Submit Record")

            if submitted:
                if not passcode or not wtw_name:
                    st.error("Passcode and WTW selection are required.")
                else:
                    entry_id = str(uuid.uuid4())
                    rows_to_insert = [{
                        "entry_id": entry_id, "entry_timestamp": entry_timestamp.isoformat(),
                        "wtw_name": wtw_name, "sampling_point": sampling_point,
                        "user_email": st.session_state["username"],
                        "passcode_used": passcode, "ph": ph, "turbidity": turbidity,
                        "free_chlorine": free_chlorine,
                    }]
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
    # No title or warning here, handled by the new info box above the login
    pass




