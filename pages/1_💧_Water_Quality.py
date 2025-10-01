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
            turbidity_raw = st.number_input("Turbidity (NTU)", min_value=0.0, step=0.01, key="turb_raw")
            passcode_raw = st.text_input("Enter Your Passcode*", type="password", key="pass_raw")
            
            submitted_raw = st.form_submit_button("Submit Raw Water Record")
            if submitted_raw:
                # This is where you would save the 'raw' data to BigQuery
                st.success("Raw Water data submitted successfully!")

    # --- Form for Settling Water ---
    with tab_settling:
        st.header("Settling Water Parameters")
        with st.form("settling_water_form", clear_on_submit=True):
            st.info("Fill out the form for the Settling Water sampling point.")
            wtw_name_settling = st.selectbox("Select WTW*", assigned_wtws, key="wtw_settling")
            ph_settling = st.number_input("pH Value", min_value=0.0, max_value=14.0, value=7.0, step=0.1, key="ph_settling")
            turbidity_settling = st.number_input("Turbidity (NTU)", min_value=0.0, step=0.01, key="turb_settling")
            passcode_settling = st.text_input("Enter Your Passcode*", type="password", key="pass_settling")

            submitted_settling = st.form_submit_button("Submit Settling Water Record")
            if submitted_settling:
                st.success("Settling Water data submitted successfully!")

    # --- Form for Final Water (with all parameters) ---
    with tab_final:
        st.header("Final Water Parameters")
        with st.form("final_water_form", clear_on_submit=True):
            st.info("Fill out the form for the Final Water sampling point.")
            wtw_name_final = st.selectbox("Select WTW*", assigned_wtws, key="wtw_final")
            ph_final = st.number_input("pH Value", min_value=0.0, max_value=14.0, value=7.0, step=0.1, key="ph_final")
            turbidity_final = st.number_input("Turbidity (NTU)", min_value=0.0, step=0.01, key="turb_final")
            free_chlorine_final = st.number_input("Free Chlorine (mg/L)", min_value=0.0, step=0.1, key="chlor_final")
            passcode_final = st.text_input("Enter Your Passcode*", type="password", key="pass_final")
            
            submitted_final = st.form_submit_button("Submit Final Water Record")
            if submitted_final:
                # This is where you would call your function to save 'final' data
                st.success("Final Water data submitted successfully!")

else:
    st.info("As a Manager, you do not have access to this data entry form.")



