from fastapi import FastAPI
from app.routes import planner

app = FastAPI(title="Travel Planner API", version="1.0.0")

# Include router
app.include_router(planner.router, prefix="/api", tags=["planner"])
