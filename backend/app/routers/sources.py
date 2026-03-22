import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.core.database import get_db
from app.models.schema import Source
from app.schemas.api import SourceResponse, SourceUpdateRequest

router = APIRouter(prefix="/api/sources", tags=["sources"])

@router.get("", response_model=List[SourceResponse])
async def get_sources(session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(Source).order_by(Source.name))
    sources = result.scalars().all()
    # Deduplicate by name for display purposes, keeping the first source per name.
    # The returned source's ID is used for toggling, and all same-named sources
    # are toggled together via the PATCH endpoint below.
    seen_names = set()
    unique_sources = []
    for s in sources:
        if s.name not in seen_names:
            seen_names.add(s.name)
            unique_sources.append(s)
    return unique_sources

@router.patch("/{source_id}", response_model=SourceResponse)
async def update_source(source_id: uuid.UUID, req: SourceUpdateRequest, session: AsyncSession = Depends(get_db)):
    # Find the target source
    result = await session.execute(select(Source).where(Source.id == source_id))
    source = result.scalars().first()
    
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    # Toggle ALL sources sharing the same name so the UI stays consistent
    # (multiple URLs may exist under the same source name)
    all_result = await session.execute(select(Source).where(Source.name == source.name))
    all_sources = all_result.scalars().all()
    for s in all_sources:
        s.active = req.active

    await session.commit()
    await session.refresh(source)
    return source
