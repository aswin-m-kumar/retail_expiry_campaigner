import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

_client: Client = None

def get_client() -> Client:
    global _client
    if _client is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
        try:
            _client = create_client(SUPABASE_URL, SUPABASE_KEY)
            print("✅ Successfully connected to Supabase database")
        except Exception as e:
            print(f"❌ Failed to connect to Supabase: {e}")
            raise e
    return _client

def get_expiring_inventory(window_days: int):
    client = get_client()
    # Note: days_to_expiry computed in SQL or filtered via date comparison
    # This is a simplified version; actual implementation would use a date filter
    # For now, we fetch all and let the agent filter or use a RPC if available
    response = client.table("inventory").select("*, items(*)").execute()
    return response.data

def get_users(role: str = None):
    client = get_client()
    query = client.table("user").select("*")
    if role:
        query = query.eq("role", role)
    response = query.execute()
    return response.data

def get_purchase_history(user_id: str):
    client = get_client()
    response = client.table("purchases").select("*").eq("user_id", user_id).execute()
    return response.data

def insert_notification(row: dict):
    client = get_client()
    client.table("notifications").insert(row).execute()

def insert_offer(row: dict):
    client = get_client()
    client.table("offers").insert(row).execute()

def get_notifications(user_id: str = None):
    client = get_client()
    query = client.table("notifications").select("*")
    if user_id:
        query = query.eq("user_id", user_id)
    response = query.execute()
    return response.data

def get_offers(user_id: str = None):
    client = get_client()
    query = client.table("offers").select("*")
    if user_id:
        query = query.eq("user_id", user_id)
    response = query.execute()
    return response.data

def update_inventory_stock(inventory_id: str, new_qty: int):
    client = get_client()
    response = client.table("inventory").update({"stock_qty": new_qty}).eq("inventory_id", inventory_id).execute()
    return response.data
