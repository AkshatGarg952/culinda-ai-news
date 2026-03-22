import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List

from app.core.database import get_db
from app.core.config import settings
import smtplib
from email.mime.text import MIMEText
from app.models.schema import BroadcastLog, Favorite, PlatformType
from app.schemas.api import BroadcastRequest, BroadcastResponse

router = APIRouter(prefix="/api/broadcast", tags=["broadcast"])

@router.post("", response_model=BroadcastResponse)
async def trigger_broadcast(req: BroadcastRequest, session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(Favorite).where(Favorite.id == req.favorite_id))
    favorite = result.scalars().first()
    
    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")
        
    try:
        platform_enum = PlatformType(req.platform)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid platform: {req.platform}")
        
    status = "sent"
    if req.platform in ["email", "newsletter"]:
        if settings.smtp_email and settings.smtp_password:
            subject = "AI News Broadcast"
            body = req.content
            if body.startswith("Subject:"):
                parts = body.split("\n", 1)
                subject = parts[0].replace("Subject:", "").strip()
                body = parts[1].strip() if len(parts) > 1 else body
            
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = settings.smtp_email
            msg['To'] = settings.smtp_email # Sent to self for demo
            
            try:
                # Assuming Gmail/App Password for the demo
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                    server.login(settings.smtp_email, settings.smtp_password)
                    server.send_message(msg)
                status = "sent"
            except Exception as e:
                print(f"SMTP Error: {e}")
                status = "failed"
        else:
            status = "failed"
    
    log = BroadcastLog(
        favorite_id=req.favorite_id,
        platform=platform_enum,
        status=status,
        content_snapshot=req.content
    )
    session.add(log)
    await session.commit()
    await session.refresh(log)
    
    return log

@router.get("/history", response_model=List[BroadcastResponse])
async def get_broadcast_history(session: AsyncSession = Depends(get_db)):
    result = await session.execute(
        select(BroadcastLog).order_by(desc(BroadcastLog.created_at)).limit(50)
    )
    return result.scalars().all()
