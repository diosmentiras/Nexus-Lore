"""Relation (图谱关系) CRUD + Graph API"""

from __future__ import annotations



from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models import Entity, Relation, SourceDocument
from app.schemas import (
    GraphLink,
    GraphNode,
    GraphResponse,
    RelationCreate,
    RelationResponse,
)
from app.services.world_service import resolve_world_id

router = APIRouter(prefix="/api/relations", tags=["Relations"])


@router.get("", response_model=list[RelationResponse])
async def list_relations(
    world_id: str | None = None,
    source_id: str | None = None,
    target_id: str | None = None,
    relation_type: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Relation).order_by(Relation.created_at.desc())
    if world_id:
        stmt = stmt.where(Relation.world_id == world_id)
    if source_id:
        stmt = stmt.where(Relation.source_id == source_id)
    if target_id:
        stmt = stmt.where(Relation.target_id == target_id)
    if relation_type:
        stmt = stmt.where(Relation.relation_type == relation_type)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("", response_model=RelationResponse, status_code=201)
async def create_relation(data: RelationCreate, db: AsyncSession = Depends(get_db)):
    # 验证源和目标实体存在
    src = await db.get(Entity, data.source_id)
    tgt = await db.get(Entity, data.target_id)
    if not src or not tgt:
        raise HTTPException(404, "Source or target entity not found")
    if src.world_id and tgt.world_id and str(src.world_id) != str(tgt.world_id):
        raise HTTPException(400, "Source and target entities belong to different worlds")
    values = data.model_dump(by_alias=True)
    values["world_id"] = values.get("world_id") or src.world_id or tgt.world_id
    values["world_id"] = await resolve_world_id(db, str(values["world_id"]) if values["world_id"] else None)
    relation = Relation(**values)
    db.add(relation)
    await db.flush()
    await db.refresh(relation)
    return relation


@router.delete("/{relation_id}", status_code=204)
async def delete_relation(relation_id: str, db: AsyncSession = Depends(get_db)):
    relation = await db.get(Relation, relation_id)
    if not relation:
        raise HTTPException(404, "Relation not found")
    await db.delete(relation)


@router.get("/graph", response_model=GraphResponse)
async def get_graph(
    world_id: str | None = None,
    faction: str | None = None,
    relation_type: str | None = None,
    tag: str | None = None,
    include_documents: bool = False,
    db: AsyncSession = Depends(get_db),
):
    """构建 Nexus 拓扑星图数据"""
    # 查询实体
    entity_stmt = select(Entity)
    if world_id:
        entity_stmt = entity_stmt.where(Entity.world_id == world_id)
    if faction:
        entity_stmt = entity_stmt.where(Entity.faction_id.isnot(None))
    if tag:
        entity_stmt = entity_stmt.where(Entity.tags.any(tag))
    entities = (await db.execute(entity_stmt)).scalars().all()

    # 查询关系
    rel_stmt = select(Relation)
    if world_id:
        rel_stmt = rel_stmt.where(Relation.world_id == world_id)
    if relation_type:
        rel_stmt = rel_stmt.where(Relation.relation_type == relation_type)
    relations = (await db.execute(rel_stmt)).scalars().all()

    # 实体颜色映射
    type_colors = {
        "character": "#00f0ff",
        "faction": "#ff00aa",
        "item": "#ffd700",
        "location": "#00ff88",
        "event": "#ffaa00",
        "containment": "#ff3355",
    }

    rel_colors = {
        "ally": "#00ff88",
        "hostile": "#ff3355",
        "neutral": "#8888aa",
        "member": "#a855f7",
    }

    entity_map = {str(e.id): e for e in entities}

    nodes = [
        GraphNode(
            id=str(e.id),
            name=e.name,
            entity_type=e.entity_type,
            color=type_colors.get(e.entity_type, "#00f0ff"),
            faction=str(e.faction_id) if e.faction_id else None,
            summary=e.summary,
            tags=e.tags,
            canonical_name=e.meta.get("canonical_name") if isinstance(e.meta, dict) else None,
        )
        for e in entities
    ]

    links = [
        GraphLink(
            source=str(r.source_id),
            target=str(r.target_id),
            relation_type=r.relation_type,
            label=r.label,
            color=rel_colors.get(r.relation_type, "#2a2a4a"),
        )
        for r in relations
        if str(r.source_id) in entity_map and str(r.target_id) in entity_map
    ]

    if include_documents:
        document_stmt = select(SourceDocument)
        if world_id:
            document_stmt = document_stmt.where(SourceDocument.world_id == world_id)
        documents = (await db.execute(document_stmt)).scalars().all()
        document_map = {str(document.id): document for document in documents}
        used_document_ids: set[str] = set()

        for entity in entities:
            stories = entity.meta.get("stories", []) if isinstance(entity.meta, dict) else []
            for story in stories if isinstance(stories, list) else []:
                document_id = story.get("document_id") if isinstance(story, dict) else None
                if not document_id or document_id not in document_map:
                    continue
                used_document_ids.add(document_id)
                links.append(
                    GraphLink(
                        source=str(entity.id),
                        target=document_id,
                        relation_type="appears_in",
                        label="出现于",
                        color="#8b5cf6",
                    )
                )

        nodes.extend(
            GraphNode(
                id=document_id,
                name=document_map[document_id].title,
                entity_type="source",
                color="#8b5cf6" if document_map[document_id].status != "missing" else "#ff3355",
                size=10,
                summary=document_map[document_id].analysis_summary,
                url=document_map[document_id].url,
                status=document_map[document_id].status,
                tags=["来源文章"],
            )
            for document_id in sorted(used_document_ids)
        )

    return GraphResponse(nodes=nodes, links=links)
