from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid

class SourceResponse(BaseModel):
    id: uuid.UUID
    name: str
    url: str
    type: str
    active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class SourceUpdateRequest(BaseModel):
    active: bool

class NewsItemResponse(BaseModel):
    id: uuid.UUID
    source_id: uuid.UUID
    source_name: Optional[str] = None
    title: str
    summary: Optional[str] = None
    author: Optional[str] = None
    url: str
    published_at: Optional[datetime] = None
    tags: Optional[List[str]] = []
    impact_score: Optional[float] = 0.0
    cluster_id: Optional[str] = None
    is_duplicate: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class PaginatedNewsResponse(BaseModel):
    items: List[NewsItemResponse]
    total: int
    page: int
    page_size: int

class FavoriteCreateRequest(BaseModel):
    news_item_id: uuid.UUID

class FavoriteResponse(BaseModel):
    id: uuid.UUID
    news_item_id: uuid.UUID
    news_item: Optional[NewsItemResponse] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class PaginatedFavoritesResponse(BaseModel):
    items: List[FavoriteResponse]
    total: int
    page: int
    page_size: int

class BroadcastRequest(BaseModel):
    favorite_id: uuid.UUID
    platform: str
    content: str

class BroadcastResponse(BaseModel):
    id: uuid.UUID
    favorite_id: uuid.UUID
    platform: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class SystemStatsResponse(BaseModel):
    total_articles: int
    total_sources: int
    active_sources: int
    dedup_rate_percentage: float
    average_impact: float

class AIMessageRequest(BaseModel):
    news_item_id: uuid.UUID

class AIResponse(BaseModel):
    generated_content: str
