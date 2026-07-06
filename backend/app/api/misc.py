"""Dashboard & Export API"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import Entity, Event, LintIssue, Relation
from app.schemas import DashboardStats


@router.get("/version")
async def get_version():
    """获取 Nexus-Lore 版本信息"""
    return {
        "name": "Nexus-Lore",
        "version": "0.1.0",
        "description": "Lore as Data — 自托管世界观构建终端",
        "tagline": "设定即数据"
    }

router = APIRouter(prefix="/api", tags=["Dashboard"])


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard(db: AsyncSession = Depends(get_db)):
    """获取 Dashboard 统计数据"""
    counts = {}
    for entity_type in ("character", "faction", "item", "location", "event", "containment"):
        result = await db.execute(
            select(func.count(Entity.id)).where(Entity.entity_type == entity_type)
        )
        counts[entity_type] = result.scalar() or 0

    rel_count = (await db.execute(select(func.count(Relation.id)))).scalar() or 0
    event_count = (await db.execute(select(func.count(Event.id)))).scalar() or 0
    issue_count = (await db.execute(select(func.count(LintIssue.id)).where(LintIssue.resolved == False))).scalar() or 0

    return DashboardStats(
        characters=counts["character"],
        factions=counts["faction"],
        items=counts["item"],
        relations=rel_count,
        events=event_count,
        issues=issue_count,
    )


@router.get("/export")
async def export_data(db: AsyncSession = Depends(get_db)):
    """导出全部世界观数据为 JSON"""
    entities = (await db.execute(select(Entity))).scalars().all()
    relations = (await db.execute(select(Relation))).scalars().all()
    events = (await db.execute(select(Event))).scalars().all()

    return {
        "entities": [e.__dict__ for e in entities],
        "relations": [r.__dict__ for r in relations],
        "events": [e.__dict__ for e in events],
    }
