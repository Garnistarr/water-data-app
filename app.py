import json
import uuid
from datetime import datetime, timezone
import pandas as pd
import streamlit as st
import bcrypt
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
        
        users = {}
        for index, row in df.iterrows():
            email_lower = row["email"]
            
            wtws_value = row['assigned_wtws']
            if wtws_value is None:
                assigned_list = []
            else:
                assigned_list = list(wtws_value)

            users[email_lower] = {
                "name": row["name"],
                "password": row["password"],
                "role": row["role"], 
                "wtws": assigned_list
            }
        return users
    except Exception as e:
        st.error("🔴 Could not fetch user data from BigQuery.")
        st.exception(e)
        return None

# -----------------------------
# Initialize Session State
# -----------------------------
if 'authentication_status' not in st.session_state:
    st.session_state['authentication_status'] = None
if 'name' not in st.session_state:
    st.session_state['name'] = None
if 'email' not in st.session_state:
    st.session_state['email'] = None

# --- Custom Login Logic ---
if not st.session_state['authentication_status']:
    st.title("💧 Water Treatment App")
    st.info("Please enter your email and password to log in.")

    users_from_db = fetch_users_from_db()
    if not users_from_db:
        st.error("No user data found in the database. Please add a user.")
        st.stop()

    with st.form("login_form"):
        email = st.text_input("Email").lower()
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            if email in users_from_db:
                user_data = users_from_db[email]
                stored_hashed_password = user_data['password'].encode('utf-8')
                typed_password_bytes = password.encode('utf-8')
                
                if bcrypt.checkpw(typed_password_bytes, stored_hashed_password):
                    st.session_state['authentication_status'] = True
                    st.session_state['name'] = user_data['name']
                    st.session_state['email'] = email
                    st.rerun()
                else:
                    st.error("Incorrect email or password")
            else:
                st.error("Incorrect email or password")
else:
    # -----------------------------
    # Main App (for logged-in users)
    # -----------------------------
    st.sidebar.title(f"Welcome, {st.session_state['name']}!")
    if st.sidebar.button("Logout"):
        st.session_state['authentication_status'] = None
        st.session_state['name'] = None
        st.session_state['email'] = None
        st.rerun()

    st.title("ProtApp Home")
    st.header("Welcome to the Water Treatment Data App")
    st.write("Please select a page from the sidebar to begin.")
    st.info("This is the main landing page. All data entry forms and dashboards are located in the pages accessible via the sidebar menu.")




