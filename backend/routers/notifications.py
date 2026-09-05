from fastapi import APIRouter
from backend import db

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("/")
def get_notifications(user_id: str = None):
    return db.get_notifications(user_id)
