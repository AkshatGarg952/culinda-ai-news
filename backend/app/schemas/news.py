from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional
from datetime import datetime
import uuid

class ParsedArticle(BaseModel):
    title: str
    summary: str
    author: Optional[str] = None
    url: str
    published_at: Optional[datetime] = None
    source_id: uuid.UUID

class ProcessedArticle(ParsedArticle):
    tags: List[str] = Field(default_factory=list)
    impact_score: float = 0.0
    cluster_id: Optional[str] = None
    embedding: Optional[List[float]] = None
    is_duplicate: bool = False
