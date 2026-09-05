import streamlit as st

st.title("Campaigns")

st.info("Placeholder: create and review expiry-dated campaigns.")

st.text_input("Campaign name")
st.selectbox("Target segment", ["Expiring in 7 days", "Expiring in 14 days", "Expiring in 30 days"])
st.button("Launch campaign", type="primary")