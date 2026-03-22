import math
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, nullslast
from sqlalchemy.orm import selectinload
from typing import Optional
import uuid

from app.core.database import get_db
from app.core.config import settings
from app.models.schema import NewsItem, Source
from app.schemas.api import PaginatedNewsResponse, NewsItemResponse, AIResponse
import google.generativeai as genai

if settings.gemini_api_key:
    genai.configure(api_key=settings.gemini_api_key)

router = APIRouter(prefix="/api/news", tags=["news"])

def to_response(item: NewsItem) -> NewsItemResponse:
    return NewsItemResponse(
        id=item.id,
        source_id=item.source_id,
        source_name=item.source.name if item.source else None,
        title=item.title,
        summary=item.summary,
        author=item.author,
        url=item.url,
        published_at=item.published_at,
        tags=item.tags or [],
        impact_score=item.impact_score or 0.0,
        cluster_id=item.cluster_id,
        is_duplicate=item.is_duplicate,
        created_at=item.created_at,
    )

@router.get("", response_model=PaginatedNewsResponse)
async def get_news(
    source: Optional[uuid.UUID] = None,
    keyword: Optional[str] = None,
    entity: Optional[str] = None,
    sort_by: str = Query("date", description="date|impact|source"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db)
):
    query = select(NewsItem).options(selectinload(NewsItem.source)).where(NewsItem.is_duplicate == False)
    
    if source:
        query = query.where(NewsItem.source_id == source)
    
    if keyword:
        search_pattern = f"%{keyword}%"
        query = query.where(NewsItem.title.ilike(search_pattern) | NewsItem.summary.ilike(search_pattern))
        
    if entity:
        query = query.where(NewsItem.tags.contains([entity]) | NewsItem.title.ilike(f"%{entity}%"))

    if sort_by == "impact":
        query = query.order_by(nullslast(desc(NewsItem.impact_score)))
    elif sort_by == "source":
        query = query.order_by(NewsItem.source_id, desc(NewsItem.published_at))
    else:
        query = query.order_by(desc(NewsItem.published_at))
        
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await session.execute(count_query)
    total = count_result.scalar() or 0
    
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await session.execute(query)
    items = result.scalars().all()
    
    return PaginatedNewsResponse(
        items=[to_response(item) for item in items],
        total=total,
        page=page,
        page_size=page_size
    )

@router.get("/{news_id}", response_model=NewsItemResponse)
async def get_single_news(news_id: uuid.UUID, session: AsyncSession = Depends(get_db)):
    result = await session.execute(
        select(NewsItem).options(selectinload(NewsItem.source)).where(NewsItem.id == news_id)
    )
    item = result.scalars().first()
    
    if not item:
        raise HTTPException(status_code=404, detail="News item not found")
        
    return to_response(item)

@router.post("/{news_id}/summarize", response_model=AIResponse)
async def summarize_news(news_id: uuid.UUID, session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(NewsItem).where(NewsItem.id == news_id))
    item = result.scalars().first()
    
    if not item:
        raise HTTPException(status_code=404, detail="News item not found")

    if not settings.gemini_api_key:
        fallback = f"TL;DR: {item.title}. {(item.summary or '')[:200]}"
        return AIResponse(generated_content=fallback)
        
    prompt = f"Provide a 2-sentence TL;DR for this article titled '{item.title}': {item.summary}"
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"temperature": 0.3})
        response = await model.generate_content_async(prompt)
        return AIResponse(generated_content=response.text)
    except Exception:
        fallback = f"TL;DR: {item.title}. {(item.summary or '')[:200]}"
        return AIResponse(generated_content=fallback)

