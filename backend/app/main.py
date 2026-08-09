"""FastAPI 应用入口"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import documents, entities, events, extract, linter, misc, relations, worlds
from app.config import settings
from app.db.session import async_session, engine
from app.models import Base, Entity, SourceDocument
from app.services.world_service import ensure_default_world


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期 — 启动时创建数据库表"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(_ensure_covering_indexes)
    async with async_session() as session:
        await ensure_default_world(session)
        await session.commit()
    yield
    await engine.dispose()


def _ensure_covering_indexes(connection):
    """Add performance indexes to databases created by earlier releases."""
    for table in (SourceDocument.__table__, Entity.__table__):
        for index in table.indexes:
            index.create(connection, checkfirst=True)


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — 允许前端跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(worlds.router)
app.include_router(documents.router)
app.include_router(entities.router)
app.include_router(relations.router)
app.include_router(events.router)
app.include_router(linter.router)
app.include_router(extract.router)
app.include_router(misc.router)


@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.app_name}
