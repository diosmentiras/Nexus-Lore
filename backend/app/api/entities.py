"""Entity CRUD API"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import Entity
from app.schemas import EntityCreate, EntityResponse, EntityUpdate
from app.services.world_service import resolve_world_id

router = APIRouter(prefix="/api/entities", tags=["Entities"])


@router.get("", response_model=list[EntityResponse])
async def list_entities(
    world_id: str | None = Query(None),
    type: str | None = Query(None),
    search: str | None = Query(None),
    tag: str | None = Query(None),
    faction_id: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Entity).order_by(Entity.updated_at.desc())
    if world_id:
        stmt = stmt.where(Entity.world_id == world_id)
    if type:
        stmt = stmt.where(Entity.entity_type == type)
    if search:
        stmt = stmt.where(Entity.name.ilike(f"%{search}%"))
    if tag:
        stmt = stmt.where(Entity.tags.any(tag))
    if faction_id:
        stmt = stmt.where(Entity.faction_id == faction_id)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{entity_id}", response_model=EntityResponse)
async def get_entity(entity_id: str, db: AsyncSession = Depends(get_db)):
    entity = await db.get(Entity, entity_id)
    if not entity:
        raise HTTPException(404, "Entity not found")
    return entity


@router.post("", response_model=EntityResponse, status_code=201)
async def create_entity(data: EntityCreate, db: AsyncSession = Depends(get_db)):
    values = data.model_dump(by_alias=True)
    values["world_id"] = await resolve_world_id(db, values.get("world_id"))
    entity = Entity(**values)
    db.add(entity)
    await db.flush()
    await db.refresh(entity)
    return entity


@router.patch("/{entity_id}", response_model=EntityResponse)
async def update_entity(entity_id: str, data: EntityUpdate, db: AsyncSession = Depends(get_db)):
    entity = await db.get(Entity, entity_id)
    if not entity:
        raise HTTPException(404, "Entity not found")
    update = data.model_dump(exclude_unset=True, by_alias=True)
    if "world_id" in update:
        update["world_id"] = await resolve_world_id(db, update["world_id"])
    for key, val in update.items():
        setattr(entity, key, val)
    await db.flush()
    await db.refresh(entity)
    return entity


@router.delete("/{entity_id}", status_code=204)
async def delete_entity(entity_id: str, db: AsyncSession = Depends(get_db)):
    entity = await db.get(Entity, entity_id)
    if not entity:
        raise HTTPException(404, "Entity not found")
    await db.delete(entity)
