import streamlit as st

# 1. Check if the user is logged in from the shared briefcase (session_state)
if 'authentication_status' not in st.session_state or not st.session_state['authentication_status']:
    st.warning("Please log in to access this page.")
    st.stop()

# 2. Get the shared user data
user_data = st.session_state.get('user_data', {})
user_role = user_data.get("role")

# 3. Build the page content
st.title("📈 Manager Dashboard")

if user_role == "Manager":
    st.info("This is a placeholder for the Manager Dashboard. This feature is coming soon.")
    st.write("Here, you will be able to see charts and metrics based on the data collected by Process Controllers.")
elif user_role == "Process Controller":
    st.warning("As a Process Controller, you do not have access to the Manager Dashboard.")
else:
    st.error("Your role is not defined. Please contact an administrator.")
