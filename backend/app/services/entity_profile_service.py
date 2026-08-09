"""Build readable entity dossiers from imported story documents."""

from __future__ import annotations

import re
from typing import Any, Iterable


TYPE_LABELS = {
    "character": "人物",
    "faction": "组织或势力",
    "item": "物品",
    "location": "地点",
    "event": "事件",
    "containment": "异常",
}

GENERIC_ADAPTATIONS = {
    "基本上没变",
    "基本完全没变",
    "几乎完全相同",
    "基本上是他自己",
    "largely unchanged",
    "largely the same",
}


def _clean(value: Any) -> str:
    return " ".join(str(value or "").replace("\xa0", " ").split()).strip(" :\n\t")


def _story_document_ids(entity: Any) -> set[str]:
    meta = entity.meta if isinstance(entity.meta, dict) else {}
    return {
        str(story["document_id"])
        for story in meta.get("stories", [])
        if isinstance(story, dict) and story.get("document_id")
    }


def _aliases(entity: Any) -> list[str]:
    meta = entity.meta if isinstance(entity.meta, dict) else {}
    candidates = [entity.name, meta.get("adaptation"), meta.get("canonical_name")]
    aliases: list[str] = []
    for candidate in candidates:
        alias = _clean(candidate).strip(".,。\"'")
        if len(alias) < 3 or alias.casefold() in GENERIC_ADAPTATIONS:
            continue
        if alias.casefold() not in {item.casefold() for item in aliases}:
            aliases.append(alias)
    return aliases


def _document_evidence(document: Any, aliases: list[str], limit: int = 2) -> list[dict[str, str]]:
    if getattr(document, "status", None) == "missing":
        return []
    lines = [_clean(line) for line in str(getattr(document, "content", "") or "").splitlines()]
    lines = [line for line in lines if line]
    evidence: list[dict[str, str]] = []
    seen: set[str] = set()

    for index, line in enumerate(lines):
        matched = next((alias for alias in aliases if alias.casefold() in line.casefold()), None)
        if not matched:
            continue
        excerpt = "\n".join(lines[max(0, index - 1): min(len(lines), index + 2)])
        if len(excerpt) > 420:
            excerpt = excerpt[:417].rstrip() + "..."
        fingerprint = re.sub(r"\s+", "", excerpt).casefold()
        if fingerprint in seen:
            continue
        seen.add(fingerprint)
        evidence.append(
            {
                "document_id": str(document.id),
                "title": document.title,
                "url": document.url,
                "matched_alias": matched,
                "excerpt": excerpt,
            }
        )
        if len(evidence) >= limit:
            break
    return evidence


def build_entity_profile(
    entity: Any,
    documents_by_id: dict[str, Any],
    all_entities: Iterable[Any],
) -> tuple[str, str, dict[str, Any]]:
    meta = entity.meta if isinstance(entity.meta, dict) else {}
    canonical = _clean(meta.get("canonical_name")) or entity.name
    adaptation = _clean(meta.get("adaptation"))
    stories = [story for story in meta.get("stories", []) if isinstance(story, dict)]
    story_titles = [_clean(story.get("title")) for story in stories if _clean(story.get("title"))]
    document_ids = _story_document_ids(entity)
    documents = [documents_by_id[document_id] for document_id in document_ids if document_id in documents_by_id]
    kind = TYPE_LABELS.get(entity.entity_type, entity.entity_type)

    subject = {
        "character": "该角色",
        "faction": "该组织",
        "item": "该物品",
        "location": "该地点",
        "event": "该事件",
        "containment": "该异常",
    }.get(entity.entity_type, "该设定")

    if adaptation and adaptation.casefold() not in GENERIC_ADAPTATIONS and adaptation.casefold() != entity.name.casefold():
        adaptation_sentence = f"在西部改写中，{subject}被重新设定为“{adaptation.rstrip('。.')}”。"
    elif canonical.casefold() != entity.name.casefold():
        adaptation_sentence = f"该版本基本保留原型的核心身份，并以“{entity.name}”进入西部叙事。"
    else:
        adaptation_sentence = "设定中心将其视为原型在这条西部时间线中的直接对应物。"

    title_preview = "、".join(f"《{title}》" for title in story_titles[:3])
    if len(story_titles) > 3:
        title_preview += f"等 {len(story_titles)} 篇故事"
    elif story_titles:
        title_preview += f"共 {len(story_titles)} 篇故事"

    aliases = _aliases(entity)
    evidence: list[dict[str, str]] = []
    dates: list[str] = []
    for document in documents:
        evidence.extend(_document_evidence(document, aliases))
        document_meta = document.meta if isinstance(document.meta, dict) else {}
        for marker in document_meta.get("date_markers", []):
            marker_text = _clean(marker)
            if marker_text and marker_text not in dates:
                dates.append(marker_text)
    evidence = evidence[:8]
    dates = dates[:12]

    co_entities: list[dict[str, Any]] = []
    for other in all_entities:
        if str(other.id) == str(entity.id):
            continue
        shared_ids = document_ids & _story_document_ids(other)
        if not shared_ids:
            continue
        shared_titles = [
            documents_by_id[document_id].title
            for document_id in shared_ids
            if document_id in documents_by_id
        ]
        co_entities.append(
            {
                "id": str(other.id),
                "name": other.name,
                "entity_type": other.entity_type,
                "shared_story_count": len(shared_ids),
                "shared_story_titles": shared_titles,
            }
        )
    co_entities.sort(key=lambda item: (-item["shared_story_count"], item["name"]))
    co_entities = co_entities[:16]

    summary_parts = [
        f"{entity.name}是“死者手牌”世界中的{kind}设定，对应 SCP 体系中的“{canonical}”。",
        adaptation_sentence,
    ]
    if title_preview:
        summary_parts.append(f"设定中心将其关联到{title_preview}。")
    summary = "".join(summary_parts)

    scope_detail = (
        f"已归档 {len(story_titles)} 篇承载故事，其中 {sum(document.status != 'missing' for document in documents)} 篇正文可读取。"
        if story_titles
        else "设定中心未为该条目标注独立承载故事。"
    )
    evidence_detail = (
        f"在已读取正文中定位到 {len(evidence)} 组直接文本依据；这些片段用于核对身份、行动与叙事语境。"
        if evidence
        else "当前正文库尚未定位到同名直接提及；条目身份主要依据设定中心映射，不能据此推断未写明的经历。"
    )
    association_detail = (
        f"同篇故事还连接到 {len(co_entities)} 个已建档设定，可用于追踪人物、组织与地点之间的叙事联系。"
        if co_entities
        else "目前没有从共同承载文章中识别出其他已建档设定。"
    )
    background = "\n\n".join(
        [
            f"身份与改写：{adaptation_sentence}",
            f"叙事范围：{scope_detail}",
            f"资料依据：{evidence_detail}{association_detail}",
        ]
    )

    profile = {
        "version": 1,
        "kind_label": kind,
        "overview": summary,
        "adaptation_note": adaptation_sentence,
        "story_count": len(story_titles),
        "available_story_count": sum(document.status != "missing" for document in documents),
        "evidence": evidence,
        "co_entities": co_entities,
        "date_markers": dates,
        "source_note": "内容由设定中心映射与本地归档正文交叉整理；正文未明确说明之处不作推断。",
    }
    return summary, background, profile
