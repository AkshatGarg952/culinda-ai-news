from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.bootstrap import initialize_database
from app.routers import news, favorites, broadcast, sources, system, ai
from app.services.scheduler import start_scheduler

app = FastAPI(title="AI News Aggregation Dashboard API", version="1.0.0")

app.include_router(news.router)
app.include_router(favorites.router)
app.include_router(broadcast.router)
app.include_router(sources.router)
app.include_router(system.router)
app.include_router(ai.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await initialize_database()
    start_scheduler()

@app.get("/health")
async def health_check():
    return {"status": "ok"}
