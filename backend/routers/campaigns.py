from fastapi import APIRouter, BackgroundTasks
from backend import agent

router = APIRouter(prefix="/campaigns", tags=["Campaigns"])

# Simple in-memory state for campaign status
campaign_status = {"running": False, "last_result": None}

def campaign_task():
    global campaign_status
    try:
        result = agent.run_campaign()
        campaign_status["last_result"] = result
    except Exception as e:
        campaign_status["last_result"] = {"error": str(e)}
    finally:
        campaign_status["running"] = False

@router.post("/run")
def run_campaign(background_tasks: BackgroundTasks):
    if campaign_status["running"]:
        return {"status": "error", "message": "Campaign already running"}
    
    campaign_status["running"] = True
    background_tasks.add_task(campaign_task)
    return {"status": "started", "message": "Campaign started in background"}

@router.get("/status")
def get_status():
    return {
        "running": campaign_status["running"],
        "last_result": campaign_status["last_result"]
    }

