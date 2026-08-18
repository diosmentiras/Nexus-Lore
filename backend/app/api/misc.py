"""Dashboard & Export API"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import Entity, Event, LintIssue, Relation, SourceDocument, World
from app.schemas import DashboardOverview, DashboardStats, DashboardWorldSummary

router = APIRouter(prefix="/api", tags=["Dashboard"])


def model_to_dict(model):
    return {column.name: getattr(model, column.name) for column in model.__table__.columns}


@router.get("/version")
async def get_version():
    """获取 Nexus-Lore 版本信息"""
    return {
        "name": "Nexus-Lore",
        "version": "0.2.0",
        "description": "Lore as Data — 自托管世界观构建终端",
        "tagline": "设定即数据",
    }


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard(world_id: str | None = None, db: AsyncSession = Depends(get_db)):
    """获取 Dashboard 统计数据"""
    counts = {}
    for entity_type in ("character", "faction", "item", "location", "event", "containment"):
        stmt = select(func.count(Entity.id)).where(Entity.entity_type == entity_type)
        if world_id:
            stmt = stmt.where(Entity.world_id == world_id)
        result = await db.execute(stmt)
        counts[entity_type] = result.scalar() or 0

    rel_stmt = select(func.count(Relation.id))
    event_stmt = select(func.count(Event.id))
    issue_stmt = select(func.count(LintIssue.id)).where(LintIssue.resolved == False)
    if world_id:
        rel_stmt = rel_stmt.where(Relation.world_id == world_id)
        event_stmt = event_stmt.where(Event.world_id == world_id)
        issue_stmt = issue_stmt.where(LintIssue.world_id == world_id)

    rel_count = (await db.execute(rel_stmt)).scalar() or 0
    event_count = (await db.execute(event_stmt)).scalar() or 0
    issue_count = (await db.execute(issue_stmt)).scalar() or 0

    return DashboardStats(
        characters=counts["character"],
        factions=counts["faction"],
        items=counts["item"],
        relations=rel_count,
        events=event_count,
        issues=issue_count,
    )


@router.get("/dashboard/overview", response_model=DashboardOverview)
async def get_dashboard_overview(db: AsyncSession = Depends(get_db)):
    """Return compact global counts and per-world navigation data."""
    document_counts = (
        select(
            SourceDocument.world_id.label("world_id"),
            func.count(SourceDocument.id).label("document_count"),
            func.sum(case((SourceDocument.status != "missing", 1), else_=0)).label("available_document_count"),
        )
        .group_by(SourceDocument.world_id)
        .subquery()
    )
    entity_counts = (
        select(
            Entity.world_id.label("world_id"),
            func.count(Entity.id).label("entity_count"),
            func.max(case((Entity.entity_type == "world", Entity.id), else_=None)).label("dossier_id"),
        )
        .group_by(Entity.world_id)
        .subquery()
    )
    event_counts = (
        select(Event.world_id.label("world_id"), func.count(Event.id).label("event_count"))
        .group_by(Event.world_id)
        .subquery()
    )
    world_rows = (
        await db.execute(
            select(
                World,
                func.coalesce(document_counts.c.document_count, 0),
                func.coalesce(document_counts.c.available_document_count, 0),
                func.coalesce(entity_counts.c.entity_count, 0),
                func.coalesce(event_counts.c.event_count, 0),
                entity_counts.c.dossier_id,
            )
            .outerjoin(document_counts, document_counts.c.world_id == World.id)
            .outerjoin(entity_counts, entity_counts.c.world_id == World.id)
            .outerjoin(event_counts, event_counts.c.world_id == World.id)
            .where(World.slug != "default")
            .order_by(func.coalesce(document_counts.c.document_count, 0).desc(), World.name.asc())
        )
    ).all()

    async def count(stmt):
        return (await db.execute(stmt)).scalar() or 0

    document_count = await count(select(func.count(SourceDocument.id)))
    missing_count = await count(select(func.count(SourceDocument.id)).where(SourceDocument.status == "missing"))
    issue_count = await count(select(func.count(LintIssue.id)).where(LintIssue.resolved == False))

    return DashboardOverview(
        worlds=len(world_rows),
        documents=document_count,
        available_documents=document_count - missing_count,
        missing_documents=missing_count,
        lore=await count(select(func.count(Entity.id))),
        relations=await count(select(func.count(Relation.id))),
        events=await count(select(func.count(Event.id))),
        issues=issue_count,
        world_summaries=[
            DashboardWorldSummary(
                id=str(world.id),
                name=world.name,
                slug=world.slug,
                description=world.description,
                source_url=world.source_url,
                document_count=document_count,
                available_document_count=available_document_count,
                entity_count=entity_count,
                event_count=event_count,
                dossier_id=str(dossier_id) if dossier_id else None,
            )
            for world, document_count, available_document_count, entity_count, event_count, dossier_id in world_rows
        ],
    )


@router.get("/export")
async def export_data(world_id: str | None = None, db: AsyncSession = Depends(get_db)):
    """导出全部世界观数据为 JSON"""
    world_stmt = select(World)
    entity_stmt = select(Entity)
    relation_stmt = select(Relation)
    event_stmt = select(Event)
    document_stmt = select(SourceDocument)
    if world_id:
        world_stmt = world_stmt.where(World.id == world_id)
        entity_stmt = entity_stmt.where(Entity.world_id == world_id)
        relation_stmt = relation_stmt.where(Relation.world_id == world_id)
        event_stmt = event_stmt.where(Event.world_id == world_id)
        document_stmt = document_stmt.where(SourceDocument.world_id == world_id)

    worlds = (await db.execute(world_stmt)).scalars().all()
    documents = (await db.execute(document_stmt)).scalars().all()
    entities = (await db.execute(entity_stmt)).scalars().all()
    relations = (await db.execute(relation_stmt)).scalars().all()
    events = (await db.execute(event_stmt)).scalars().all()

    return {
        "worlds": [model_to_dict(w) for w in worlds],
        "documents": [model_to_dict(d) for d in documents],
        "entities": [model_to_dict(e) for e in entities],
        "relations": [model_to_dict(r) for r in relations],
        "events": [model_to_dict(e) for e in events],
    }
