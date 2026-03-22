import difflib
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from datetime import datetime, timedelta, timezone

from app.schemas.news import ProcessedArticle
from app.models.schema import NewsItem

async def check_duplicate(session: AsyncSession, article: ProcessedArticle) -> tuple[bool, str | None]:
    stmt = select(NewsItem).where(NewsItem.url == article.url)
    result = await session.execute(stmt)
    if result.scalars().first():
        return True, None

    # Strip timezone info so it matches the TIMESTAMP WITHOUT TIME ZONE column
    recent_limit = (datetime.now(timezone.utc) - timedelta(hours=48)).replace(tzinfo=None)

    stmt = select(NewsItem).where(NewsItem.published_at >= recent_limit)
    result = await session.execute(stmt)
    recent_items = result.scalars().all()

    for item in recent_items:
        ratio = difflib.SequenceMatcher(None, article.title.lower(), item.title.lower()).ratio()
        if ratio > 0.85:
            return True, None

    if not article.embedding:
        return False, None

    embedding_str = "[" + ",".join(map(str, article.embedding)) + "]"
    query = text("""
        SELECT id, cluster_id, 1 - (embedding <=> :embedding) as similarity 
        FROM news_items 
        WHERE published_at >= :recent_limit
        AND embedding IS NOT NULL
        ORDER BY similarity DESC LIMIT 1
    """)

    sim_result = await session.execute(query, {
        "embedding": embedding_str,
        "recent_limit": recent_limit
    })

    top_match = sim_result.fetchone()
    if top_match:
        sim = getattr(top_match, "similarity", 0)
        if sim > 0.88:
            return True, None
        elif sim > 0.70:
            c_id = getattr(top_match, "cluster_id", None) or str(getattr(top_match, "id", ""))
            return False, c_id

    return False, None
