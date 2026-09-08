from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.v1 import router as v1_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: emit a plain-ASCII banner (avoids cp1252 encoding crashes that
    # a module-level print with non-ASCII characters could cause on Windows).
    print("EDITH backend started")
    yield
    # Shutdown: nothing to tear down for the in-memory slice.


app = FastAPI(
    title="EDITH Backend",
    description="Backend API for the EDITH Multi-Agent AI Platform",
    version="0.1.0",
    lifespan=lifespan,
)

# Local-development CORS for the Next.js frontend (ports 3000/3001).
# Tightened for production later; this is intentionally dev-only.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1_router)


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
