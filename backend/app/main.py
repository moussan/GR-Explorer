from fastapi import FastAPI

# Import the API router
from .api import endpoints

app = FastAPI(
    title="GR Explorer Backend API",
    description="API for performing General Relativity calculations and managing scenarios.",
    version="0.1.0",
    # Add root path if deploying behind a proxy with a specific prefix
    # root_path="/api/v1" 
)

@app.get("/", tags=["General"])
def read_root():
    """Root endpoint, provides a simple welcome message."""
    return {"message": "Welcome to the GR Explorer Backend!"}

# Include the calculation and verification endpoints
app.include_router(endpoints.router, prefix="/api", tags=["API"])

# Placeholder for future scenario management API
# from .api import scenarios
# app.include_router(scenarios.router, prefix="/api/scenarios", tags=["Scenarios"])

# The following is useful for running directly with `python main.py` for simple debugging
# but uvicorn command in Dockerfile is the primary way to run.
if __name__ == "__main__":
    import uvicorn
    # Use reload=True for development so server restarts on code changes
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True) 