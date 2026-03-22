from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.models.schema import NewsItem, Source
from app.schemas.api import SystemStatsResponse
from app.services.scheduler import run_ingestion_cycle

router = APIRouter(prefix="/api", tags=["system"])

@router.post("/refresh")
async def manual_refresh(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_ingestion_cycle)
    return {"status": "Ingestion triggered in background"}

@router.get("/stats", response_model=SystemStatsResponse)
async def get_system_stats(session: AsyncSession = Depends(get_db)):
    total_articles = (await session.execute(select(func.count(NewsItem.id)))).scalar() or 0
    total_sources = (await session.execute(select(func.count(Source.id)))).scalar() or 0
    active_sources = (await session.execute(select(func.count(Source.id)).where(Source.active == True))).scalar() or 0
    duplicates = (await session.execute(select(func.count(NewsItem.id)).where(NewsItem.is_duplicate == True))).scalar() or 0
    
    avg_impact = (await session.execute(select(func.avg(NewsItem.impact_score)).where(NewsItem.is_duplicate == False))).scalar() or 0.0
    
    dedup_rate = (duplicates / total_articles * 100) if total_articles > 0 else 0.0
    
    return SystemStatsResponse(
        total_articles=total_articles,
        total_sources=total_sources,
        active_sources=active_sources,
        dedup_rate_percentage=round(dedup_rate, 2),
        average_impact=round(float(avg_impact), 2)
    )
