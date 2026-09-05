import streamlit as st

st.title("Inventory")

st.info("Placeholder: list products with expiry dates here.")

with st.expander("Add product", expanded=False):
    name = st.text_input("Product name")
    expiry = st.date_input("Expiry date")
    st.button("Add", type="primary")