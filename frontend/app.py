import streamlit as st
import requests
import time
from src.config import API_BASE_URL

st.set_page_config(page_title="Retail Expiry Campaigner", layout="wide")

# Basic Auth / Role Selection
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.role = None

if not st.session_state.authenticated:
    st.title("🔐 Login")
    with st.form("login_form"):
        user_id = st.text_input("User ID")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Role", ["customer", "owner"])
        submit = st.form_submit_button("Login")

        if submit:
            # Basic simulation of auth as full auth logic is not in backend yet
            if user_id and password:
                st.session_state.authenticated = True
                st.session_state.role = role
                st.session_state.user_id = user_id
                st.rerun()
            else:
                st.error("Please enter both User ID and Password")
    st.stop()

# Authenticated Dashboard
st.title(f"🛒 Retail Expiry Campaigner - {st.session_state.role.capitalize()} View")

if st.session_state.role == "owner":
    tab1, tab2, tab3, tab4 = st.tabs(["📦 Inventory", "📢 Campaigns", "📜 Agent Log", "🤖 Owner AI"])

    with tab1:
        st.header("Expiring Inventory")
        if st.button("Refresh Inventory"):
            try:
                res = requests.get(f"{API_BASE_URL}/inventory/")
                if res.status_code == 200:
                    data = res.json()
                    flattened = []
                    for item in data:
                        row = item.copy()
                        if "items" in item and isinstance(item["items"], dict):
                            row.update(item["items"])
                            del row["items"]
                        flattened.append(row)
                    st.table(flattened)
                else:
                    st.error(f"API Error: {res.status_code}")
            except Exception as e:
                st.error(f"Connection error: {e}")

    with tab2:
        st.header("Campaign Management")
        if st.button("🚀 Run Campaign Agent"):
            try:
                res = requests.post(f"{API_BASE_URL}/campaigns/run")
                if res.status_code == 200:
                    status = res.json()
                    if status.get("status") == "started":
                        st.info("Campaign started in background. Please check the Agent Log tab.")
                    else:
                        st.warning(status.get("message", "Unknown error"))
                else:
                    st.error(f"API Error: {res.status_code}")
            except Exception as e:
                st.error(f"Connection error: {e}")

    with tab3:
        st.header("Decision Log")
        if st.button("Load Latest Result"):
            try:
                res = requests.get(f"{API_BASE_URL}/campaigns/status")
                if res.status_code == 200:
                    status = res.json()
                    if status["running"]:
                        st.warning("Campaign is still running... please wait.")
                    elif status["last_result"]:
                        if isinstance(status["last_result"], dict) and "error" in status["last_result"]:
                            st.error(f"Last campaign failed: {status['last_result']['error']}")
                        else:
                            st.table(status["last_result"])
                    else:
                        st.info("No campaign results available.")
                else:
                    st.error(f"API Error: {res.status_code}")
            except Exception as e:
                st.error(f"Connection error: {e}")

    with tab4:
        st.header("Store Owner AI Assistant")
        query = st.text_input("Ask about your inventory:")
        if st.button("Ask", key="owner_ask"):
            try:
                res = requests.post(f"{API_BASE_URL}/chat/owner", params={"query": query})
                if res.status_code == 200:
                    st.write(res.json().get("answer", "No answer provided"))
                else:
                    st.error(f"API Error: {res.status_code}")
            except Exception as e:
                st.error(f"Connection error: {e}")

else: # Customer View
    tab1, tab2 = st.tabs(["👤 My Deals", "🤖 Deal Finder"])

    with tab1:
        st.header("My Notifications & Offers")
        if st.button("Refresh Deals"):
            try:
                # Fetch notifications
                n_res = requests.get(f"{API_BASE_URL}/notifications/", params={"user_id": st.session_state.user_id})
                o_res = requests.get(f"{API_BASE_URL}/offers/", params={"user_id": st.session_state.user_id})
                
                if n_res.status_code == 200 and o_res.status_code == 200:
                    st.subheader("Notifications")
                    st.table(n_res.json())
                    st.subheader("Personalized Offers")
                    st.table(o_res.json())
                else:
                    st.error("Could not fetch deals.")
            except Exception as e:
                st.error(f"Connection error: {e}")

    with tab2:
        st.header("Customer AI Agent")
        query = st.text_input("Ask about deals or availability:")
        if st.button("Ask", key="customer_ask"):
            try:
                res = requests.post(f"{API_BASE_URL}/chat/customer", params={"query": query, "user_id": st.session_state.user_id})
                if res.status_code == 200:
                    st.write(res.json().get("answer", "No answer provided"))
                else:
                    st.error(f"API Error: {res.status_code}")
            except Exception as e:
                st.error(f"Connection error: {e}")

if st.sidebar.button("Logout"):
    st.session_state.authenticated = False
    st.session_state.role = None
    st.rerun()
