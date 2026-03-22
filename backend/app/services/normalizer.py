import re
from datetime import datetime, timezone
from bs4 import BeautifulSoup

from app.schemas.news import ParsedArticle

def strip_html(content: str) -> str:
    if not content:
        return ""
    soup = BeautifulSoup(content, "lxml")
    text = soup.get_text(separator=" ", strip=True)
    return re.sub(r'\s+', ' ', text)

from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

def clean_url(url: str) -> str:
    parsed = urlparse(url)
    query_params = parse_qsl(parsed.query, keep_blank_values=True)
    cleaned_params = [(k, v) for k, v in query_params if not k.startswith('utm_')]
    new_query = urlencode(cleaned_params)
    return urlunparse(parsed._replace(query=new_query))


def normalize_article(article: ParsedArticle) -> ParsedArticle:
    article.title = strip_html(article.title)
    
    clean_summary = strip_html(article.summary)
    if len(clean_summary) > 500:
        clean_summary = clean_summary[:497] + "..."
    article.summary = clean_summary
    
    article.url = clean_url(article.url)
    
    if article.published_at:
        if article.published_at.tzinfo is None:
            article.published_at = article.published_at.replace(tzinfo=timezone.utc)
    else:
        article.published_at = datetime.now(timezone.utc)
        
    return article
