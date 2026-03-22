import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Float, ForeignKey, Text, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
import enum

from app.models.base import Base

class SourceType(str, enum.Enum):
    rss = "rss"
    api = "api"
    scrape = "scrape"

class PlatformType(str, enum.Enum):
    email = "email"
    linkedin = "linkedin"
    whatsapp = "whatsapp"
    blog = "blog"
    newsletter = "newsletter"

class BroadcastStatus(str, enum.Enum):
    sent = "sent"
    failed = "failed"
    pending = "pending"

class UserRole(str, enum.Enum):
    admin = "admin"
    user = "user"

class Source(Base):
    __tablename__ = "sources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    url = Column(String, unique=True, nullable=False)
    type = Column(Enum(SourceType), nullable=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    news_items = relationship("NewsItem", back_populates="source")

class NewsItem(Base):
    __tablename__ = "news_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = Column(UUID(as_uuid=True), ForeignKey("sources.id"))
    title = Column(String, nullable=False)
    summary = Column(Text)
    author = Column(String)
    url = Column(String, unique=True, nullable=False)
    published_at = Column(DateTime)
    tags = Column(JSONB)
    is_duplicate = Column(Boolean, default=False)
    impact_score = Column(Float)
    cluster_id = Column(String)
    embedding = Column(Vector(1536))
    created_at = Column(DateTime, default=datetime.utcnow)

    source = relationship("Source", back_populates="news_items")
    favorites = relationship("Favorite", back_populates="news_item")

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.user)
    created_at = Column(DateTime, default=datetime.utcnow)

    favorites = relationship("Favorite", back_populates="user")

class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    news_item_id = Column(UUID(as_uuid=True), ForeignKey("news_items.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="favorites")
    news_item = relationship("NewsItem", back_populates="favorites")
    broadcast_logs = relationship("BroadcastLog", back_populates="favorite")

class BroadcastLog(Base):
    __tablename__ = "broadcast_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    favorite_id = Column(UUID(as_uuid=True), ForeignKey("favorites.id"))
    platform = Column(Enum(PlatformType), nullable=False)
    status = Column(Enum(BroadcastStatus), default=BroadcastStatus.pending)
    content_snapshot = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    favorite = relationship("Favorite", back_populates="broadcast_logs")
