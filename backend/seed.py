import random
import uuid
from datetime import datetime, timedelta
from backend import db

def reset_db():
    """Clears all data from the tables in correct order of dependency."""
    client = db.get_client()
    print("🧹 Resetting database...")
    # Delete in reverse order of FK dependencies
    tables = ["offers", "notifications", "purchases", "inventory", "items", "user"]
    for table in tables:
        client.table(table).delete().neq("user_id", "00000000-0000-0000-0000-000000000000").execute()
        print(f"  - Cleared {table}")

def seed():
    client = db.get_client()
    print("🌱 Seeding data...")
    
    # Seed items
    items = [
        {"name": "Organic Milk", "category": "Dairy", "unit_cost": 1.0, "mrp": 2.0, "perishability_tier": "high"},
        {"name": "Whole Grain Bread", "category": "Bakery", "unit_cost": 0.5, "mrp": 1.5, "perishability_tier": "high"},
        {"name": "Greek Yogurt", "category": "Dairy", "unit_cost": 0.8, "mrp": 2.5, "perishability_tier": "med"},
        {"name": "Pasta", "category": "Dry Goods", "unit_cost": 0.3, "mrp": 1.2, "perishability_tier": "low"},
    ]
    
    item_ids = []
    for item in items:
        res = client.table("items").insert(item).execute()
        item_ids.append(res.data[0]["item_id"])
        
    # Seed users
    users = [
        {"name": "Alice", "role": "customer", "join_date": "2023-01-01", "visit_frequency_per_month": 4, "loyalty_tier": "vip", "avg_basket_value": 50.0, "discount_sensitivity": "insensitive"},
        {"name": "Bob", "role": "customer", "join_date": "2023-06-01", "visit_frequency_per_month": 2, "loyalty_tier": "regular", "avg_basket_value": 30.0, "discount_sensitivity": "responsive"},
        {"name": "Charlie", "role": "customer", "join_date": "2024-01-01", "visit_frequency_per_month": 1, "loyalty_tier": "new", "avg_basket_value": 20.0, "discount_sensitivity": "neutral"},
        {"name": "Store Owner", "role": "owner", "join_date": "2022-01-01", "visit_frequency_per_month": 30, "loyalty_tier": "vip", "avg_basket_value": 0.0, "discount_sensitivity": "insensitive"},
    ]
    
    user_ids = []
    for user in users:
        res = client.table("user").insert(user).execute()
        user_ids.append(res.data[0]["user_id"])
        
    # Seed inventory
    for item_id in item_ids:
        expiry = (datetime.now() + timedelta(days=random.randint(1, 40))).strftime("%Y-%m-%d")
        client.table("inventory").insert({
            "item_id": item_id,
            "batch_no": f"BATCH-{random.randint(100, 999)}",
            "stock_qty": random.randint(10, 100),
            "expiry_date": expiry
        }).execute()
        
    # Seed some purchases
    for _ in range(20):
        client.table("purchases").insert({
            "user_id": random.choice(user_ids[:3]),
            "item_id": random.choice(item_ids),
            "purchased_at": datetime.now().isoformat(),
            "price_paid": random.uniform(1.0, 5.0),
            "discount_applied": random.uniform(0, 20)
        }).execute()
    print("✅ Seeding complete!")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "reset":
        reset_db()
        seed()
    else:
        seed()
