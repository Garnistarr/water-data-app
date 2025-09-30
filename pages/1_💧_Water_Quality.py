import streamlit as st
import uuid
from datetime import datetime, timezone

# --- This page is a simple worker. It gets all its info from the shared briefcase (session_state) ---

# 1. Check if the user is logged in
if 'authentication_status' not in st.session_state or not st.session_state['authentication_status']:
    st.warning("Please log in to access this page.")
    st.stop()

# 2. Get the shared data from the briefcase
user_data = st.session_state.get('user_data', {})
client = st.session_state.get('db_client')

if not user_data or not client:
    st.error("Session expired or data is missing. Please log out and log back in.")
    st.stop()

user_role = user_data.get("role")
assigned_wtws = user_data.get("wtws", [])

# 3. Build the page based on the user's role
if user_role == "Process Controller":
    st.header("📝 Water Quality Data Entry")

    with st.form("water_quality_form", clear_on_submit=True):
        entry_timestamp = datetime.now(timezone.utc)
        
        if not assigned_wtws:
            st.warning("You are not assigned to any Water Treatment Works. Please contact an administrator.")
            wtw_name = None
        else:
            wtw_name = st.selectbox("Select WTW*", assigned_wtws)

        sampling_point = st.selectbox("Sampling Point*", ["Raw", "Settling", "Filter 1", "Filter 2", "Final"])
        st.markdown("---")
        ph = st.number_input("pH Value", min_value=0.0, max_value=14.0, value=7.0, step=0.1)
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
                    "user_email": st.session_state["email"],
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
    st.info("As a Manager, you do not have access to this data entry form.")



