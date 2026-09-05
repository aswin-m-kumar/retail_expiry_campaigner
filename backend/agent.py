import os
import random
from datetime import datetime, timedelta
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from . import db, config

# Initialize Groq via LangChain with fallback options
groq_key = os.getenv("GROQ_API_KEY")
llm = None
if groq_key:
    try:
        llm = ChatGroq(api_key=groq_key, model="llama-3.1-8b-instant", temperature=0.7)
    except Exception as e:
        print(f"⚠️ Warning initializing Groq LLM: {e}")

def compute_urgency_score(inventory_row: dict) -> float:
    try:
        expiry_str = inventory_row.get("expiry_date", "")
        if isinstance(expiry_str, str) and len(expiry_str) >= 10:
            expiry_date = datetime.strptime(expiry_str[:10], "%Y-%m-%d").date()
        else:
            expiry_date = datetime.now().date() + timedelta(days=15)
        
        days_to_expiry = (expiry_date - datetime.now().date()).days
        if days_to_expiry <= 0:
            return 1.0
        
        item_info = inventory_row.get("items", {}) or {}
        tier = item_info.get("perishability_tier", "med")
        weight = config.URGENCY_WEIGHTS.get(tier, 1.0)
        
        score = (config.EXPIRY_WINDOW_DAYS - days_to_expiry) / config.EXPIRY_WINDOW_DAYS
        return max(0.0, min(1.0, score * weight))
    except Exception as e:
        return 0.5

def compute_affinity_score(user_id: str, category: str) -> float:
    try:
        purchases = db.get_purchase_history(user_id)
        if not purchases:
            return 0.3
        cat_count = sum(1 for p in purchases if isinstance(p, dict) and p.get("category") == category)
        score = (cat_count * 0.3) + (len(purchases) / 10.0)
        return max(0.0, min(1.0, score))
    except Exception:
        return 0.5

def compute_would_buy_anyway_score(user_row: dict) -> float:
    score = 0.0
    tier = user_row.get("loyalty_tier", "new")
    sensitivity = user_row.get("discount_sensitivity", "neutral")
    
    if tier == "vip":
        score += 0.4
    elif tier == "regular":
        score += 0.2
        
    if sensitivity == "insensitive":
        score += 0.4
    elif sensitivity == "neutral":
        score += 0.1
        
    return max(0.0, min(1.0, score))

def decide_strategy(urgency: float, affinity: float, would_buy_anyway: float) -> tuple[str, float, float]:
    if would_buy_anyway > config.WOULD_BUY_ANYWAY_THRESHOLD:
        return "notify", 0.0, 0.0
    
    total_score = (urgency * 0.6) + (affinity * 0.4)
    
    if total_score > 0.7:
        band = config.DISCOUNT_BANDS.get("aggressive_discount", (31, 50))
        return "aggressive_discount", round(random.uniform(*band), 1), total_score
    elif total_score > 0.4:
        band = config.DISCOUNT_BANDS.get("tiered_discount", (16, 30))
        return "tiered_discount", round(random.uniform(*band), 1), total_score
    else:
        band = config.DISCOUNT_BANDS.get("small_perk", (5, 15))
        return "small_perk", round(random.uniform(*band), 1), total_score

def generate_reasoning_text(user_row: dict, item_row: dict, scores: dict, strategy: str) -> str:
    user_name = user_row.get("name", "Valued Customer")
    item_name = item_row.get("name", "Product")
    
    if llm:
        try:
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a helpful retail marketing assistant. Return only a single concise customer-facing promotional sentence."),
                ("user", "User: {user}, Item: {item}, Strategy: {strategy}. Write a 1-sentence customer offer.")
            ])
            chain = prompt | llm
            res = chain.invoke({"user": user_name, "item": item_name, "strategy": strategy})
            if res and res.content:
                return res.content.strip()
        except Exception as e:
            pass # Fallback to template below on rate limit or API error
            
    # Clean fallback template
    if strategy == "notify":
        return f"Heads up {user_name}! {item_name} is fresh and expiring soon. Grab yours before stock runs out!"
    elif strategy == "aggressive_discount":
        return f"Exclusive Mega Deal for {user_name}! Get up to 50% off on {item_name} today!"
    elif strategy == "tiered_discount":
        return f"Special offer for {user_name}: Enjoy a discount on {item_name} on your next visit!"
    else:
        return f"Special perk for {user_name}: Extra reward points when you purchase {item_name}!"

def run_campaign():
    inventory = db.get_expiring_inventory(config.EXPIRY_WINDOW_DAYS)
    users = db.get_users(role="customer")
    logs = []
    
    if not inventory or not users:
        return [{"status": "No inventory or users available to run campaign"}]
    
    # Process campaign records
    for inv in inventory:
        item = inv.get("items", {}) or {}
        if not item:
            item = {"name": f"Batch {inv.get('batch_no', 'Item')}", "category": "General"}
            
        urgency = compute_urgency_score(inv)
        
        for user in users:
            try:
                affinity = compute_affinity_score(user["user_id"], item.get("category", ""))
                would_buy = compute_would_buy_anyway_score(user)
                
                strategy, discount, total_score = decide_strategy(urgency, affinity, would_buy)
                scores = {"urgency": urgency, "affinity": affinity, "would_buy": would_buy}
                text = generate_reasoning_text(user, item, scores, strategy)
                
                if strategy == "notify":
                    db.insert_notification({
                        "user_id": user["user_id"],
                        "inventory_id": inv["inventory_id"],
                        "message": text,
                        "reasoning_text": text
                    })
                else:
                    db.insert_offer({
                        "user_id": user["user_id"],
                        "inventory_id": inv["inventory_id"],
                        "strategy_type": strategy,
                        "discount_pct": discount,
                        "reasoning_text": text,
                        "urgency_score": round(urgency, 2),
                        "affinity_score": round(affinity, 2)
                    })
                
                logs.append({
                    "user": user.get("name"),
                    "user_id": user.get("user_id"),
                    "item": item.get("name"),
                    "strategy": strategy,
                    "discount_pct": discount,
                    "score": round(total_score, 2)
                })
            except Exception as err:
                print(f"Error processing user {user.get('name')}: {err}")
                
    return logs

def answer_owner_query(query_text: str) -> str:
    if llm:
        try:
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a store inventory expert assistant. Answer concisely in 1-2 sentences."),
                ("user", "{query}")
            ])
            chain = prompt | llm
            return chain.invoke({"query": query_text}).content
        except Exception:
            pass
    return f"Inventory Assistant: Answer for query '{query_text}'. All expiring batches are tracked in the database."

def answer_customer_query(query_text: str, user_id: str) -> str:
    resolved_id = db.resolve_user_id(user_id)
    offers = db.get_offers(resolved_id)
    notifications = db.get_notifications(resolved_id)
    
    if llm:
        try:
            prompt = ChatPromptTemplate.from_messages([
                ("system", f"You are a store deal assistant. User has {len(offers)} active offers and {len(notifications)} notifications. Answer concisely."),
                ("user", "{query}")
            ])
            chain = prompt | llm
            return chain.invoke({"query": query_text}).content
        except Exception:
            pass
            
    if offers:
        best_offer = max(offers, key=lambda x: x.get("discount_pct", 0))
        return f"You currently have {len(offers)} deal(s) available! Best offer: {best_offer.get('discount_pct')}% off."
    elif notifications:
        return f"You have {len(notifications)} notification(s) regarding fresh expiring stock."
    else:
        return "You don't have active deals right now. Ask the store owner to run the latest campaign!"
