import streamlit as st
import requests
import time
from src.config import API_BASE_URL

st.set_page_config(page_title="Retail Expiry Campaigner", layout="wide", initial_sidebar_state="expanded")

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.role = None
    st.session_state.user_id = None
    st.session_state.user_name = None

# Custom styling for rich aesthetics
st.markdown("""
<style>
    .metric-card {
        background-color: #1e2130;
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #323854;
        margin-bottom: 12px;
    }
    .badge-aggressive { background-color: #e63946; color: white; padding: 4px 8px; border-radius: 6px; font-weight: bold; }
    .badge-tiered { background-color: #f77f00; color: white; padding: 4px 8px; border-radius: 6px; font-weight: bold; }
    .badge-perk { background-color: #457b9d; color: white; padding: 4px 8px; border-radius: 6px; font-weight: bold; }
    .badge-notify { background-color: #2a9d8f; color: white; padding: 4px 8px; border-radius: 6px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

def fetch_users():
    try:
        res = requests.get(f"{API_BASE_URL}/users/", timeout=3)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return [
        {"user_id": "Alice", "name": "Alice", "role": "customer", "loyalty_tier": "vip"},
        {"user_id": "Bob", "name": "Bob", "role": "customer", "loyalty_tier": "regular"},
        {"user_id": "Charlie", "name": "Charlie", "role": "customer", "loyalty_tier": "new"},
        {"user_id": "Store Owner", "name": "Store Owner", "role": "owner", "loyalty_tier": "vip"}
    ]

# ── Login View ──
if not st.session_state.authenticated:
    st.title("🛍️ Retail Expiry Campaigner — Login")
    st.caption("Select or enter a user identity to enter the store dashboard")
    
    users_list = fetch_users()
    user_options = {f"{u['name']} ({u['role'].capitalize()} - {u.get('loyalty_tier', 'tier').upper()})": u for u in users_list}
    
    col1, col2 = st.columns([1, 1])
    with col1:
        with st.form("login_form"):
            selected_option = st.selectbox("Select Existing Account:", list(user_options.keys()))
            custom_input = st.text_input("Or Enter Custom User ID / Name (Optional):", value="")
            submit = st.form_submit_button("🔑 Sign In")

            if submit:
                if custom_input.strip():
                    st.session_state.user_id = custom_input.strip()
                    st.session_state.user_name = custom_input.strip()
                    st.session_state.role = "customer"
                else:
                    selected_user = user_options[selected_option]
                    st.session_state.user_id = selected_user["user_id"]
                    st.session_state.user_name = selected_user["name"]
                    st.session_state.role = selected_user["role"]
                
                st.session_state.authenticated = True
                st.rerun()
                
    with col2:
        st.info("""
        ### 💡 Welcome to Retail Expiry Campaigner
        - **Customers**: View personalized discount offers & notifications for expiring inventory.
        - **Store Owners**: Run the AI Campaign Engine and monitor inventory risk.
        """)
    st.stop()

# ── Authenticated App Header & Sidebar ──
st.sidebar.markdown(f"### 👤 {st.session_state.user_name}")
role_icon = "🏪" if st.session_state.role == "owner" else "🛍️"
st.sidebar.markdown(f"**Role:** {role_icon} {st.session_state.role.capitalize()}")
st.sidebar.markdown(f"**ID:** `{st.session_state.user_id}`")
st.sidebar.divider()

if st.sidebar.button("🚪 Logout"):
    st.session_state.authenticated = False
    st.session_state.role = None
    st.session_state.user_id = None
    st.session_state.user_name = None
    st.rerun()

# ── OWNER DASHBOARD ──
if st.session_state.role == "owner":
    st.title("🏪 Store Owner Operations Dashboard")
    tab1, tab2, tab3, tab4 = st.tabs(["📦 Inventory Risk Monitor", "📢 AI Campaign Manager", "📜 Decision Logs", "🤖 Store Owner AI"])

    with tab1:
        st.header("Expiring Stock Inventory")
        if st.button("🔄 Refresh Inventory"):
            st.rerun()
            
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
                st.dataframe(flattened, use_container_width=True)
            else:
                st.error(f"API Error: {res.status_code}")
        except Exception as e:
            st.error(f"Connection error: {e}")

    with tab2:
        st.header("Trigger AI Campaign Engine")
        st.write("Scans all expiring items and evaluates customer urgency, affinity, and price sensitivity to generate personalized offers.")
        
        if st.button("🚀 Run Campaign Agent Now", type="primary"):
            with st.spinner("Executing campaign scoring pipeline..."):
                try:
                    res = requests.post(f"{API_BASE_URL}/campaigns/run")
                    if res.status_code == 200:
                        status = res.json()
                        st.success("🎉 Campaign execution complete! Check decision logs tab.")
                    else:
                        st.error(f"API Error: {res.status_code}")
                except Exception as e:
                    st.error(f"Connection error: {e}")

    with tab3:
        st.header("Recent Campaign Decision Logs")
        try:
            res = requests.get(f"{API_BASE_URL}/campaigns/status")
            if res.status_code == 200:
                status = res.json()
                if status.get("last_result"):
                    st.write(status["last_result"])
                else:
                    st.info("No campaign logs recorded yet. Click 'Run Campaign Agent' in the Campaign Manager tab.")
            else:
                st.error(f"API Error: {res.status_code}")
        except Exception as e:
            st.error(f"Connection error: {e}")

    with tab4:
        st.header("Store Assistant AI")
        query = st.text_input("Ask about stock levels, expiry dates, or product performance:")
        if st.button("Ask Assistant"):
            try:
                res = requests.post(f"{API_BASE_URL}/chat/owner", params={"query": query})
                if res.status_code == 200:
                    st.success(res.json().get("answer"))
            except Exception as e:
                st.error(f"Error: {e}")

# ── CUSTOMER DASHBOARD ──
else:
    st.title(f"🛍️ Welcome back, {st.session_state.user_name}!")
    tab1, tab2 = st.tabs(["🎁 My Deals & Offers", "🤖 Customer Deal Assistant"])

    with tab1:
        st.header("Your Personalized Deals & Expiry Alerts")
        
        # Load offers and notifications directly
        offers, notifications = [], []
        try:
            o_res = requests.get(f"{API_BASE_URL}/offers/", params={"user_id": st.session_state.user_id})
            n_res = requests.get(f"{API_BASE_URL}/notifications/", params={"user_id": st.session_state.user_id})
            
            if o_res.status_code == 200:
                offers = o_res.json()
            if n_res.status_code == 200:
                notifications = n_res.json()
        except Exception as e:
            st.error(f"Could not connect to server: {e}")

        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("🏷️ Active Offers", len(offers))
        with m2:
            st.metric("🔔 Stock Alerts", len(notifications))
        with m3:
            max_disc = max([o.get("discount_pct", 0) for o in offers], default=0)
            st.metric("💰 Top Discount", f"{max_disc}%" if max_disc else "N/A")

        st.divider()

        if not offers and not notifications:
            st.warning("ℹ️ **No active deals found for your account.**")
            st.info("""
            This happens if the campaign agent has not been run yet, or if your user account is in a high-loyalty tier configured for notifications.
            """)
            if st.button("⚡ Run Campaign Engine to Generate My Deals Now"):
                with st.spinner("Generating deals..."):
                    try:
                        requests.post(f"{API_BASE_URL}/campaigns/run")
                        st.success("Deals generated successfully! Reloading...")
                        time.sleep(1)
                        st.rerun()
                    except Exception as err:
                        st.error(f"Error running campaign: {err}")
        else:
            if offers:
                st.subheader("🔥 Exclusive Offers For You")
                for offer in offers:
                    strategy = offer.get("strategy_type", "offer").replace("_", " ").title()
                    disc = offer.get("discount_pct", 0)
                    msg = offer.get("reasoning_text", "Special deal!")
                    
                    with st.container():
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4>🏷️ {msg}</h4>
                            <p><b>Discount:</b> <span class="badge-aggressive">{disc}% OFF</span> | <b>Strategy:</b> {strategy}</p>
                        </div>
                        """, unsafe_allow_html=True)

            if notifications:
                st.subheader("🔔 Expiry & Stock Notifications")
                for notif in notifications:
                    msg = notif.get("message", notif.get("reasoning_text", "Expiring item alert"))
                    st.info(f"📢 {msg}")

    with tab2:
        st.header("Deal Finder Assistant")
        query = st.text_input("Ask what deals or fresh items are available today:")
        if st.button("Search Deals"):
            try:
                res = requests.post(f"{API_BASE_URL}/chat/customer", params={"query": query, "user_id": st.session_state.user_id})
                if res.status_code == 200:
                    st.success(res.json().get("answer"))
            except Exception as e:
                st.error(f"Error: {e}")
