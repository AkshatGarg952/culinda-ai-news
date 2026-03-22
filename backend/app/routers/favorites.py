import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from app.core.database import get_db
from app.models.schema import Favorite, NewsItem
from app.schemas.api import FavoriteCreateRequest, FavoriteResponse, PaginatedFavoritesResponse

router = APIRouter(prefix="/api/favorites", tags=["favorites"])

# Dummy user ID for MVP
USER_ID = uuid.UUID('00000000-0000-0000-0000-000000000001')

@router.get("", response_model=PaginatedFavoritesResponse)
async def get_favorites(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=500),
    session: AsyncSession = Depends(get_db)
):
    query = select(Favorite).where(Favorite.user_id == USER_ID).order_by(desc(Favorite.created_at))
    
    count_query = select(func.count()).select_from(query.subquery())
    total = (await session.execute(count_query)).scalar() or 0
    
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await session.execute(query)
    favorites = result.scalars().all()
    
    # Eager load could be used, but this is simple enough for MVP
    items = []
    for fp in favorites:
        news_result = await session.execute(select(NewsItem).where(NewsItem.id == fp.news_item_id))
        fp.news_item = news_result.scalars().first()
        items.append(fp)
        
    return PaginatedFavoritesResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )

@router.post("", response_model=FavoriteResponse)
async def create_favorite(req: FavoriteCreateRequest, session: AsyncSession = Depends(get_db)):
    result = await session.execute(
        select(Favorite).where(Favorite.news_item_id == req.news_item_id, Favorite.user_id == USER_ID)
    )
    existing = result.scalars().first()
    if existing:
        raise HTTPException(status_code=400, detail="Already favorited")
        
    news_result = await session.execute(select(NewsItem).where(NewsItem.id == req.news_item_id))
    if not news_result.scalars().first():
        raise HTTPException(status_code=404, detail="News item not found")
        
    favorite = Favorite(user_id=USER_ID, news_item_id=req.news_item_id)
    session.add(favorite)
    await session.commit()
    await session.refresh(favorite)

    # Explicitly load the news_item relationship for response serialization
    news_item_result = await session.execute(select(NewsItem).where(NewsItem.id == req.news_item_id))
    favorite.news_item = news_item_result.scalars().first()

    return favorite

@router.delete("/{favorite_id}")
async def remove_favorite(favorite_id: uuid.UUID, session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(Favorite).where(Favorite.id == favorite_id))
    favorite = result.scalars().first()
    
    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")
        
    await session.delete(favorite)
    await session.commit()
    return {"status": "deleted"}
