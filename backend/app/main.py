"""FastAPI 应用入口"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import entities, events, extract, linter, misc, relations
from app.config import settings
from app.db.session import engine
from app.models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期 — 启动时创建数据库表"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


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
app.include_router(entities.router)
app.include_router(relations.router)
app.include_router(events.router)
app.include_router(linter.router)
app.include_router(extract.router)
app.include_router(misc.router)


@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.app_name}
