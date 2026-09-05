from fastapi import APIRouter
from backend import db

router = APIRouter(prefix="/offers", tags=["Offers"])

@router.get("/")
def get_offers(user_id: str = None):
    return db.get_offers(user_id)
