from fastapi import APIRouter, HTTPException
from backend import db, agent, config

router = APIRouter(prefix="/inventory", tags=["Inventory"])

@router.get("/")
def get_inventory():
    return db.get_expiring_inventory(config.EXPIRY_WINDOW_DAYS)

@router.patch("/{inventory_id}")
def update_stock(inventory_id: str, qty: int):
    try:
        return db.update_inventory_stock(inventory_id, qty)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
