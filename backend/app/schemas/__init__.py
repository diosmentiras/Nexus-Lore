from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# ===================== Entity =====================

class EntityBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    entity_type: str = Field(..., pattern=r"^(character|faction|item|location|event|containment)$")
    faction_id: uuid.UUID | None = None
    summary: str | None = None
    background: str | None = None
    tags: list[str] = []
    metadata: dict[str, Any] = Field(default={}, alias="meta")
    date: str | None = None
    date_context: str | None = None


class EntityCreate(EntityBase):
    source_text: str | None = None


class EntityUpdate(BaseModel):
    name: str | None = None
    entity_type: str | None = None
    faction_id: uuid.UUID | None = None
    summary: str | None = None
    background: str | None = None
    tags: list[str] | None = None
    metadata: dict[str, Any] | None = Field(default=None, alias="meta")
    date: str | None = None
    date_context: str | None = None


class EntityResponse(EntityBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    extracted_by_ai: bool

    model_config = {"from_attributes": True, "populate_by_name": True}


# ===================== Relation =====================

class RelationBase(BaseModel):
    source_id: uuid.UUID
    target_id: uuid.UUID
    relation_type: str = Field(..., pattern=r"^(ally|hostile|neutral|member|owns|located_at|other)$")
    label: str | None = None
    date_start: str | None = None
    date_end: str | None = None


class RelationCreate(RelationBase):
    pass


class RelationResponse(RelationBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    metadata: dict[str, Any] = Field(default={}, alias="meta")

    model_config = {"from_attributes": True, "populate_by_name": True}


# ===================== Event =====================

class EventBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    date: str = Field(..., max_length=50)
    date_context: str | None = None
    entity_ids: list[str] = []
    tags: list[str] = []


class EventCreate(EventBase):
    source_text: str | None = None


class EventUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    date: str | None = None
    date_context: str | None = None
    entity_ids: list[str] | None = None
    tags: list[str] | None = None


class EventResponse(EventBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    date_order: int
    extracted_by_ai: bool
    metadata: dict[str, Any] = Field(default={}, alias="meta")

    model_config = {"from_attributes": True, "populate_by_name": True}


# ===================== Lint Issue =====================

class LintIssueBase(BaseModel):
    severity: str = Field(default="warning", pattern=r"^(error|warning|info)$")
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    entity1_id: uuid.UUID | None = None
    entity2_id: uuid.UUID | None = None
    entity1_name: str | None = None
    entity2_name: str | None = None
    issue_type: str | None = None
    source_lore_id: uuid.UUID | None = None


class LintIssueResponse(LintIssueBase):
    id: uuid.UUID
    resolved: bool
    created_at: datetime
    updated_at: datetime
    metadata: dict[str, Any] = Field(default={}, alias="meta")

    model_config = {"from_attributes": True, "populate_by_name": True}


# ===================== AI Extract =====================

class AiExtractRequest(BaseModel):
    text: str = Field(..., min_length=1)
    types: list[str] = ["character", "faction", "item", "event"]
    provider: str | None = None


class AiExtractEntity(BaseModel):
    name: str
    entity_type: str
    summary: str | None = None
    faction: str | None = None
    tags: list[str] = []
    relations: list[tuple[str, str, str | None]] = []


class AiExtractResponse(BaseModel):
    entities: list[AiExtractEntity]
    events: list[dict[str, Any]] = []


# ===================== Lint Run =====================

class LintRunResponse(BaseModel):
    issues: list[LintIssueResponse]
    summary: dict[str, int]


# ===================== Nexus / Graph =====================

class GraphNode(BaseModel):
    id: str
    name: str
    entity_type: str
    color: str | None = None
    size: int = 8
    faction: str | None = None


class GraphLink(BaseModel):
    source: str
    target: str
    relation_type: str
    label: str | None = None
    color: str | None = None


class GraphResponse(BaseModel):
    nodes: list[GraphNode]
    links: list[GraphLink]


# ===================== Dashboard =====================

class DashboardStats(BaseModel):
    characters: int = 0
    factions: int = 0
    items: int = 0
    relations: int = 0
    events: int = 0
    issues: int = 0
