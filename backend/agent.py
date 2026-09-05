import os
import random
from datetime import datetime, timedelta
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from . import db, config

# Initialize Groq via LangChain
# Ensure GROQ_API_KEY is set in your environment
llm = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model="openai/gpt-oss-120b")

def compute_urgency_score(inventory_row: dict) -> float:
    expiry_date = datetime.strptime(inventory_row["expiry_date"], "%Y-%m-%d").date()
    days_to_expiry = (expiry_date - datetime.now().date()).days
    
    tier = inventory_row["items"]["perishability_tier"]
    weight = config.URGENCY_WEIGHTS.get(tier, 1.0)
    
    score = (config.EXPIRY_WINDOW_DAYS - days_to_expiry) / config.EXPIRY_WINDOW_DAYS
    score = max(0.0, min(1.0, score * weight))
    return score

def compute_affinity_score(user_id: str, category: str) -> float:
    purchases = db.get_purchase_history(user_id)
    score = len(purchases) / 10.0 
    return max(0.0, min(1.0, score))

def compute_would_buy_anyway_score(user_row: dict) -> float:
    score = 0.0
    if user_row["loyalty_tier"] == "vip": score += 0.4
    elif user_row["loyalty_tier"] == "regular": score += 0.2
    if user_row["discount_sensitivity"] == "insensitive": score += 0.4
    return max(0.0, min(1.0, score))

def decide_strategy(urgency: float, affinity: float, would_buy_anyway: float) -> tuple[str, float, float]:
    if would_buy_anyway > config.WOULD_BUY_ANYWAY_THRESHOLD:
        return "notify", 0.0, 0.0
    
    total_score = (urgency * 0.6) + (affinity * 0.4)
    
    if total_score > 0.8:
        band = config.DISCOUNT_BANDS["aggressive_discount"]
        return "aggressive_discount", random.uniform(*band), total_score
    elif total_score > 0.5:
        band = config.DISCOUNT_BANDS["tiered_discount"]
        return "tiered_discount", random.uniform(*band), total_score
    else:
        band = config.DISCOUNT_BANDS["small_perk"]
        return "small_perk", random.uniform(*band), total_score

def generate_reasoning_text(user_row: dict, item_row: dict, scores: dict, strategy: str) -> str:
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful retail marketing assistant. Your response must be a single, concise sentence."),
        ("user", "User: {user}, Item: {item}, Strategy: {strategy}, Scores: {scores}. Write a one-line customer-facing offer/notification.")
    ])
    chain = prompt | llm
    response = chain.invoke({
        "user": user_row['name'], 
        "item": item_row['name'], 
        "strategy": strategy, 
        "scores": scores
    })
    return response.content

def run_campaign():
    # ... (keep existing implementation)
    inventory = db.get_expiring_inventory(config.EXPIRY_WINDOW_DAYS)
    users = db.get_users(role="customer")
    logs = []
    
    for inv in inventory:
        item = inv["items"]
        urgency = compute_urgency_score(inv)
        
        for user in users:
            affinity = compute_affinity_score(user["user_id"], item["category"])
            would_buy = compute_would_buy_anyway_score(user)
            
            strategy, discount, total_score = decide_strategy(urgency, affinity, would_buy)
            scores = {"urgency": urgency, "affinity": affinity, "would_buy": would_buy}
            text = generate_reasoning_text(user, item, scores, strategy)
            
            if strategy == "notify":
                db.insert_notification({"user_id": user["user_id"], "inventory_id": inv["inventory_id"], "message": text, "reasoning_text": text})
            else:
                db.insert_offer({"user_id": user["user_id"], "inventory_id": inv["inventory_id"], "strategy_type": strategy, "discount_pct": discount, "reasoning_text": text, "urgency_score": urgency, "affinity_score": affinity})
            
            logs.append({"user": user["name"], "item": item["name"], "strategy": strategy, "score": total_score})
            
    return logs

def answer_owner_query(query_text: str) -> str:
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a store inventory expert. Answer in one concise line."),
        ("user", "{query}")
    ])
    chain = prompt | llm
    return chain.invoke({"query": query_text}).content

def answer_customer_query(query_text: str, user_id: str) -> str:
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a friendly store assistant. Answer in one concise line."),
        ("user", "{query}")
    ])
    chain = prompt | llm
    return chain.invoke({"query": query_text}).content
