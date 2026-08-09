from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import World

DEFAULT_WORLD_SLUG = "default"


async def ensure_default_world(db: AsyncSession) -> World:
    result = await db.execute(select(World).where(World.slug == DEFAULT_WORLD_SLUG))
    world = result.scalar_one_or_none()
    if world:
        return world

    world = World(
        name="默认世界观",
        slug=DEFAULT_WORLD_SLUG,
        description="未指定归属时使用的默认设定集。",
    )
    db.add(world)
    await db.flush()
    await db.refresh(world)
    return world


async def resolve_world_id(db: AsyncSession, world_id: str | None) -> str:
    if world_id:
        return world_id
    world = await ensure_default_world(db)
    return str(world.id)
