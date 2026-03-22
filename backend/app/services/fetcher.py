import httpx
import feedparser
from bs4 import BeautifulSoup
from typing import List
import structlog
from datetime import datetime

from app.models.schema import Source, SourceType
from app.schemas.news import ParsedArticle

logger = structlog.get_logger()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; CulindaBot/1.0; +https://culinda.ai)"
}

async def fetch_rss(url: str) -> dict:
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True, headers=HEADERS) as client:
        response = await client.get(url)
        response.raise_for_status()
        return feedparser.parse(response.content)

async def fetch_json_api(url: str) -> dict:
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True, headers=HEADERS) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()

async def fetch_html(url: str) -> str:
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True, headers=HEADERS) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.text


def parse_rss_entries(feed: dict, source: Source) -> List[ParsedArticle]:
    articles = []
    for entry in feed.entries[:20]:
        title = entry.get('title', '')
        link = entry.get('link', '')
        
        if not title or not link:
            continue
            
        summary = entry.get('summary', '') or entry.get('description', '')
        author = entry.get('author', None)
        
        # feedparser standardizes dates to struct_time or uses published
        published_parsed = entry.get('published_parsed')
        published_date = None
        if published_parsed:
            published_date = datetime(*published_parsed[:6])
            
        articles.append(ParsedArticle(
            title=title,
            summary=summary,
            url=link,
            author=author,
            published_at=published_date,
            source_id=source.id
        ))
        
    return articles

def parse_api_entries(data: dict, source: Source) -> List[ParsedArticle]:
    # Custom parser depending on the API structure. 
    # For now we assume a standard list of items if it's generic.
    # We would add specific mapping logic here per API.
    # E.g. arXiv xml mapping if treating arXiv as REST API instead of raw feed
    
    articles = []
    # simplified representation 
    items = data.get('items', []) or data.get('articles', [])
    for item in items[:20]:
        articles.append(ParsedArticle(
            title=item.get('title', ''),
            summary=item.get('description', ''),
            url=item.get('url', ''),
            author=item.get('author'),
            source_id=source.id
        ))
    return articles

def scrape_html_articles(html: str, source: Source) -> List[ParsedArticle]:
    soup = BeautifulSoup(html, 'lxml')
    articles = []
    
    for article in soup.find_all('article')[:20]:
        title_el = article.find(['h1', 'h2', 'h3'])
        link_el = article.find('a')
        
        if title_el and link_el:
            title = title_el.get_text(strip=True)
            url = link_el.get('href', '')
            
            if url.startswith('/'):
                # Handle relative links by joining with source base URL (omitted for brevity)
                pass
                
            summary_el = article.find(['p', 'div', 'span'])
            summary = summary_el.get_text(strip=True) if summary_el else ""
            
            articles.append(ParsedArticle(
                title=title,
                summary=summary,
                url=url,
                source_id=source.id
            ))
            
    return articles

async def fetch_source_articles(source: Source) -> List[ParsedArticle]:
    try:
        if source.type == SourceType.rss:
            feed = await fetch_rss(source.url)
            return parse_rss_entries(feed, source)
            
        elif source.type == SourceType.api:
            data = await fetch_json_api(source.url)
            return parse_api_entries(data, source)
            
        elif source.type == SourceType.scrape:
            html = await fetch_html(source.url)
            return scrape_html_articles(html, source)
            
    except Exception as e:
        logger.error(f"failed_fetching_source", source_id=str(source.id), target=source.url, error=str(e))
        return []

    return []
