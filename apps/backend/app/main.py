from fastapi import FastAPI

print("🚀 EDITH BACKEND STARTED")

app = FastAPI(
    title="EDITH Backend",
    description="Backend API for the EDITH Multi-Agent AI Platform",
    version="0.1.0"
)


@app.get("/")
async def root():
    return {
        "message": "Welcome to EDITH 🚀"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "edith-backend",
        "version": "0.1.0"
    }