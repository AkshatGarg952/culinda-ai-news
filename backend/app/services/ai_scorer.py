import json
import google.generativeai as genai
from app.core.config import settings
from app.schemas.news import ProcessedArticle

if settings.gemini_api_key:
    genai.configure(api_key=settings.gemini_api_key)

async def generate_impact_and_tags(article_title: str, article_summary: str) -> dict:
    if not settings.gemini_api_key:
        return {"impact_score": 0.5, "tags": []}

    prompt = f"""
    Analyze the following AI news article.
    Title: {article_title}
    Summary: {article_summary}
    
    Provide:
    1. impact_score: A float from 0.0 to 1.0 representing industry significance.
    2. tags: A list of 3-5 relevant string keywords.
    
    Return pure JSON:
    {{
        "impact_score": 0.0,
        "tags": []
    }}
    """
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"temperature": 0.3, "response_mime_type": "application/json"})
        response = await model.generate_content_async(
            contents=[{"role": "user", "parts": [{"text": "You are an AI news analyst.\n" + prompt}]}]
        )
        
        content = response.text
        return json.loads(content)
        
    except Exception as e:
        return {"impact_score": 0.5, "tags": []}

async def generate_embeddings(text: str) -> list[float]:
    if not settings.gemini_api_key:
        return []
        
    try:
        response = genai.embed_content(
            model="models/text-embedding-004",
            content=text,
            task_type="retrieval_document"
        )
        return response['embedding']
    except Exception:
        return []

async def enrich_article(article: ProcessedArticle) -> ProcessedArticle:
    ai_data = await generate_impact_and_tags(article.title, article.summary)
    
    article.impact_score = ai_data.get("impact_score", 0.5)
    article.tags = ai_data.get("tags", [])
    
    text_for_embedding = f"{article.title}. {article.summary}"
    embedding = await generate_embeddings(text_for_embedding)
    if embedding:
        article.embedding = embedding
        
    return article
