from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints import calculations
from app.db.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="GR Explorer API",
    description="API for General Relativity calculations and exploration",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers
app.include_router(calculations.router, prefix="/api/v1/calculations", tags=["calculations"])

@app.get("/", tags=["General"])
def read_root():
    """Root endpoint, provides a simple welcome message."""
    return {"message": "Welcome to the GR Explorer Backend!"}

# Placeholder for future scenario management API
# from .api import scenarios
# app.include_router(scenarios.router, prefix="/api/scenarios", tags=["Scenarios"])

# The following is useful for running directly with `python main.py` for simple debugging
# but uvicorn command in Dockerfile is the primary way to run.
if __name__ == "__main__":
    import uvicorn
    # Use reload=True for development so server restarts on code changes
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True) 