from fastapi import FastAPI

from app.routers import health

app = FastAPI(
    title="Retail Expiry Campaigner API",
    version="0.1.0",
)

app.include_router(health.router)


@app.get("/")
def root():
    return {"service": "retail-expiry-campaigner", "docs": "/docs"}