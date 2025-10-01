import json
import streamlit as st
import bcrypt
from google.cloud import bigquery
from google.oauth2 import service_account
import uuid
from datetime import datetime, timezone

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="ProtApp",
    page_icon="💧",
    layout="centered",
)

# -----------------------------
# Functions
# -----------------------------
@st.cache_resource
def get_db_connection():
    try:
        creds_json_str = st.secrets["GCP_CREDENTIALS"]
        creds_dict = json.loads(creds_json_str)
        credentials = service_account.Credentials.from_service_account_info(creds_dict)
        client = bigquery.Client(credentials=credentials, project=credentials.project_id)
        return client
    except Exception:
        st.error("🔴 Could not connect to BigQuery.")
        st.stop()

@st.cache_data(ttl=600)
def fetch_all_users(_client):
    query = "SELECT email, name, password, role, assigned_wtws FROM protapp_water_data.user_permissions"
    try:
        df = _client.query(query).to_dataframe()
        if df.empty: return None
        df['email'] = df['email'].str.lower()
        users = {}
        for _, row in df.iterrows():
            email_lower = row["email"]
            wtws_value = row['assigned_wtws']
            assigned_list = list(wtws_value) if wtws_value is not None else []
            users[email_lower] = {
                "name": row["name"], "password": row["password"],
                "role": row["role"], "wtws": assigned_list
            }
        return users
    except Exception:
        st.error("🔴 Could not fetch user data.")
        return None

# --- Function to display the Water Quality page content ---
def water_quality_page():
    st.title("💧 Water Quality Data Entry")
    user_data = st.session_state.user_data
    client = get_db_connection() # Get a fresh client connection
    assigned_wtws = user_data.get("wtws", [])

    if user_data.get("role") == "Process Controller":
        with st.form("water_quality_form", clear_on_submit=True):
            st.header("Water Quality Form")
            wtw_name = st.selectbox("Select WTW*", assigned_wtws)
            sampling_point = st.selectbox("Sampling Point*", ["Raw", "Settling", "Filter 1", "Filter 2", "Final"])
            st.markdown("---")
            ph = st.number_input("pH Value", min_value=0.0, max_value=14.0, value=7.0, step=0.1)
            turbidity = st.number_input("Turbidity (NTU)", min_value=0.0, step=0.01)
            free_chlorine = st.number_input("Free Chlorine (mg/L)", min_value=0.0, step=0.1)
            passcode = st.text_input("Enter Your Passcode*", type="password")
            submitted = st.form_submit_button("Submit Record")
            
            if submitted:
                # Logic to save data to BigQuery
                entry_id = str(uuid.uuid4())
                entry_timestamp = datetime.now(timezone.utc)
                rows_to_insert = [{
                    "entry_id": entry_id, "entry_timestamp": entry_timestamp.isoformat(),
                    "wtw_name": wtw_name, "sampling_point": sampling_point,
                    "user_email": st.session_state.user_data['email'],
                    "passcode_used": passcode, "ph": ph, "turbidity": turbidity,
                    "free_chlorine": free_chlorine,
                }]
                table_id = "protapp_water_data.water_quality_log"
                errors = client.insert_rows_json(table_id, rows_to_insert)
                if not errors:
                    st.success("Data submitted successfully!")
                else:
                    st.error(f"Error submitting record: {errors}")

    else:
        st.info("As a Manager, you do not have access to this data entry form.")
    
    if st.button("⬅️ Back to Main Menu"):
        st.session_state.page = 'Home'
        st.rerun()

# --- Function to display the Manager Dashboard ---
def manager_dashboard_page():
    st.title("📈 Manager Dashboard")
    st.info("Manager dashboard coming soon.")
    if st.button("⬅️ Back to Main Menu"):
        st.session_state.page = 'Home'
        st.rerun()

# -----------------------------
# Initialize Session State
# -----------------------------
if 'authentication_status' not in st.session_state:
    st.session_state.authentication_status = None
if 'page' not in st.session_state:
    st.session_state.page = 'Home'
if 'user_data' not in st.session_state:
    st.session_state.user_data = None


# -----------------------------
# Login / Main App Logic
# -----------------------------
if not st.session_state.authentication_status:
    # --- LOGIN SCREEN ---
    st.title("💧 Water Treatment App Login")
    st.info("Please enter your email (in lowercase) and password.")

    client = get_db_connection()
    all_users = fetch_all_users(client)
    
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
                st.rerun()
            else:
                st.error("Incorrect email or password")

else:
    # --- MAIN MENU OR PAGE VIEWS (for logged-in users) ---
    st.sidebar.title(f"Welcome, {st.session_state.user_data['name']}!")
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

    # --- View Router ---
    if st.session_state.page == 'Home':
        st.title("ProtApp Menu")
        st.header("Please select an option")
        
        # --- Main Menu Buttons ---
        if st.button("💧 Water Quality", use_container_width=True):
            st.session_state.page = 'Water Quality'
            st.rerun()
        
        if st.button("📈 Manager Dashboard", use_container_width=True):
            st.session_state.page = 'Manager Dashboard'
            st.rerun()
        
        # Add more buttons here for other pages like Volumes, Chemicals, etc.

    elif st.session_state.page == 'Water Quality':


