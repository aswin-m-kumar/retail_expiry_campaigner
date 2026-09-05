import streamlit as st
import requests
import time
from src.config import API_BASE_URL

st.set_page_config(page_title="Retail Expiry Campaigner", layout="wide", initial_sidebar_state="expanded")

# Initialize session state for auth and chat histories
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.role = None
    st.session_state.user_id = None
    st.session_state.user_name = None

if "customer_messages" not in st.session_state:
    st.session_state.customer_messages = [
        {"role": "assistant", "content": "👋 Hi there! I'm your Deal Finder AI. Ask me about active offers, expiring items, or specific categories!"}
    ]

if "owner_messages" not in st.session_state:
    st.session_state.owner_messages = [
        {"role": "assistant", "content": "🏪 Hello Store Owner! Ask me about expiring inventory risk, low stock levels, or running marketing campaigns."}
    ]

# Custom CSS for high contrast & rich interactive aesthetics
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #1e2436 0%, #151824 100%);
        color: #ffffff !important;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #363d59;
        margin-bottom: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .metric-card h4 {
        color: #ffffff !important;
        font-weight: 600;
        margin-top: 0;
        margin-bottom: 10px;
        font-size: 1.15rem;
    }
    .metric-card p {
        color: #e0e6ed !important;
        margin: 0;
        font-size: 0.95rem;
    }
    .badge-discount {
        background: linear-gradient(135deg, #e63946 0%, #d62828 100%);
        color: #ffffff !important;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        display: inline-block;
    }
    .badge-strategy {
        background-color: #2b324b;
        color: #38bdf8 !important;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        border: 1px solid #38bdf840;
    }
    .stButton>button {
        border-radius: 8px;
        transition: all 0.2s ease-in-out;
    }
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
    st.title("🛍️ Retail Expiry Campaigner — Interactive Login")
    st.caption("Select or enter an identity to interact with live campaigns & AI deal finders")
    
    users_list = fetch_users()
    user_options = {f"{u['name']} ({u['role'].capitalize()} - {u.get('loyalty_tier', 'tier').upper()})": u for u in users_list}
    
    col1, col2 = st.columns([1, 1])
    with col1:
        with st.form("login_form"):
            selected_option = st.selectbox("Select Account:", list(user_options.keys()))
            custom_input = st.text_input("Or Enter Custom User ID / Name (Optional):", value="")
            submit = st.form_submit_button("🔑 Sign In & Start")

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
        - **Customers**: Interact with AI Assistant, claim deals in 1-click, and track expiry alerts.
        - **Store Owners**: Monitor live stock risks and trigger background AI campaign scoring.
        """)
    st.stop()

# ── Sidebar ──
st.sidebar.markdown(f"### 👤 {st.session_state.user_name}")
role_icon = "🏪" if st.session_state.role == "owner" else "🛍️"
st.sidebar.markdown(f"**Role:** {role_icon} {st.session_state.role.capitalize()}")
st.sidebar.markdown(f"**User ID:** `{st.session_state.user_id}`")
st.sidebar.divider()

if st.sidebar.button("🚪 Logout"):
    st.session_state.authenticated = False
    st.session_state.role = None
    st.session_state.user_id = None
    st.session_state.user_name = None
    st.rerun()

# ── STORE OWNER VIEW ──
if st.session_state.role == "owner":
    st.title("🏪 Store Owner Interactive Command Center")
    tab1, tab2, tab3, tab4 = st.tabs(["📦 Inventory Risk Monitor", "📢 AI Campaign Manager", "📜 Decision Logs", "🤖 Store Owner AI Assistant"])

    with tab1:
        st.header("Expiring Stock Inventory")
        if st.button("🔄 Refresh Live Inventory"):
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
                
                filter_choice = st.radio("Filter Inventory Risk:", ["All Batches", "🔴 Low Stock (< 20 units)"], horizontal=True)
                if filter_choice == "🔴 Low Stock (< 20 units)":
                    flattened = [r for r in flattened if r.get("stock_qty", 0) < 20]
                    
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
                        st.success("🎉 Campaign execution complete! Check decision logs tab.")
                        st.balloons()
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
                    logs = status["last_result"]
                    if isinstance(logs, list):
                        formatted_logs = []
                        for entry in logs:
                            if isinstance(entry, dict):
                                row = entry.copy()
                                if "discount_pct" in row and isinstance(row["discount_pct"], (int, float)):
                                    row["discount_pct"] = f"{float(row['discount_pct']):.2f}%"
                                formatted_logs.append(row)
                            else:
                                formatted_logs.append(entry)
                        st.dataframe(formatted_logs, use_container_width=True)
                    else:
                        st.write(logs)
                else:
                    st.info("No campaign logs recorded yet. Click 'Run Campaign Agent' in the Campaign Manager tab.")
            else:
                st.error(f"API Error: {res.status_code}")
        except Exception as e:
            st.error(f"Connection error: {e}")

    with tab4:
        st.header("🤖 Interactive Store Owner Assistant")
        
        # Display chat message history
        for msg in st.session_state.owner_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
        # Interactive Chat Input
        if prompt := st.chat_input("Ask about stock levels, low inventory, or campaigns..."):
            st.session_state.owner_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
                
            with st.chat_message("assistant"):
                with st.spinner("Analyzing inventory data..."):
                    try:
                        res = requests.post(f"{API_BASE_URL}/chat/owner", params={"query": prompt})
                        ans = res.json().get("answer", "No response provided.") if res.status_code == 200 else f"API Error: {res.status_code}"
                    except Exception as err:
                        ans = f"Connection error: {err}"
                    st.markdown(ans)
                    st.session_state.owner_messages.append({"role": "assistant", "content": ans})

# ── CUSTOMER VIEW ──
else:
    st.title(f"🛍️ Welcome back, {st.session_state.user_name}!")
    tab1, tab2 = st.tabs(["🎁 My Interactive Deals & Offers", "🤖 AI Deal Finder Chat"])

    with tab1:
        st.header("Your Personalized Deals & Expiry Alerts")
        
        # Load offers and notifications
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
            max_disc = max([float(o.get("discount_pct", 0)) for o in offers], default=0.0)
            st.metric("💰 Top Discount", f"{max_disc:.2f}%" if max_disc > 0 else "N/A")

        st.divider()

        if not offers and not notifications:
            st.warning("ℹ️ **No active deals found for your account.**")
            st.info("Click below to trigger the AI campaign engine and generate personalized deals right now!")
            if st.button("⚡ Run Campaign Engine to Generate My Deals Now"):
                with st.spinner("Generating deals..."):
                    try:
                        requests.post(f"{API_BASE_URL}/campaigns/run")
                        st.success("Deals generated successfully! Reloading...")
                        st.balloons()
                        time.sleep(1)
                        st.rerun()
                    except Exception as err:
                        st.error(f"Error running campaign: {err}")
        else:
            if offers:
                st.subheader("🔥 Exclusive Offers (Click to Claim!)")
                for offer in offers:
                    offer_id = offer.get("offer_id")
                    strategy = offer.get("strategy_type", "offer").replace("_", " ").title()
                    disc_val = float(offer.get("discount_pct", 0))
                    disc_str = f"{disc_val:.2f}%"
                    msg = offer.get("reasoning_text", "Special deal!")
                    
                    c1, c2 = st.columns([4, 1])
                    with c1:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4>🏷️ {msg}</h4>
                            <p><b>Discount:</b> <span class="badge-discount">{disc_str} OFF</span> &nbsp;|&nbsp; <b>Strategy:</b> <span class="badge-strategy">{strategy}</span></p>
                        </div>
                        """, unsafe_allow_html=True)
                    with c2:
                        st.write("")
                        if st.button("🎟️ Claim Deal", key=f"claim_{offer_id}"):
                            try:
                                claim_res = requests.post(f"{API_BASE_URL}/offers/claim", params={"offer_id": offer_id})
                                if claim_res.status_code == 200:
                                    st.toast(f"🎉 Claimed {disc_str} OFF offer!", icon="🎁")
                                    st.balloons()
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error("Could not claim offer.")
                            except Exception as err:
                                st.error(f"Error claiming: {err}")

            if notifications:
                st.subheader("🔔 Expiry & Stock Notifications")
                for notif in notifications:
                    msg = notif.get("message", notif.get("reasoning_text", "Expiring item alert"))
                    st.info(f"📢 {msg}")

    with tab2:
        st.header("🤖 Interactive AI Deal Assistant")
        st.caption("Ask questions about your offers, category deals, or expiring items below!")
        
        # Suggested prompt chips
        st.markdown("**Try asking:**")
        chip_col1, chip_col2, chip_col3 = st.columns(3)
        with chip_col1:
            if st.button("💡 What deals do I have today?"):
                st.session_state.customer_messages.append({"role": "user", "content": "What deals do I have today?"})
                st.rerun()
        with chip_col2:
            if st.button("💡 Show dairy or bakery offers"):
                st.session_state.customer_messages.append({"role": "user", "content": "Show dairy or bakery offers"})
                st.rerun()
        with chip_col3:
            if st.button("💡 Which item has top discount?"):
                st.session_state.customer_messages.append({"role": "user", "content": "Which item has the top discount?"})
                st.rerun()

        st.divider()

        # Render conversation history bubbles
        for msg in st.session_state.customer_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Auto-trigger if last message was user chip click without response
        if st.session_state.customer_messages and st.session_state.customer_messages[-1]["role"] == "user":
            prompt = st.session_state.customer_messages[-1]["content"]
            with st.chat_message("assistant"):
                with st.spinner("Searching active deals..."):
                    try:
                        res = requests.post(f"{API_BASE_URL}/chat/customer", params={"query": prompt, "user_id": st.session_state.user_id})
                        ans = res.json().get("answer", "No answer provided.") if res.status_code == 200 else f"API Error: {res.status_code}"
                    except Exception as err:
                        ans = f"Connection error: {err}"
                    st.markdown(ans)
                    st.session_state.customer_messages.append({"role": "assistant", "content": ans})

        # Interactive Chat Input
        if prompt := st.chat_input("Ask Deal Assistant..."):
            st.session_state.customer_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
                
            with st.chat_message("assistant"):
                with st.spinner("Searching active deals..."):
                    try:
                        res = requests.post(f"{API_BASE_URL}/chat/customer", params={"query": prompt, "user_id": st.session_state.user_id})
                        ans = res.json().get("answer", "No answer provided.") if res.status_code == 200 else f"API Error: {res.status_code}"
                    except Exception as err:
                        ans = f"Connection error: {err}"
                    st.markdown(ans)
                    st.session_state.customer_messages.append({"role": "assistant", "content": ans})
