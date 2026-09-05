from fastapi import APIRouter
from backend import agent

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/owner")
def owner_chat(query: str):
    return {"answer": agent.answer_owner_query(query)}

@router.post("/customer")
def customer_chat(query: str, user_id: str):
    return {"answer": agent.answer_customer_query(query, user_id)}
