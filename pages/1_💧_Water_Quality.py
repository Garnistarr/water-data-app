import streamlit as st
import uuid
from datetime import datetime, timezone

st.title("💧 Water Quality Data Entry")

# Check if the user is logged in
if st.session_state.get('authentication_status'):
    user_data = st.session_state.user_data
    client = st.session_state.db_client
    user_role = user_data.get("role")
    assigned_wtws = user_data.get("wtws", [])

    if user_role == "Process Controller":
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
                        "user_email": st.session_state.email,
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
    else:
        st.info("As a Manager, you do not have access to this data entry form.")
else:
    st.warning("Please log in on the Home page to access this page.")


