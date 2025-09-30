import streamlit as st

# Set the title of the page
st.title("📈 Manager Dashboard")

# Check if the user is logged in, which is set in app.py
if st.session_state.get('authentication_status'):
    
    # Get the user's role from the shared session state
    user_role = st.session_state.get('user_data', {}).get("role")

    # Display content based on the user's role
    if user_role == "Manager":
        st.info("This is a placeholder for the Manager Dashboard. This feature is coming soon.")
        st.write("Here, you will be able to see charts and metrics based on the data collected by Process Controllers.")
    
    elif user_role == "Process Controller":
        st.warning("As a Process Controller, you do not have access to the Manager Dashboard.")
    
    else:
        st.error("Your role is not defined. Please contact an administrator.")

else:
    # If the user is not logged in, show a warning message
    st.warning("Please log in on the Home page to access this page.")


