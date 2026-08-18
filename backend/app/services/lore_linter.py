"""Deterministic consistency checks for a single lore world."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Any, Iterable


ENGINE_VERSION = "rules-v1"

_DEATH_PATTERN = re.compile(r"死亡|去世|牺牲|阵亡|殉职|被杀|遇害|处决|身亡|毙命")
_POSTHUMOUS_PATTERN = re.compile(r"回忆|档案|记录|录像|遗体|尸体|纪念|追悼|此前|过去|生前|梦境|幻象")
_UNKNOWN_DATES = {"", "unknown", "未知", "不详", "待定", "n/a", "none"}


@dataclass(slots=True)
class IssueCandidate:
    severity: str
    title: str
    description: str
    issue_type: str
    entity1_id: str | None = None
    entity2_id: str | None = None
    entity1_name: str | None = None
    entity2_name: str | None = None
    source_lore_id: str | None = None
    meta: dict[str, Any] = field(default_factory=dict)


def normalize_entity_name(value: str) -> str:
    """Normalize names enough to catch accidental duplicates without fuzzy guessing."""
    normalized = unicodedata.normalize("NFKC", value or "").casefold()
    return re.sub(r"[\W_]+", "", normalized, flags=re.UNICODE)


def parse_temporal_order(value: str | None) -> int | None:
    """Convert common year/date labels to a sortable integer."""
    if not value:
        return None
    normalized = unicodedata.normalize("NFKC", value).strip().lower()
    if normalized in _UNKNOWN_DATES:
        return None

    century = re.search(r"(公元前)?\s*(\d{1,3})\s*世纪", normalized)
    if century:
        year = (int(century.group(2)) - 1) * 100
        return -year if century.group(1) else year

    year = re.search(r"(公元前|前)?\s*(-?\d{1,6})\s*(?:年|[-/.]|$)", normalized)
    if not year:
        return None
    result = int(year.group(2))
    if year.group(1) and result > 0:
        result = -result
    return result


def _id(value: Any) -> str | None:
    return str(value) if value is not None else None


def _event_order(event: Any) -> int | None:
    explicit = getattr(event, "date_order", 0) or 0
    if explicit:
        return int(explicit)
    return parse_temporal_order(getattr(event, "date", None))


def build_lint_candidates(
    world_id: str,
    entities: Iterable[Any],
    relations: Iterable[Any],
    events: Iterable[Any],
) -> list[IssueCandidate]:
    """Run structural and timeline rules against already-loaded ORM objects."""
    entity_list = list(entities)
    relation_list = list(relations)
    event_list = list(events)
    entity_map = {_id(entity.id): entity for entity in entity_list}
    issues: list[IssueCandidate] = []

    duplicate_groups: dict[str, list[Any]] = {}
    for entity in entity_list:
        key = normalize_entity_name(entity.name)
        if key:
            duplicate_groups.setdefault(key, []).append(entity)
    for group in duplicate_groups.values():
        if len(group) < 2:
            continue
        canonical = group[0]
        for duplicate in group[1:]:
            issues.append(
                IssueCandidate(
                    severity="warning",
                    title="疑似重复实体",
                    description=f"“{canonical.name}”与“{duplicate.name}”规范化后的名称相同，建议合并或补充区分信息。",
                    issue_type="duplicate_entity",
                    entity1_id=_id(canonical.id),
                    entity2_id=_id(duplicate.id),
                    entity1_name=canonical.name,
                    entity2_name=duplicate.name,
                    source_lore_id=_id(duplicate.id),
                )
            )

    for entity in entity_list:
        faction_id = _id(getattr(entity, "faction_id", None))
        if not faction_id:
            continue
        faction = entity_map.get(faction_id)
        if not faction:
            issues.append(
                IssueCandidate(
                    severity="error",
                    title="实体引用了不存在的势力",
                    description=f"“{entity.name}”的 faction_id 无法在当前世界中找到。",
                    issue_type="dangling_faction",
                    entity1_id=_id(entity.id),
                    entity1_name=entity.name,
                    source_lore_id=_id(entity.id),
                )
            )
        elif faction.entity_type != "faction":
            issues.append(
                IssueCandidate(
                    severity="warning",
                    title="势力字段指向了非势力实体",
                    description=f"“{entity.name}”将“{faction.name}”设为所属势力，但目标类型是 {faction.entity_type}。",
                    issue_type="invalid_faction_type",
                    entity1_id=_id(entity.id),
                    entity2_id=_id(faction.id),
                    entity1_name=entity.name,
                    entity2_name=faction.name,
                    source_lore_id=_id(entity.id),
                )
            )

    for relation in relation_list:
        source_id = _id(relation.source_id)
        target_id = _id(relation.target_id)
        source = entity_map.get(source_id)
        target = entity_map.get(target_id)
        if not source or not target:
            missing = "源实体" if not source else "目标实体"
            issues.append(
                IssueCandidate(
                    severity="error",
                    title="关系包含失效引用",
                    description=f"关系“{getattr(relation, 'label', None) or relation.relation_type}”的{missing}不存在。",
                    issue_type="dangling_relation",
                    entity1_id=source_id if source else target_id,
                    entity1_name=source.name if source else (target.name if target else None),
                    source_lore_id=source_id if source else target_id,
                    meta={"relation_id": _id(relation.id)},
                )
            )
            continue
        if source_id == target_id:
            issues.append(
                IssueCandidate(
                    severity="warning",
                    title="实体与自身建立了关系",
                    description=f"“{source.name}”存在一条指向自身的 {relation.relation_type} 关系。",
                    issue_type="self_relation",
                    entity1_id=source_id,
                    entity1_name=source.name,
                    source_lore_id=source_id,
                    meta={"relation_id": _id(relation.id)},
                )
            )

        source_world = _id(getattr(source, "world_id", None))
        target_world = _id(getattr(target, "world_id", None))
        if source_world != world_id or target_world != world_id:
            issues.append(
                IssueCandidate(
                    severity="error",
                    title="关系跨越了世界边界",
                    description=f"“{source.name}”与“{target.name}”不属于同一世界，关系数据需要重新归档。",
                    issue_type="cross_world_relation",
                    entity1_id=source_id,
                    entity2_id=target_id,
                    entity1_name=source.name,
                    entity2_name=target.name,
                    source_lore_id=source_id,
                    meta={"relation_id": _id(relation.id)},
                )
            )

        start = parse_temporal_order(getattr(relation, "date_start", None))
        end = parse_temporal_order(getattr(relation, "date_end", None))
        if start is not None and end is not None and start > end:
            issues.append(
                IssueCandidate(
                    severity="warning",
                    title="关系时间范围倒置",
                    description=f"“{source.name}”与“{target.name}”的关系开始时间晚于结束时间。",
                    issue_type="relation_date_order",
                    entity1_id=source_id,
                    entity2_id=target_id,
                    entity1_name=source.name,
                    entity2_name=target.name,
                    source_lore_id=source_id,
                    meta={"relation_id": _id(relation.id), "date_start": relation.date_start, "date_end": relation.date_end},
                )
            )

    events_by_entity: dict[str, list[Any]] = {}
    for event in event_list:
        for entity_id in dict.fromkeys(str(item) for item in (getattr(event, "entity_ids", None) or [])):
            entity = entity_map.get(entity_id)
            if not entity:
                issues.append(
                    IssueCandidate(
                        severity="warning",
                        title="事件引用了不存在的实体",
                        description=f"事件“{event.title}”引用了已删除或属于其他世界的实体 {entity_id}。",
                        issue_type="dangling_event_reference",
                        meta={"event_id": _id(event.id), "event_title": event.title, "missing_entity_id": entity_id},
                    )
                )
                continue
            events_by_entity.setdefault(entity_id, []).append(event)

    for entity_id, entity_events in events_by_entity.items():
        ordered = sorted(
            ((order, event) for event in entity_events if (order := _event_order(event)) is not None),
            key=lambda item: item[0],
        )
        death_events = [
            (order, event)
            for order, event in ordered
            if _DEATH_PATTERN.search(" ".join([event.title or "", event.description or "", " ".join(event.tags or [])]))
        ]
        if not death_events:
            continue
        death_order, death_event = death_events[0]
        later = next(
            (
                event
                for order, event in ordered
                if order > death_order
                and event.id != death_event.id
                and not _POSTHUMOUS_PATTERN.search(" ".join([event.title or "", event.description or "", " ".join(event.tags or [])]))
            ),
            None,
        )
        if not later:
            continue
        entity = entity_map[entity_id]
        issues.append(
            IssueCandidate(
                severity="error",
                title="角色在死亡事件后继续行动",
                description=f"“{entity.name}”在“{death_event.title}”后仍出现在“{later.title}”中，请核对时间、复活设定或回忆语境。",
                issue_type="post_death_appearance",
                entity1_id=entity_id,
                entity1_name=entity.name,
                source_lore_id=entity_id,
                meta={
                    "death_event_id": _id(death_event.id),
                    "death_event_title": death_event.title,
                    "later_event_id": _id(later.id),
                    "later_event_title": later.title,
                },
            )
        )

    return issues
