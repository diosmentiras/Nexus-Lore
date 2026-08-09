#!/usr/bin/env python3
"""Enrich imported Aces and Eights entities with document-backed dossiers."""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

from sqlalchemy import select


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))
os.environ.setdefault("DATABASE_URL", f"sqlite+aiosqlite:///{BACKEND_ROOT / 'data/dev.db'}")

from app.db.session import async_session, engine
from app.models import Entity, SourceDocument, World
from app.services.entity_profile_service import build_entity_profile


async def main() -> None:
    async with async_session() as db:
        world = (
            await db.execute(select(World).where(World.slug == "aces-and-eights"))
        ).scalar_one_or_none()
        if world is None:
            raise RuntimeError("aces-and-eights world not found")

        entities = (
            await db.execute(select(Entity).where(Entity.world_id == world.id))
        ).scalars().all()
        documents = (
            await db.execute(select(SourceDocument).where(SourceDocument.world_id == world.id))
        ).scalars().all()
        documents_by_id = {str(document.id): document for document in documents}

        evidence_count = 0
        for entity in entities:
            summary, background, profile = build_entity_profile(entity, documents_by_id, entities)
            entity.summary = summary
            entity.background = background
            entity.meta = {**entity.meta, "profile": profile}
            evidence_count += len(profile["evidence"])

        await db.commit()
        print(f"entities_enriched: {len(entities)}")
        print(f"evidence_snippets: {evidence_count}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
