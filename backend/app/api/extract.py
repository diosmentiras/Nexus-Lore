"""AI 逆向解析引擎 — The Harvester API"""

from __future__ import annotations

import httpx
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas import AiExtractRequest, AiExtractResponse
from app.services.ai_service import ai_service
from app.services.extraction_service import analyze_and_persist

router = APIRouter(prefix="/api/extract", tags=["AI Extract"])


@router.get("/status")
async def ai_status():
    return ai_service.public_config()


@router.post("/test")
async def test_ai_connection():
    try:
        return await ai_service.test_connection()
    except httpx.HTTPError as exc:
        return {"ok": False, "provider": ai_service.provider, "detail": str(exc)}


@router.post("", response_model=AiExtractResponse)
async def ai_extract(data: AiExtractRequest, db: AsyncSession = Depends(get_db)):
    """
    将原始文本解析为结构化设定。

    流程：
    1. 文本分块
    2. 调用 LLM 进行 NER 实体抽取
    3. 结果结构化并返回
    """
    return await analyze_and_persist(
        db,
        text=data.text,
        world_id=data.world_id,
        source_document_id=data.source_document_id,
        types=data.types,
    )
