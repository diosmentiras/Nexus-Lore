from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Entity, Event, Relation
from app.schemas import AiExtractEntity, AiExtractResponse
from app.services.ai_service import ai_service
from app.services.world_service import resolve_world_id

ENTITY_TYPES = {"character", "faction", "item", "location", "event", "containment"}
RELATION_TYPES = {"ally", "hostile", "neutral", "member", "owns", "located_at", "other"}


def _as_list(value: Any) -> list:
    return value if isinstance(value, list) else []


def _clean_text(value: Any, fallback: str = "") -> str:
    return str(value).strip() if value is not None and str(value).strip() else fallback


async def analyze_and_persist(
    db: AsyncSession,
    *,
    text: str,
    world_id: str | None,
    source_document_id: str | None = None,
    types: list[str] | None = None,
) -> AiExtractResponse:
    resolved_world_id = await resolve_world_id(db, world_id)
    requested_types = types or ["character", "faction", "item", "location", "event", "containment"]
    extracted = await ai_service.extract_lore(text, requested_types)

    existing_entities = (
        await db.execute(select(Entity).where(Entity.world_id == resolved_world_id))
    ).scalars().all()
    entity_by_name = {entity.name: entity for entity in existing_entities}

    response_entities: list[AiExtractEntity] = []

    for raw_entity in extracted["entities"]:
        name = _clean_text(raw_entity.get("name"))
        if not name:
            continue
        entity_type = raw_entity.get("entity_type")
        if entity_type not in ENTITY_TYPES:
            entity_type = "event" if "event" in requested_types else "character"

        entity = entity_by_name.get(name)
        if not entity:
            entity = Entity(
                world_id=resolved_world_id,
                source_document_id=source_document_id,
                name=name,
                entity_type=entity_type,
                extracted_by_ai=True,
            )
            db.add(entity)
            await db.flush()
            entity_by_name[name] = entity

        entity.entity_type = entity.entity_type or entity_type
        entity.summary = _clean_text(raw_entity.get("summary"), entity.summary or None)
        entity.background = _clean_text(raw_entity.get("background"), entity.background or None)
        entity.tags = list(dict.fromkeys([*entity.tags, *[str(tag) for tag in _as_list(raw_entity.get("tags"))]]))
        entity.date = _clean_text(raw_entity.get("date"), entity.date or None)
        entity.date_context = _clean_text(raw_entity.get("date_context"), entity.date_context or None)
        entity.extracted_by_ai = True

        response_entities.append(
            AiExtractEntity(
                name=entity.name,
                entity_type=entity.entity_type,
                summary=entity.summary,
                tags=entity.tags,
                relations=[
                    (
                        _clean_text(rel.get("target")),
                        _clean_text(rel.get("relation_type"), "other"),
                        _clean_text(rel.get("label"), None),
                    )
                    for rel in _as_list(raw_entity.get("relations"))
                    if isinstance(rel, dict) and rel.get("target")
                ],
            )
        )

    await db.flush()

    for raw_entity in extracted["entities"]:
        source = entity_by_name.get(_clean_text(raw_entity.get("name")))
        if not source:
            continue
        for raw_relation in _as_list(raw_entity.get("relations")):
            if not isinstance(raw_relation, dict):
                continue
            target = entity_by_name.get(_clean_text(raw_relation.get("target")))
            if not target or source.id == target.id:
                continue
            relation_type = raw_relation.get("relation_type")
            if relation_type not in RELATION_TYPES:
                relation_type = "other"
            label = _clean_text(raw_relation.get("label"), None)
            existing_relation = (
                await db.execute(
                    select(Relation).where(
                        Relation.world_id == resolved_world_id,
                        Relation.source_id == source.id,
                        Relation.target_id == target.id,
                        Relation.relation_type == relation_type,
                        Relation.label == label,
                    )
                )
            ).scalar_one_or_none()
            if not existing_relation:
                db.add(
                    Relation(
                        world_id=resolved_world_id,
                        source_document_id=source_document_id,
                        source_id=source.id,
                        target_id=target.id,
                        relation_type=relation_type,
                        label=label,
                    )
                )

    response_events: list[dict[str, Any]] = []
    for raw_event in extracted["events"]:
        title = _clean_text(raw_event.get("title"))
        if not title:
            continue
        date = _clean_text(raw_event.get("date"), "unknown")
        names = [_clean_text(name) for name in _as_list(raw_event.get("entities"))]
        entity_ids = [str(entity_by_name[name].id) for name in names if name in entity_by_name]

        existing_event = (
            await db.execute(
                select(Event).where(
                    Event.world_id == resolved_world_id,
                    Event.source_document_id == source_document_id,
                    Event.title == title,
                    Event.date == date,
                )
            )
        ).scalar_one_or_none()
        event = existing_event or Event(
            world_id=resolved_world_id,
            source_document_id=source_document_id,
            title=title,
            date=date,
            extracted_by_ai=True,
        )
        if not existing_event:
            db.add(event)

        event.description = _clean_text(raw_event.get("description"), event.description or None)
        event.date_context = _clean_text(raw_event.get("date_context"), event.date_context or None)
        event.entity_ids = list(dict.fromkeys([*event.entity_ids, *entity_ids]))
        event.tags = list(dict.fromkeys([*event.tags, *[str(tag) for tag in _as_list(raw_event.get("tags"))]]))
        event.extracted_by_ai = True
        response_events.append(
            {
                "title": event.title,
                "description": event.description,
                "date": event.date,
                "date_context": event.date_context,
                "entity_ids": event.entity_ids,
                "tags": event.tags,
            }
        )

    return AiExtractResponse(entities=response_entities, events=response_events)
