from fastapi import APIRouter
from backend import db

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/")
def get_users(role: str = None):
    return db.get_users(role)
