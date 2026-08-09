"""Source document import API"""

from __future__ import annotations

import hashlib

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import SourceDocument, World
from app.schemas import (
    AiExtractResponse,
    SourceDocumentCatalog,
    SourceDocumentCatalogItem,
    SourceDocumentCreate,
    SourceDocumentResponse,
    SourceDocumentUpdate,
)
from app.services.extraction_service import analyze_and_persist

router = APIRouter(prefix="/api/documents", tags=["Source Documents"])


def content_hash(content: str) -> str:
    normalized = "\n".join(line.rstrip() for line in content.strip().splitlines())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


@router.get("", response_model=list[SourceDocumentResponse])
async def list_documents(
    world_id: str | None = Query(None),
    status: str | None = Query(None),
    source_site: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(SourceDocument).order_by(SourceDocument.updated_at.desc())
    if world_id:
        stmt = stmt.where(SourceDocument.world_id == world_id)
    if status:
        stmt = stmt.where(SourceDocument.status == status)
    if source_site:
        stmt = stmt.where(SourceDocument.source_site == source_site)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/catalog", response_model=SourceDocumentCatalog)
async def document_catalog(
    world_id: str = Query(...),
    status: str | None = Query(None),
    search: str | None = Query(None, max_length=120),
    page: int = Query(1, ge=1),
    page_size: int = Query(30, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Return document metadata without loading article bodies."""
    filters = [SourceDocument.world_id == world_id]
    if status:
        filters.append(SourceDocument.status == status)
    if search:
        filters.append(SourceDocument.title.ilike(f"%{search.strip()}%"))

    total = (
        await db.execute(select(func.count(SourceDocument.id)).where(*filters))
    ).scalar() or 0
    status_rows = (
        await db.execute(
            select(SourceDocument.status, func.count(SourceDocument.id))
            .where(SourceDocument.world_id == world_id)
            .group_by(SourceDocument.status)
        )
    ).all()
    rows = (
        await db.execute(
            select(
                SourceDocument.id,
                SourceDocument.world_id,
                SourceDocument.title,
                SourceDocument.url,
                SourceDocument.source_site,
                SourceDocument.status,
                SourceDocument.analysis_summary,
                SourceDocument.meta,
                SourceDocument.updated_at,
            )
            .where(*filters)
            .order_by(SourceDocument.updated_at.desc(), SourceDocument.title.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
    ).mappings().all()

    return SourceDocumentCatalog(
        items=[SourceDocumentCatalogItem.model_validate(dict(row)) for row in rows],
        total=total,
        page=page,
        page_size=page_size,
        status_counts={row_status: count for row_status, count in status_rows},
    )


@router.get("/{document_id}", response_model=SourceDocumentResponse)
async def get_document(document_id: str, db: AsyncSession = Depends(get_db)):
    document = await db.get(SourceDocument, document_id)
    if not document:
        raise HTTPException(404, "Source document not found")
    return document


@router.post("", response_model=SourceDocumentResponse, status_code=201)
async def create_document(data: SourceDocumentCreate, db: AsyncSession = Depends(get_db)):
    world = await db.get(World, data.world_id)
    if not world:
        raise HTTPException(404, "World not found")

    doc_hash = content_hash(data.content)
    if data.url:
        existing = (
            await db.execute(
                select(SourceDocument).where(
                    SourceDocument.world_id == data.world_id,
                    SourceDocument.url == data.url,
                )
            )
        ).scalar_one_or_none()
        if existing:
            raise HTTPException(409, "Source document URL already exists in this world")

    document = SourceDocument(**data.model_dump(by_alias=True), content_hash=doc_hash)
    db.add(document)
    await db.flush()
    await db.refresh(document)
    return document


@router.patch("/{document_id}", response_model=SourceDocumentResponse)
async def update_document(document_id: str, data: SourceDocumentUpdate, db: AsyncSession = Depends(get_db)):
    document = await db.get(SourceDocument, document_id)
    if not document:
        raise HTTPException(404, "Source document not found")

    update = data.model_dump(exclude_unset=True, by_alias=True)
    if "content" in update:
        document.content_hash = content_hash(update["content"])
    for key, val in update.items():
        setattr(document, key, val)
    await db.flush()
    await db.refresh(document)
    return document


@router.post("/{document_id}/analyze", response_model=AiExtractResponse)
async def analyze_document(document_id: str, db: AsyncSession = Depends(get_db)):
    document = await db.get(SourceDocument, document_id)
    if not document:
        raise HTTPException(404, "Source document not found")
    document.status = "analyzing"
    result = await analyze_and_persist(
        db,
        text=document.content,
        world_id=str(document.world_id),
        source_document_id=str(document.id),
    )
    document.status = "analyzed"
    document.analysis_summary = f"提取实体 {len(result.entities)} 个，事件 {len(result.events)} 个。"
    await db.flush()
    return result


@router.delete("/{document_id}", status_code=204)
async def delete_document(document_id: str, db: AsyncSession = Depends(get_db)):
    document = await db.get(SourceDocument, document_id)
    if not document:
        raise HTTPException(404, "Source document not found")
    await db.delete(document)
