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

def get_expiring_inventory(window_days: int = 30):
    client = get_client()
    try:
        response = client.table("inventory").select("*, items(*)").execute()
        return response.data
    except Exception as e:
        inv_data = client.table("inventory").select("*").execute().data
        items_data = client.table("items").select("*").execute().data
        item_map = {item["item_id"]: item for item in items_data}
        for inv in inv_data:
            inv["items"] = item_map.get(inv.get("item_id"), {})
        return inv_data

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

def resolve_user_id(identifier: str) -> str:
    if not identifier:
        return identifier
    try:
        import uuid
        uuid.UUID(identifier)
        return identifier
    except ValueError:
        try:
            client = get_client()
            res = client.table("user").select("user_id").ilike("name", identifier).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]["user_id"]
        except Exception:
            pass
        return identifier

def get_notifications(user_id: str = None):
    client = get_client()
    query = client.table("notifications").select("*")
    if user_id:
        resolved_id = resolve_user_id(user_id)
        query = query.eq("user_id", resolved_id)
    response = query.execute()
    return response.data

def get_offers(user_id: str = None):
    client = get_client()
    query = client.table("offers").select("*")
    if user_id:
        resolved_id = resolve_user_id(user_id)
        query = query.eq("user_id", resolved_id)
    response = query.execute()
    return response.data

def update_inventory_stock(inventory_id: str, new_qty: int):
    client = get_client()
    response = client.table("inventory").update({"stock_qty": new_qty}).eq("inventory_id", inventory_id).execute()
    return response.data

def claim_offer(offer_id: str):
    client = get_client()
    try:
        offer = client.table("offers").select("*").eq("offer_id", offer_id).execute().data
        if not offer:
            return {"status": "error", "message": "Offer not found"}
        offer_data = offer[0]
        inv_id = offer_data.get("inventory_id")
        
        client.table("offers").delete().eq("offer_id", offer_id).execute()
        
        if inv_id:
            inv = client.table("inventory").select("*").eq("inventory_id", inv_id).execute().data
            if inv and len(inv) > 0:
                current_qty = inv[0].get("stock_qty", 1)
                new_qty = max(0, current_qty - 1)
                client.table("inventory").update({"stock_qty": new_qty}).eq("inventory_id", inv_id).execute()
                
        return {"status": "success", "message": "Offer claimed successfully!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
