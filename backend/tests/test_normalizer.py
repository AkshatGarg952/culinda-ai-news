import pytest
from app.schemas.news import ParsedArticle
from app.services.normalizer import normalize_article

def test_normalize_article_html_stripping():
    raw = ParsedArticle(
        title="Breaking <script>alert('xss')</script> News",
        summary="<p>This is a <b>bold</b> statement with <a href='link'>links</a>.</p>",
        url="https://example.com/news?tracking_id=123",
        source_id="00000000-0000-0000-0000-000000000001"
    )
    
    normalized = normalize_article(raw)
    
    assert "Breaking News" in normalized.title
    assert "<script>" not in normalized.title
    assert "This is a bold statement with links ." == normalized.summary
    assert "<b>" not in normalized.summary

def test_normalize_article_url_cleaning():
    raw = ParsedArticle(
        title="Test",
        summary="Test",
        url="https://example.com/article?utm_source=twitter&utm_medium=social&v=1.0",
        source_id="00000000-0000-0000-0000-000000000001"
    )
    
    normalized = normalize_article(raw)
    
    assert normalized.url == "https://example.com/article?v=1.0"
    assert "utm_source" not in normalized.url

def test_normalize_article_summary_truncation():
    long_text = "A" * 6000
    raw = ParsedArticle(
        title="Test",
        summary=long_text,
        url="https://example.com",
        source_id="00000000-0000-0000-0000-000000000001"
    )
    
    normalized = normalize_article(raw)
    assert len(normalized.summary) == 500
    assert normalized.summary.endswith("...")
