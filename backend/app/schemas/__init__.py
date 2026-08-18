from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# ===================== World =====================

class WorldBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=120, pattern=r"^[a-z0-9][a-z0-9-]*$")
    description: str | None = None
    source_url: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict, alias="meta")


class WorldCreate(WorldBase):
    pass


class WorldUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    slug: str | None = Field(default=None, min_length=1, max_length=120, pattern=r"^[a-z0-9][a-z0-9-]*$")
    description: str | None = None
    source_url: str | None = None
    metadata: dict[str, Any] | None = Field(default=None, alias="meta")


class WorldResponse(WorldBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}


# ===================== Source Document =====================

class SourceDocumentBase(BaseModel):
    world_id: str
    title: str = Field(..., min_length=1, max_length=255)
    url: str | None = None
    source_site: str | None = None
    content: str = Field(..., min_length=1)
    status: str = "imported"
    analysis_summary: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict, alias="meta")


class SourceDocumentCreate(SourceDocumentBase):
    pass


class SourceDocumentUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    url: str | None = None
    source_site: str | None = None
    content: str | None = Field(default=None, min_length=1)
    status: str | None = None
    analysis_summary: str | None = None
    metadata: dict[str, Any] | None = Field(default=None, alias="meta")


class SourceDocumentResponse(SourceDocumentBase):
    id: str
    content_hash: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}


class SourceDocumentCatalogItem(BaseModel):
    id: str
    world_id: str
    title: str
    url: str | None = None
    source_site: str | None = None
    status: str
    analysis_summary: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict, alias="meta")
    updated_at: datetime

    model_config = {"populate_by_name": True}


class SourceDocumentCatalog(BaseModel):
    items: list[SourceDocumentCatalogItem]
    total: int
    page: int
    page_size: int
    status_counts: dict[str, int] = Field(default_factory=dict)


# ===================== Entity =====================

class EntityBase(BaseModel):
    world_id: str | None = None
    source_document_id: str | None = None
    name: str = Field(..., min_length=1, max_length=255)
    entity_type: str = Field(..., pattern=r"^(character|faction|item|location|event|containment|world)$")
    faction_id: str | None = None
    summary: str | None = None
    background: str | None = None
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict, alias="meta")
    date: str | None = None
    date_context: str | None = None


class EntityCreate(EntityBase):
    source_text: str | None = None


class EntityUpdate(BaseModel):
    world_id: str | None = None
    source_document_id: str | None = None
    name: str | None = None
    entity_type: str | None = None
    faction_id: str | None = None
    summary: str | None = None
    background: str | None = None
    tags: list[str] | None = None
    metadata: dict[str, Any] | None = Field(default=None, alias="meta")
    date: str | None = None
    date_context: str | None = None


class EntityResponse(EntityBase):
    id: str
    created_at: datetime
    updated_at: datetime
    extracted_by_ai: bool

    model_config = {"from_attributes": True, "populate_by_name": True}


# ===================== Relation =====================

class RelationBase(BaseModel):
    world_id: str | None = None
    source_document_id: str | None = None
    source_id: str
    target_id: str
    relation_type: str = Field(..., pattern=r"^(ally|hostile|neutral|member|owns|located_at|other)$")
    label: str | None = None
    date_start: str | None = None
    date_end: str | None = None


class RelationCreate(RelationBase):
    pass


class RelationResponse(RelationBase):
    id: str
    created_at: datetime
    updated_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict, alias="meta")

    model_config = {"from_attributes": True, "populate_by_name": True}


# ===================== Event =====================

class EventBase(BaseModel):
    world_id: str | None = None
    source_document_id: str | None = None
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    date: str = Field(..., max_length=50)
    date_context: str | None = None
    entity_ids: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class EventCreate(EventBase):
    source_text: str | None = None


class EventUpdate(BaseModel):
    world_id: str | None = None
    source_document_id: str | None = None
    title: str | None = None
    description: str | None = None
    date: str | None = None
    date_context: str | None = None
    entity_ids: list[str] | None = None
    tags: list[str] | None = None


class EventResponse(EventBase):
    id: str
    created_at: datetime
    updated_at: datetime
    date_order: int
    extracted_by_ai: bool
    metadata: dict[str, Any] = Field(default_factory=dict, alias="meta")

    model_config = {"from_attributes": True, "populate_by_name": True}


# ===================== Lint Issue =====================

class LintIssueBase(BaseModel):
    world_id: str | None = None
    severity: str = Field(default="warning", pattern=r"^(error|warning|info)$")
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    entity1_id: str | None = None
    entity2_id: str | None = None
    entity1_name: str | None = None
    entity2_name: str | None = None
    issue_type: str | None = None
    source_lore_id: str | None = None


class LintIssueResponse(LintIssueBase):
    id: str
    resolved: bool
    created_at: datetime
    updated_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict, alias="meta")

    model_config = {"from_attributes": True, "populate_by_name": True}


class LintIssueUpdate(BaseModel):
    resolved: bool


# ===================== AI Extract =====================

class AiExtractRequest(BaseModel):
    text: str = Field(..., min_length=1)
    world_id: str | None = None
    source_document_id: str | None = None
    types: list[str] = Field(default_factory=lambda: ["character", "faction", "item", "event"])
    provider: str | None = None


class AiExtractEntity(BaseModel):
    name: str
    entity_type: str
    summary: str | None = None
    faction: str | None = None
    tags: list[str] = Field(default_factory=list)
    relations: list[tuple[str, str, str | None]] = Field(default_factory=list)


class AiExtractResponse(BaseModel):
    entities: list[AiExtractEntity]
    events: list[dict[str, Any]] = Field(default_factory=list)


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
    summary: str | None = None
    tags: list[str] = Field(default_factory=list)
    url: str | None = None
    status: str | None = None
    canonical_name: str | None = None


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


class DashboardWorldSummary(BaseModel):
    id: str
    name: str
    slug: str
    description: str | None = None
    source_url: str | None = None
    document_count: int = 0
    available_document_count: int = 0
    entity_count: int = 0
    event_count: int = 0
    dossier_id: str | None = None


class DashboardOverview(BaseModel):
    worlds: int = 0
    documents: int = 0
    available_documents: int = 0
    missing_documents: int = 0
    lore: int = 0
    relations: int = 0
    events: int = 0
    issues: int = 0
    world_summaries: list[DashboardWorldSummary] = Field(default_factory=list)
