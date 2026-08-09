from __future__ import annotations

import os
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, TypeDecorator, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY, JSONB as PG_JSONB, UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


# ---- Polyfill types (PG JSONB/ARRAY ↔ SQLite Text) ---- #

class JSONType(TypeDecorator):
    impl = String
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_JSONB())
        return dialect.type_descriptor(Text())

    def process_bind_param(self, value, dialect):
        if dialect.name != "postgresql" and value is not None:
            import json
            return json.dumps(value, ensure_ascii=False)
        return value

    def process_result_value(self, value, dialect):
        if dialect.name != "postgresql" and value is not None:
            import json
            return json.loads(value)
        return value or {}


class ArrayType(TypeDecorator):
    impl = String
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_ARRAY(String()))
        return dialect.type_descriptor(Text())

    def process_bind_param(self, value, dialect):
        if dialect.name != "postgresql" and value is not None:
            import json
            return json.dumps(list(value), ensure_ascii=False)
        return value

    def process_result_value(self, value, dialect):
        if dialect.name != "postgresql" and value is not None:
            import json
            return json.loads(value)
        return value or []


def _is_pg() -> bool:
    return (os.environ.get("DATABASE_URL") or "").startswith("postgresql")


def _uuid_col():
    if _is_pg():
        return PG_UUID(as_uuid=True)
    return String(36)


def _gen_id():
    if _is_pg():
        return uuid.uuid4()
    return str(uuid.uuid4())


# ---- Base ---- #

class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


# ---- Models ---- #

class World(Base, TimestampMixin):
    __tablename__ = "worlds"

    id: Mapped[str] = mapped_column(_uuid_col(), primary_key=True, default=_gen_id)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    meta: Mapped[dict[str, Any]] = mapped_column(JSONType(), default=dict, nullable=False)


class SourceDocument(Base, TimestampMixin):
    __tablename__ = "source_documents"
    __table_args__ = (
        UniqueConstraint("world_id", "url", name="uq_source_documents_world_url"),
        Index("ix_source_documents_world_status_id", "world_id", "status", "id"),
        Index("ix_source_documents_world_updated_id", "world_id", "updated_at", "id"),
    )

    id: Mapped[str] = mapped_column(_uuid_col(), primary_key=True, default=_gen_id)
    world_id: Mapped[str] = mapped_column(_uuid_col(), ForeignKey("worlds.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_site: Mapped[str | None] = mapped_column(String(120), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="imported", index=True)
    analysis_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    meta: Mapped[dict[str, Any]] = mapped_column(JSONType(), default=dict, nullable=False)

    world: Mapped[World] = relationship("World")

class Entity(Base, TimestampMixin):
    __tablename__ = "entities"
    __table_args__ = (Index("ix_entities_world_type_id", "world_id", "entity_type", "id"),)

    id: Mapped[str] = mapped_column(_uuid_col(), primary_key=True, default=_gen_id)
    world_id: Mapped[str | None] = mapped_column(_uuid_col(), ForeignKey("worlds.id", ondelete="CASCADE"), nullable=True, index=True)
    source_document_id: Mapped[str | None] = mapped_column(_uuid_col(), ForeignKey("source_documents.id", ondelete="SET NULL"), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    faction_id: Mapped[str | None] = mapped_column(_uuid_col(), ForeignKey("entities.id"), nullable=True, index=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    background: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[list[str]] = mapped_column(ArrayType(), default=list, nullable=False)
    meta: Mapped[dict[str, Any]] = mapped_column(JSONType(), default=dict, nullable=False)
    date: Mapped[str | None] = mapped_column(String(50), nullable=True)
    date_context: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    extracted_by_ai: Mapped[bool] = mapped_column(default=False)

    world: Mapped[World | None] = relationship("World")
    source_document: Mapped[SourceDocument | None] = relationship("SourceDocument")
    faction: Mapped[Entity | None] = relationship("Entity", remote_side="Entity.id", foreign_keys=[faction_id])


class Relation(Base, TimestampMixin):
    __tablename__ = "relations"

    id: Mapped[str] = mapped_column(_uuid_col(), primary_key=True, default=_gen_id)
    world_id: Mapped[str | None] = mapped_column(_uuid_col(), ForeignKey("worlds.id", ondelete="CASCADE"), nullable=True, index=True)
    source_document_id: Mapped[str | None] = mapped_column(_uuid_col(), ForeignKey("source_documents.id", ondelete="SET NULL"), nullable=True, index=True)
    source_id: Mapped[str] = mapped_column(_uuid_col(), ForeignKey("entities.id", ondelete="CASCADE"), nullable=False, index=True)
    target_id: Mapped[str] = mapped_column(_uuid_col(), ForeignKey("entities.id", ondelete="CASCADE"), nullable=False, index=True)
    relation_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    label: Mapped[str | None] = mapped_column(String(255), nullable=True)
    date_start: Mapped[str | None] = mapped_column(String(50), nullable=True)
    date_end: Mapped[str | None] = mapped_column(String(50), nullable=True)
    meta: Mapped[dict[str, Any]] = mapped_column(JSONType(), default=dict, nullable=False)

    world: Mapped[World | None] = relationship("World")
    source_document: Mapped[SourceDocument | None] = relationship("SourceDocument")
    source: Mapped[Entity] = relationship("Entity", foreign_keys=[source_id])
    target: Mapped[Entity] = relationship("Entity", foreign_keys=[target_id])


class Event(Base, TimestampMixin):
    __tablename__ = "events"

    id: Mapped[str] = mapped_column(_uuid_col(), primary_key=True, default=_gen_id)
    world_id: Mapped[str | None] = mapped_column(_uuid_col(), ForeignKey("worlds.id", ondelete="CASCADE"), nullable=True, index=True)
    source_document_id: Mapped[str | None] = mapped_column(_uuid_col(), ForeignKey("source_documents.id", ondelete="SET NULL"), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    date: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    date_context: Mapped[str | None] = mapped_column(Text, nullable=True)
    date_order: Mapped[int] = mapped_column(default=0)
    entity_ids: Mapped[list[str]] = mapped_column(ArrayType(), default=list, nullable=False)
    tags: Mapped[list[str]] = mapped_column(ArrayType(), default=list, nullable=False)
    meta: Mapped[dict[str, Any]] = mapped_column(JSONType(), default=dict, nullable=False)
    source_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    extracted_by_ai: Mapped[bool] = mapped_column(default=False)

    world: Mapped[World | None] = relationship("World")
    source_document: Mapped[SourceDocument | None] = relationship("SourceDocument")


class LintIssue(Base, TimestampMixin):
    __tablename__ = "lint_issues"

    id: Mapped[str] = mapped_column(_uuid_col(), primary_key=True, default=_gen_id)
    world_id: Mapped[str | None] = mapped_column(_uuid_col(), ForeignKey("worlds.id", ondelete="CASCADE"), nullable=True, index=True)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default="warning")
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    entity1_id: Mapped[str | None] = mapped_column(_uuid_col(), ForeignKey("entities.id"), nullable=True)
    entity2_id: Mapped[str | None] = mapped_column(_uuid_col(), ForeignKey("entities.id"), nullable=True)
    entity1_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    entity2_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    issue_type: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    source_lore_id: Mapped[str | None] = mapped_column(_uuid_col(), ForeignKey("entities.id"), nullable=True)
    resolved: Mapped[bool] = mapped_column(default=False)
    meta: Mapped[dict[str, Any]] = mapped_column(JSONType(), default=dict, nullable=False)
