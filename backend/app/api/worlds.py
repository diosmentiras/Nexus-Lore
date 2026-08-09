"""World set management API"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import World
from app.schemas import WorldCreate, WorldResponse, WorldUpdate
from app.services.world_service import ensure_default_world

router = APIRouter(prefix="/api/worlds", tags=["Worlds"])


@router.get("", response_model=list[WorldResponse])
async def list_worlds(db: AsyncSession = Depends(get_db)):
    await ensure_default_world(db)
    result = await db.execute(select(World))
    worlds = list(result.scalars().all())
    worlds.sort(
        key=lambda world: (
            int((world.meta or {}).get("available_article_count", 0)),
            int((world.meta or {}).get("article_count", 0)),
            world.name,
        ),
        reverse=True,
    )
    return worlds


@router.get("/{world_id}", response_model=WorldResponse)
async def get_world(world_id: str, db: AsyncSession = Depends(get_db)):
    world = await db.get(World, world_id)
    if not world:
        raise HTTPException(404, "World not found")
    return world


@router.post("", response_model=WorldResponse, status_code=201)
async def create_world(data: WorldCreate, db: AsyncSession = Depends(get_db)):
    existing = (await db.execute(select(World).where(World.slug == data.slug))).scalar_one_or_none()
    if existing:
        raise HTTPException(409, "World slug already exists")
    world = World(**data.model_dump(by_alias=True))
    db.add(world)
    await db.flush()
    await db.refresh(world)
    return world


@router.patch("/{world_id}", response_model=WorldResponse)
async def update_world(world_id: str, data: WorldUpdate, db: AsyncSession = Depends(get_db)):
    world = await db.get(World, world_id)
    if not world:
        raise HTTPException(404, "World not found")

    update = data.model_dump(exclude_unset=True, by_alias=True)
    if "slug" in update:
        existing = (await db.execute(select(World).where(World.slug == update["slug"], World.id != world_id))).scalar_one_or_none()
        if existing:
            raise HTTPException(409, "World slug already exists")

    for key, val in update.items():
        setattr(world, key, val)
    await db.flush()
    await db.refresh(world)
    return world


@router.delete("/{world_id}", status_code=204)
async def delete_world(world_id: str, db: AsyncSession = Depends(get_db)):
    world = await db.get(World, world_id)
    if not world:
        raise HTTPException(404, "World not found")
    if world.slug == "default":
        raise HTTPException(400, "Default world cannot be deleted")
    await db.delete(world)
