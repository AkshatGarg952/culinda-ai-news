import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.config import settings
from app.models.schema import NewsItem
from app.schemas.api import AIMessageRequest, AIResponse
import google.generativeai as genai

if settings.gemini_api_key:
    genai.configure(api_key=settings.gemini_api_key)

router = APIRouter(prefix="/api/ai", tags=["ai"])

@router.post("/linkedin-caption", response_model=AIResponse)
async def generate_linkedin_caption(req: AIMessageRequest, session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(NewsItem).where(NewsItem.id == req.news_item_id))
    item = result.scalars().first()
    
    if not item:
        raise HTTPException(status_code=404, detail="News item not found")

    if not settings.gemini_api_key:
        fallback = f"Exciting news in AI!\n\n{item.title}\n\n{item.summary or ''}\n\nRead more: {item.url}\n\n#AI #MachineLearning #Tech"
        return AIResponse(generated_content=fallback)
        
    prompt = f"""
    Write a professional LinkedIn post about this news:
    Title: {item.title}
    Summary: {item.summary}
    Include a hook, 2 key insights, and 5 relevant hashtags.
    """
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"temperature": 0.7})
        response = await model.generate_content_async(prompt)
        return AIResponse(generated_content=response.text)
    except Exception:
        fallback = f"Exciting news in AI!\n\n{item.title}\n\n{item.summary or ''}\n\nRead more: {item.url}\n\n#AI #MachineLearning #Tech"
        return AIResponse(generated_content=fallback)

@router.post("/blog-paragraph", response_model=AIResponse)
async def generate_blog_paragraph(req: AIMessageRequest, session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(NewsItem).where(NewsItem.id == req.news_item_id))
    item = result.scalars().first()
    
    if not item:
        raise HTTPException(status_code=404, detail="News item not found")

    if not settings.gemini_api_key:
        fallback = f"{item.title}\n\n{item.summary or 'No summary available.'}\n\nSource: {item.url}"
        return AIResponse(generated_content=fallback)
        
    prompt = f"Write a 150-word blog paragraph summarizing this article: '{item.title}'. Include attribution to {item.author or 'the author'}. Summary: {item.summary}"
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"temperature": 0.5})
        response = await model.generate_content_async(prompt)
        return AIResponse(generated_content=response.text)
    except Exception:
        fallback = f"{item.title}\n\n{item.summary or 'No summary available.'}\n\nSource: {item.url}"
        return AIResponse(generated_content=fallback)

from typing import List
from pydantic import BaseModel

class AIDigestRequest(BaseModel):
    news_item_ids: List[uuid.UUID]

@router.post("/newsletter-digest", response_model=AIResponse)
async def generate_newsletter_digest(req: AIDigestRequest, session: AsyncSession = Depends(get_db)):
    if not req.news_item_ids:
        raise HTTPException(status_code=400, detail="No articles provided for digest")
        
    statement = select(NewsItem).where(NewsItem.id.in_(req.news_item_ids))
    result = await session.execute(statement)
    items = result.scalars().all()
    
    if not items:
        raise HTTPException(status_code=404, detail="Articles not found")
        
    articles_context = "\n\n".join([f"Headline: {item.title}\nSummary: {item.summary}" for item in items])
    
    prompt = f"""
    Create a professional AI newsletter digest covering the following stories.
    Include a short, engaging introductory paragraph, followed by a bulleted summary of each story.
    
    Stories:
    {articles_context}
    """
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"temperature": 0.6})
        response = await model.generate_content_async(prompt)
        return AIResponse(generated_content=response.text)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to generate digest")
