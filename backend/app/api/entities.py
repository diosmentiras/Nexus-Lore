"""Entity CRUD API"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import Entity
from app.schemas import EntityCreate, EntityResponse, EntityUpdate

router = APIRouter(prefix="/api/entities", tags=["Entities"])


@router.get("", response_model=list[EntityResponse])
async def list_entities(
    type: str | None = Query(None),
    search: str | None = Query(None),
    tag: str | None = Query(None),
    faction_id: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Entity).order_by(Entity.updated_at.desc())
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
    entity = Entity(**data.model_dump())
    db.add(entity)
    await db.flush()
    await db.refresh(entity)
    return entity


@router.patch("/{entity_id}", response_model=EntityResponse)
async def update_entity(entity_id: str, data: EntityUpdate, db: AsyncSession = Depends(get_db)):
    entity = await db.get(Entity, entity_id)
    if not entity:
        raise HTTPException(404, "Entity not found")
    for key, val in data.model_dump(exclude_unset=True).items():
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
