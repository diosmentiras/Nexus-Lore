from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class Entity(Base, TimestampMixin):
    __tablename__ = "entities"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    faction_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("entities.id"), nullable=True, index=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    background: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    meta: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    date: Mapped[str | None] = mapped_column(String(50), nullable=True)
    date_context: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    extracted_by_ai: Mapped[bool] = mapped_column(default=False)

    # 关系
    faction: Mapped[Entity | None] = relationship("Entity", remote_side="Entity.id", foreign_keys=[faction_id])


class Relation(Base, TimestampMixin):
    __tablename__ = "relations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("entities.id", ondelete="CASCADE"), nullable=False, index=True)
    target_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("entities.id", ondelete="CASCADE"), nullable=False, index=True)
    relation_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    label: Mapped[str | None] = mapped_column(String(255), nullable=True)
    date_start: Mapped[str | None] = mapped_column(String(50), nullable=True)
    date_end: Mapped[str | None] = mapped_column(String(50), nullable=True)
    meta: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)

    source: Mapped[Entity] = relationship("Entity", foreign_keys=[source_id])
    target: Mapped[Entity] = relationship("Entity", foreign_keys=[target_id])


class Event(Base, TimestampMixin):
    __tablename__ = "events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    date: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    date_context: Mapped[str | None] = mapped_column(Text, nullable=True)
    date_order: Mapped[int] = mapped_column(default=0)
    entity_ids: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    meta: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    source_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    extracted_by_ai: Mapped[bool] = mapped_column(default=False)


class LintIssue(Base, TimestampMixin):
    __tablename__ = "lint_issues"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default="warning")
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    entity1_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("entities.id"), nullable=True)
    entity2_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("entities.id"), nullable=True)
    entity1_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    entity2_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    issue_type: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    source_lore_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("entities.id"), nullable=True)
    resolved: Mapped[bool] = mapped_column(default=False)
    meta: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
