import streamlit as st

st.title("📈 Manager Dashboard")

if st.session_state.get('authentication_status'):
    user_role = st.session_state.user_data.get("role")

    if user_role == "Manager":
        st.info("This is a placeholder for the Manager Dashboard. This feature is coming soon.")
        st.write("Here, you will be able to see charts and metrics.")
    else:
        st.warning("You do not have access to the Manager Dashboard.")
else:
    st.warning("Please log in on the Home page to access this page.")

