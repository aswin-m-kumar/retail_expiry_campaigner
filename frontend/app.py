import streamlit as st

st.set_page_config(
    page_title="Retail Expiry Campaigner",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Retail Expiry Campaigner")

st.markdown(
    """
    Track products approaching expiry and trigger targeted retail campaigns.
    Use the sidebar to navigate.
    """
)

st.divider()

col1, col2, col3 = st.columns(3)
col1.metric("Products", "—")
col2.metric("Expiring Soon (7 days)", "—")
col3.metric("Active Campaigns", "—")