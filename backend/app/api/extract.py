"""AI 逆向解析引擎 — The Harvester API"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas import AiExtractRequest, AiExtractResponse

router = APIRouter(prefix="/api/extract", tags=["AI Extract"])


@router.post("", response_model=AiExtractResponse)
async def ai_extract(data: AiExtractRequest, db: AsyncSession = Depends(get_db)):
    """
    将原始文本解析为结构化设定。

    流程：
    1. 文本分块
    2. 调用 LLM 进行 NER 实体抽取
    3. 结果结构化并返回
    """
    # TODO: 集成 LangChain + Ollama/OpenAI
    # 当前返回空结构（骨架已就绪）
    return AiExtractResponse(entities=[], events=[])
