import streamlit as st

st.set_page_config(
    page_title="Manager Dashboard",
    page_icon="📈",
    layout="centered",
)

st.title("📈 Manager Dashboard")

if 'authentication_status' not in st.session_state or not st.session_state['authentication_status']:
    st.warning("Please log in to access this page.")
    st.stop()

st.info("This is a placeholder for the Manager Dashboard. This feature is coming soon.")

st.write("Here, you will be able to see charts and metrics based on the data collected by Process Controllers.")
