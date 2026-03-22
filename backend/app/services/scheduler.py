import asyncio
import structlog
from datetime import datetime, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.schema import Source, NewsItem
from app.schemas.news import ProcessedArticle
from app.services.fetcher import fetch_source_articles
from app.services.normalizer import normalize_article
from app.services.ai_scorer import enrich_article
from app.services.dedup import check_duplicate

logger = structlog.get_logger()
scheduler = AsyncIOScheduler()

async def process_articles(session: AsyncSession, source: Source):
    raw_articles = await fetch_source_articles(source)
    added_count = 0
    dup_count = 0

    for raw in raw_articles:
        try:
            normalized = normalize_article(raw)
            processed = ProcessedArticle(**normalized.model_dump())
            
            is_dup, cluster_id = await check_duplicate(session, processed)
            
            if is_dup:
                dup_count += 1
                continue
                
            enriched = await enrich_article(processed)
            
            pub_at = enriched.published_at
            if pub_at and pub_at.tzinfo is not None:
                pub_at = pub_at.replace(tzinfo=None)

            new_item = NewsItem(
                source_id=enriched.source_id,
                title=enriched.title,
                summary=enriched.summary,
                author=enriched.author,
                url=enriched.url,
                published_at=pub_at,
                tags=enriched.tags,
                impact_score=enriched.impact_score,
                embedding=enriched.embedding,
                cluster_id=cluster_id,
                is_duplicate=False
            )
            
            session.add(new_item)
            await session.flush()
            added_count += 1
            
        except Exception as e:
            logger.error("error_processing_article", url=raw.url, error=str(e))
            await session.rollback()
            continue
            
    await session.commit()
    logger.info("source_processed", source=source.name, added=added_count, duplicates=dup_count)

async def process_source(source: Source):
    # Each source gets its own isolated session so errors don't cascade across sources
    async with AsyncSessionLocal() as session:
        await process_articles(session, source)

async def run_ingestion_cycle():
    logger.info("starting_ingestion_cycle")
    
    async with AsyncSessionLocal() as session:
        statement = select(Source).where(Source.active == True)
        result = await session.execute(statement)
        sources = result.scalars().all()
        
    tasks = [process_source(source) for source in sources]
        
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)
            
    logger.info("completed_ingestion_cycle")

def start_scheduler():
    scheduler.add_job(run_ingestion_cycle, "interval", minutes=15)
    scheduler.start()
    logger.info("scheduler_started")
