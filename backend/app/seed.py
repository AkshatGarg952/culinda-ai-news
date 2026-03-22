import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession  # noqa: F401
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.schema import Source, SourceType

logger = logging.getLogger(__name__)

INITIAL_SOURCES = [
    {"name": "OpenAI Blog", "url": "https://openai.com/blog/rss.xml", "type": SourceType.rss},
    {"name": "Google AI Blog", "url": "https://blog.google/technology/ai/rss/", "type": SourceType.rss},
    {"name": "Meta AI", "url": "https://ai.meta.com/blog/rss/", "type": SourceType.rss},
    {"name": "Anthropic", "url": "https://www.anthropic.com/rss/all.xml", "type": SourceType.rss},
    {"name": "DeepMind", "url": "https://deepmind.google/blog/rss/", "type": SourceType.rss},
    {"name": "Hugging Face", "url": "https://huggingface.co/blog/feed.xml", "type": SourceType.rss},
    {"name": "TechCrunch AI", "url": "https://techcrunch.com/category/artificial-intelligence/feed/", "type": SourceType.rss},
    {"name": "VentureBeat AI", "url": "https://venturebeat.com/category/ai/feed", "type": SourceType.rss},
    {"name": "The Verge Tech", "url": "https://www.theverge.com/rss/index.xml", "type": SourceType.rss},
    {"name": "Wired AI", "url": "https://www.wired.com/feed/tag/artificial-intelligence/latest/rss", "type": SourceType.rss},
    {"name": "MIT Tech Review", "url": "https://www.technologyreview.com/topic/artificial-intelligence/feed", "type": SourceType.rss},
    {"name": "Y Combinator Blog", "url": "https://ycombinator.com/blog/feed/", "type": SourceType.rss},
    {"name": "arXiv cs.AI", "url": "https://export.arxiv.org/api/query?search_query=cat:cs.AI&sortBy=lastUpdatedDate&sortOrder=descending", "type": SourceType.api},
    {"name": "arXiv cs.LG", "url": "https://export.arxiv.org/api/query?search_query=cat:cs.LG&sortBy=lastUpdatedDate&sortOrder=descending", "type": SourceType.api},
    {"name": "PapersWithCode", "url": "https://paperswithcode.com/trends/rss", "type": SourceType.rss},
    {"name": "Product Hunt AI", "url": "https://www.producthunt.com/feed?category=artificial-intelligence", "type": SourceType.rss},
    {"name": "Hacker News AI", "url": "https://hnrss.org/newest?q=AI+OR+LLM+OR+machine+learning&count=30", "type": SourceType.rss},
    {"name": "Reddit MachineLearning", "url": "https://www.reddit.com/r/MachineLearning/new/.rss", "type": SourceType.rss},
    {"name": "Microsoft AI Blog", "url": "https://blogs.microsoft.com/ai/feed/", "type": SourceType.rss},
    {"name": "Stability AI Blog", "url": "https://stability.ai/news?format=rss", "type": SourceType.rss},
]

async def seed_sources() -> int:
    added_count = 0

    async with AsyncSessionLocal() as session:
        for source_data in INITIAL_SOURCES:
            statement = select(Source).where(Source.url == source_data["url"])
            result = await session.execute(statement)
            existing_source = result.scalars().first()
            
            if not existing_source:
                new_source = Source(
                    name=source_data["name"],
                    url=source_data["url"],
                    type=source_data["type"]
                )
                session.add(new_source)
                added_count += 1
        
        await session.commit()
        logger.info("initial_sources_seeded", added=added_count)
        return added_count


def main() -> None:
    asyncio.run(seed_sources())


if __name__ == "__main__":
    main()
