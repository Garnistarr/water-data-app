import streamlit as st

st.title("Test: Water Quality Page")

st.success("If you can see this message, the page file is being recognized by Streamlit.")

st.write("This is a temporary test to diagnose the sidebar issue.")

# We can check the session state here to see what this page sees
st.write("Current authentication status on this page:")
st.write(st.session_state.get('authentication_status'))



