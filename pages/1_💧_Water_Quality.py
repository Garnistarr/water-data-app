import streamlit as st
import uuid
from datetime import datetime, timezone

st.title("💧 Water Quality Data Entry")

# --- Security Check ---
# Ensure the user is logged in before showing any content
if not st.session_state.get('authentication_status'):
    st.warning("Please log in on the Home page to access this page.")
    st.stop()

# --- Get Shared Data ---
# Safely get data that was stored during login on the Home.py page
user_data = st.session_state.get('user_data', {})
client = st.session_state.get('db_client')
user_role = user_data.get("role")
assigned_wtws = user_data.get("wtws", [])
user_email = st.session_state.get("email")

# --- Helper function to save data ---
def save_data(wtw, sampling_point, ph, turbidity, free_chlorine, passcode):
    if not passcode or not wtw:
        st.error("Passcode and WTW selection are required.")
        return

    entry_id = str(uuid.uuid4())
    entry_timestamp = datetime.now(timezone.utc)
    
    rows_to_insert = [{
        "entry_id": entry_id, "entry_timestamp": entry_timestamp.isoformat(),
        "wtw_name": wtw, "sampling_point": sampling_point,
        "user_email": user_email, "passcode_used": passcode,
        "ph": ph, "turbidity": turbidity, "free_chlorine": free_chlorine,
        # TODO: Add image filenames once upload logic is built
    }]
    table_id = "protapp_water_data.water_quality_log"
    try:
        errors = client.insert_rows_json(table_id, rows_to_insert)
        if not errors:
            st.success(f"✅ {sampling_point} Water record submitted successfully!")
        else:
            st.error(f"Error submitting record: {errors}")
    except Exception as e:
        st.error("Error while inserting into BigQuery.")
        st.exception(e)

# --- Page Content ---
# Only show the form to the correct user role
if user_role == "Process Controller":

    # Create the tabs for different sampling points
    tab_raw, tab_settling, tab_final = st.tabs(["🚰 Raw Water", "💧 Settling", "✅ Final Water"])

    # --- Form for Raw Water ---
    with tab_raw:
        st.header("Raw Water Parameters")
        with st.form("raw_water_form", clear_on_submit=True):
            st.info("Fill out the form for the Raw Water sampling point.")
            wtw_name_raw = st.selectbox("Select WTW*", assigned_wtws, key="wtw_raw")
            ph_raw = st.number_input("pH Value", min_value=0.0, max_value=14.0, value=7.0, step=0.1, key="ph_raw")
            ph_image_raw = st.camera_input("Take pH Reading Picture", key="ph_cam_raw")
            turbidity_raw = st.number_input("Turbidity (NTU)", min_value=0.0, step=0.01, key="turb_raw")
            turbidity_image_raw = st.camera_input("Take Turbidity Reading Picture", key="turb_cam_raw")
            passcode_raw = st.text_input("Enter Your Passcode*", type="password", key="pass_raw")
            
            submitted_raw = st.form_submit_button("Submit Raw Water Record")
            if submitted_raw:
                save_data(wtw_name_raw, "Raw", ph_raw, turbidity_raw, None, passcode_raw)

    # --- Form for Settling Water ---
    with tab_settling:
        st.header("Settling Water Parameters")
        with st.form("settling_water_form", clear_on_submit=True):
            st.info("Fill out the form for the Settling Water sampling point.")
            wtw_name_settling = st.selectbox("Select WTW*", assigned_wtws, key="wtw_settling")
            ph_settling = st.number_input("pH Value", min_value=0.0, max_value=14.0, value=7.0, step=0.1, key="ph_settling")
            ph_image_settling = st.camera_input("Take pH Reading Picture", key="ph_cam_settling")
            turbidity_settling = st.number_input("Turbidity (NTU)", min_value=0.0, step=0.01, key="turb_settling")
            turbidity_image_settling = st.camera_input("Take Turbidity Reading Picture", key="turb_cam_settling")
            passcode_settling = st.text_input("Enter Your Passcode*", type="password", key="pass_settling")

            submitted_settling = st.form_submit_button("Submit Settling Water Record")
            if submitted_settling:
                save_data(wtw_name_settling, "Settling", ph_settling, turbidity_settling, None, passcode_settling)

    # --- Form for Final Water (with all parameters) ---
    with tab_final:
        st.header("Final Water Parameters")
        with st.form("final_water_form", clear_on_submit=True):
            st.info("Fill out the form for the Final Water sampling point.")
            wtw_name_final = st.selectbox("Select WTW*", assigned_wtws, key="wtw_final")
            ph_final = st.number_input("pH Value", min_value=0.0, max_value=14.0, value=7.0, step=0.1, key="ph_final")
            ph_image_final = st.camera_input("Take pH Reading Picture", key="ph_cam_final")
            turbidity_final = st.number_input("Turbidity (NTU)", min_value=0.0, step=0.01, key="turb_final")
            turbidity_image_final = st.camera_input("Take Turbidity Reading Picture", key="turb_cam_final")
            free_chlorine_final = st.number_input("Free Chlorine (mg/L)", min_value=0.0, step=0.1, key="chlor_final")
            free_chlorine_image_final = st.camera_input("Take Free Chlorine Picture", key="chlor_cam_final")
            passcode_final = st.text_input("Enter Your Passcode*", type="password", key="pass_final")
            
            submitted_final = st.form_submit_button("Submit Final Water Record")
            if submitted_final:
                save_data(wtw_name_final, "Final", ph_final, turbidity_final, free_chlorine_final, passcode_final)

else:
    st.info("As a Manager, you do not have access to this data entry form.")






