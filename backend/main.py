from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import health, inventory, campaigns, chat, notifications, offers, users
from backend import db

app = FastAPI(
    title="Retail Expiry Campaigner API",
    version="0.1.0",
)

@app.on_event("startup")
async def startup_event():
    try:
        db.get_client()
    except Exception as e:
        print(f"Critical Startup Error: {e}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(inventory.router)
app.include_router(campaigns.router)
app.include_router(chat.router)
app.include_router(notifications.router)
app.include_router(offers.router)
app.include_router(users.router)

@app.get("/")
def root():
    return {"service": "retail-expiry-campaigner", "docs": "/docs"}
