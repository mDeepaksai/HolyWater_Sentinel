from fastapi import FastAPI

app = FastAPI(
    title="HolyWater Sentinel API",
    description="Smart Village Water-Health Early Warning System",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "project": "HolyWater Sentinel",
        "status": "running",
        "message": "Water-Health Early Warning API"
    }