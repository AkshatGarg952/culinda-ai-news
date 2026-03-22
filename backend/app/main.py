from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import news, favorites, broadcast, sources, system, ai

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
    import uuid
    from sqlalchemy import select
    from app.core.database import AsyncSessionLocal
    from app.models.schema import User, UserRole

    # Ensure the MVP dummy user exists so favorites FK constraint is satisfied
    MVP_USER_ID = uuid.UUID('00000000-0000-0000-0000-000000000001')
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == MVP_USER_ID))
        if not result.scalars().first():
            session.add(User(id=MVP_USER_ID, name="MVP User", email="mvp@culinda.ai", role=UserRole.admin))
            await session.commit()

    from app.services.scheduler import start_scheduler
    start_scheduler()

@app.get("/health")
async def health_check():
    return {"status": "ok"}
