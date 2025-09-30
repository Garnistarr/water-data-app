import json
import streamlit as st
import bcrypt
from google.cloud import bigquery
from google.oauth2 import service_account

# -----------------------------
# Page Configuration (Main App)
# -----------------------------
st.set_page_config(
    page_title="ProtApp Home",
    page_icon="💧",
    layout="centered",
)

# -----------------------------
# Functions (Centralized in main app)
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
        st.error("🔴 Could not connect to BigQuery.")
        st.exception(e)
        st.stop()

@st.cache_data(ttl=600)
def fetch_all_users(_client):
    query = "SELECT email, name, password, role, assigned_wtws FROM protapp_water_data.user_permissions"
    try:
        df = _client.query(query).to_dataframe()
        if df.empty: return None
        df['email'] = df['email'].str.lower()
        users = {}
        for index, row in df.iterrows():
            email_lower = row["email"]
            wtws_value = row['assigned_wtws']
            assigned_list = list(wtws_value) if wtws_value is not None else []
            users[email_lower] = {
                "name": row["name"], "password": row["password"],
                "role": row["role"], "wtws": assigned_list
            }
        return users
    except Exception as e:
        st.error("🔴 Could not fetch user data.")
        st.exception(e)
        return None

# -----------------------------
# Initialize Session State
# -----------------------------
if 'authentication_status' not in st.session_state:
    st.session_state.authentication_status = None
if 'user_data' not in st.session_state:
    st.session_state.user_data = None
if 'db_client' not in st.session_state:
    st.session_state.db_client = get_db_connection()

# -----------------------------
# Login / Main App Logic
# -----------------------------
if not st.session_state.authentication_status:
    st.title("💧 Water Treatment App Login")
    st.info("Please enter your email (in lowercase) and password.")

    all_users = fetch_all_users(st.session_state.db_client)
    if not all_users:
        st.error("No user data found in the database. Please add a user.")
        st.stop()

    with st.form("login_form"):
        email = st.text_input("Email").lower()
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            user_data = all_users.get(email)
            if user_data and bcrypt.checkpw(password.encode('utf-8'), user_data['password'].encode('utf-8')):
                st.session_state.authentication_status = True
                st.session_state.user_data = user_data
                st.session_state.email = email # Keep email for logging
                st.rerun()
            else:
                st.error("Incorrect email or password")
else:
    # --- This is the Home Page for logged-in users ---
    st.sidebar.title(f"Welcome, {st.session_state.user_data['name']}!")
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

    st.title("ProtApp Home")
    st.header("Welcome to the Water Treatment Data App")
    st.info("Please select a page from the sidebar menu to begin.")





