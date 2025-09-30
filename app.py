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
    st.session_state.update({
        'authentication_status': None, 'name': None, 'email': None,
        'user_data': None, 'db_client': None
    })

# -----------------------------
# Login / Main App Logic
# -----------------------------
if not st.session_state['authentication_status']:
    st.title("💧 Water Treatment App")
    st.info("Please enter your email and password to log in.")

    all_users = fetch_all_users(get_db_connection())
    if not all_users:
        st.error("No user data found in the database. Please add a user.")
        st.stop()

    with st.form("login_form"):
        email = st.text_input("Email").lower()
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            user_data = all_users.get(email)
            if user_data:
                stored_hashed_password = user_data['password'].encode('utf-8')
                typed_password_bytes = password.encode('utf-8')
                
                if bcrypt.checkpw(typed_password_bytes, stored_hashed_password):
                    st.session_state.update({
                        'authentication_status': True,
                        'name': user_data['name'],
                        'email': email,
                        'user_data': user_data,
                        'db_client': get_db_connection()
                    })
                    st.rerun()
                else:
                    st.error("Incorrect email or password")
            else:
                st.error("Incorrect email or password")
else:
    # --- This is the Home Page for logged-in users ---
    st.sidebar.title(f"Welcome, {st.session_state['name']}!")
    if st.sidebar.button("Logout"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()

    st.title("ProtApp Home")
    st.header("Welcome to the Water Treatment Data App")
    st.info("Please select a page from the sidebar to begin.")






