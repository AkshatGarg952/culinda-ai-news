import pytest
from unittest.mock import AsyncMock, MagicMock
from app.schemas.news import ProcessedArticle
from app.services.dedup import check_duplicate

@pytest.mark.asyncio
async def test_check_duplicate_exact_url():
    session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars().first.return_value = True
    session.execute.return_value = mock_result
    
    article = ProcessedArticle(
        source_id="00000000-0000-0000-0000-000000000001",
        title="Exact URL Match",
        summary="Test",
        url="https://test.com/123",
        published_at="2026-03-18T10:00:00Z"
    )
    
    is_dup, cluster_id = await check_duplicate(session, article)
    assert is_dup is True
    assert cluster_id is None

@pytest.mark.asyncio
async def test_check_duplicate_fuzzy_title():
    session = AsyncMock()
    
    # Setup mock to return no URL match, but return recent items for fuzzy match
    mock_url_result = MagicMock()
    mock_url_result.scalars().first.return_value = None
    
    mock_recent_result = MagicMock()
    existing_item = MagicMock()
    existing_item.title = "Google Announces New AI Model"
    mock_recent_result.scalars().all.return_value = [existing_item]
    
    session.execute.side_effect = [mock_url_result, mock_recent_result]
    
    article = ProcessedArticle(
        source_id="00000000-0000-0000-0000-000000000001",
        title="Google announces a new AI model",
        summary="Test",
        url="https://test.com/456",
        published_at="2026-03-18T10:00:00Z"
    )
    
    is_dup, cluster_id = await check_duplicate(session, article)
    assert is_dup is True
    assert cluster_id is None
