#!/usr/bin/env python3
"""Build evidence-backed Chronicle events from imported article date mentions."""

from __future__ import annotations

import argparse
import asyncio
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))
os.environ.setdefault("DATABASE_URL", f"sqlite+aiosqlite:///{BACKEND_ROOT / 'data/dev.db'}")
os.environ.setdefault("DEBUG", "false")

from sqlalchemy import delete, select

from app.db.session import async_session, engine
from app.models import Event, SourceDocument, World


IMPORTER = "chronicle-date-evidence-v1"
DATE_PATTERN = re.compile(
    r"(?<!\d)(?:1\d{3}|20\d{2}|21\d{2})"
    r"(?:年(?:\d{1,2}月(?:\d{1,2}日)?)?|[-/.](?:0?[1-9]|1[0-2])"
    r"(?:[-/.](?:0?[1-9]|[12]\d|3[01]))?)(?!\d)"
)
BOUNDARIES = "\n。！？!?；;"
EVENT_CUES = (
    "发生", "建立", "成立", "开始", "结束", "爆发", "战争", "事故", "事件",
    "行动", "死亡", "出生", "发现", "失踪", "袭击", "入侵", "摧毁", "启用",
    "关闭", "抵达", "离开", "签署", "宣布", "记录", "报告", "收容", "时间线",
)


@dataclass(frozen=True)
class Candidate:
    world_id: str
    document_id: str
    document_title: str
    date: str
    date_order: int
    context: str
    section: str
    entity_ids: tuple[str, ...]
    score: int

    @property
    def import_key(self) -> str:
        return f"{IMPORTER}:{self.document_id}:{self.date}"


def clean_text(value: Any) -> str:
    return " ".join(str(value or "").replace("\xa0", " ").split())


def normalize_date(marker: str) -> tuple[str, int]:
    numbers = [int(part) for part in re.findall(r"\d+", marker)]
    year = numbers[0]
    month = numbers[1] if len(numbers) > 1 else 0
    day = numbers[2] if len(numbers) > 2 else 0
    normalized = str(year)
    if month:
        normalized += f"-{month:02d}"
    if day:
        normalized += f"-{day:02d}"
    return normalized, year * 10000 + month * 100 + day


def sentence_context(content: str, start: int, end: int) -> str:
    left = max((content.rfind(boundary, 0, start) for boundary in BOUNDARIES), default=-1) + 1
    right_positions = [content.find(boundary, end) for boundary in BOUNDARIES]
    right_positions = [position for position in right_positions if position >= 0]
    right = min(right_positions) + 1 if right_positions else len(content)
    if right - left > 420:
        left = max(left, start - 150)
        right = min(right, end + 220)
    return clean_text(content[left:right])[:360]


def likely_identifier(content: str, start: int, end: int, context: str, marker: str) -> bool:
    year = marker[:4]
    escaped = re.escape(year)
    if re.search(rf"SCP(?:-CN)?\s*[-—－:]?\s*{escaped}(?!\d)", context, re.IGNORECASE):
        return True
    if re.search(rf"(?:编号|项目编号|档案编号|条目)\s*[-—－:#：]?\s*{escaped}(?!\d)", context):
        return True
    before = content[max(0, start - 24):start]
    after = content[end:end + 24]
    if re.match(r"\s*(?:公里|千米|米|厘米|毫米|km|m/s|公里/秒|米/秒|度|%|倍|赫兹|Hz)", after, re.IGNORECASE):
        return True
    if re.search(r"(?:日志|记录|文件|档案|编号|代号|实验|测试|附录|修订|版本|协议)\s*[-—－:#：]?\s*$", before):
        return True
    if re.match(r"\s*[-—－][A-Za-z]", after):
        return True
    if re.fullmatch(rf"[+\s#]*(?:(?:TL|timeline|时间线)\s*)?{re.escape(marker)}[+\s#]*", context, re.IGNORECASE):
        return True
    if marker.endswith("年") and re.match(r"\s*(?:前|后|来|间|内|以上|以下)", after):
        if int(year) < 1800 or re.search(r"(?:距今|大约|约|已有|长达|超过|过去|历经|持续)\s*$", before):
            return True
    if re.search(r"\d{1,4}\s*(?:至|到|—|－|-)\s*$", before) and not re.search(r"(?:公元|西元)\s*\d{1,4}\s*(?:至|到|—|－|-)", context):
        return True
    return False


def candidate_score(marker: str, context: str, section: str) -> int:
    score = 1
    if re.search(r"\d{1,2}(?:日|[-/.]\d{1,2})", marker):
        score += 3
    elif re.search(r"\d{1,2}月|[-/.]\d{1,2}", marker):
        score += 2
    if any(cue in context for cue in EVENT_CUES):
        score += 2
    if any(cue in section for cue in ("时间", "年表", "历史", "纪事", "timeline")):
        score += 3
    if 24 <= len(context) <= 260:
        score += 1
    return score


def extract_candidates(document: SourceDocument) -> list[Candidate]:
    metadata = document.meta if isinstance(document.meta, dict) else {}
    section = clean_text(metadata.get("catalog_section") or "来源文章")[:120]
    entity_ids = tuple(str(value) for value in metadata.get("mapped_entity_ids", [])[:24])
    candidates: dict[str, Candidate] = {}
    for match in DATE_PATTERN.finditer(document.content):
        marker = match.group(0)
        date, date_order = normalize_date(marker)
        context = sentence_context(document.content, match.start(), match.end())
        if len(context) < 12 or likely_identifier(document.content, match.start(), match.end(), context, marker):
            continue
        candidate = Candidate(
            world_id=str(document.world_id),
            document_id=str(document.id),
            document_title=document.title,
            date=date,
            date_order=date_order,
            context=context,
            section=section,
            entity_ids=entity_ids,
            score=candidate_score(marker, context, section),
        )
        current = candidates.get(date)
        if current is None or candidate.score > current.score:
            candidates[date] = candidate
    return list(candidates.values())


def evenly_spaced(items: list[Candidate], limit: int) -> list[Candidate]:
    if len(items) <= limit:
        return items
    return [items[(index * len(items)) // limit] for index in range(limit)]


def select_world_candidates(candidates: list[Candidate], limit: int) -> list[Candidate]:
    by_date: dict[str, list[Candidate]] = {}
    for candidate in candidates:
        by_date.setdefault(candidate.date, []).append(candidate)
    for group in by_date.values():
        group.sort(key=lambda item: (-item.score, item.document_title))

    primary = sorted((group[0] for group in by_date.values()), key=lambda item: (item.date_order, item.document_title))
    if len(primary) >= limit:
        return evenly_spaced(primary, limit)

    selected = list(primary)
    extras = sorted(
        (candidate for group in by_date.values() for candidate in group[1:3]),
        key=lambda item: (-item.score, item.date_order, item.document_title),
    )
    selected.extend(extras[: limit - len(selected)])
    return sorted(selected, key=lambda item: (item.date_order, item.document_title))


async def build(args: argparse.Namespace) -> dict[str, int]:
    async with async_session() as db:
        world_stmt = select(World).where(World.slug != "default")
        if args.only:
            world_stmt = world_stmt.where(World.slug.in_(args.only))
        worlds = (await db.execute(world_stmt)).scalars().all()

        created = 0
        updated = 0
        skipped_curated = 0
        populated_worlds = 0
        for world in worlds:
            existing = (
                await db.execute(select(Event).where(Event.world_id == world.id))
            ).scalars().all()
            curated = [event for event in existing if not (isinstance(event.meta, dict) and event.meta.get("importer") == IMPORTER)]
            if curated and not args.include_curated_worlds:
                skipped_curated += 1
                continue

            documents = (
                await db.execute(
                    select(SourceDocument).where(
                        SourceDocument.world_id == world.id,
                        SourceDocument.status != "missing",
                    )
                )
            ).scalars().all()
            candidates = select_world_candidates(
                [candidate for document in documents for candidate in extract_candidates(document)],
                args.max_events_per_world,
            )
            if not candidates:
                continue
            populated_worlds += 1
            events_by_key = {
                event.meta.get("import_key"): event
                for event in existing
                if isinstance(event.meta, dict) and event.meta.get("importer") == IMPORTER
            }
            active_keys = {candidate.import_key for candidate in candidates}
            if args.refresh:
                stale_ids = [event.id for key, event in events_by_key.items() if key not in active_keys]
                if stale_ids:
                    await db.execute(delete(Event).where(Event.id.in_(stale_ids)))

            for candidate in candidates:
                event = events_by_key.get(candidate.import_key)
                if event is None:
                    event = Event(world_id=world.id, title=candidate.document_title, date=candidate.date)
                    db.add(event)
                    created += 1
                else:
                    updated += 1
                event.source_document_id = candidate.document_id
                event.title = candidate.document_title[:255]
                event.description = candidate.context
                event.date = candidate.date
                event.date_order = candidate.date_order
                event.date_context = f"来源：《{candidate.document_title}》 · {candidate.section}"[:500]
                event.entity_ids = list(candidate.entity_ids)
                event.tags = ["时间线", "原文日期", candidate.section][:3]
                event.source_text = candidate.context
                event.extracted_by_ai = False
                event.meta = {
                    "importer": IMPORTER,
                    "import_key": candidate.import_key,
                    "evidence_kind": "explicit_date_mention",
                    "confidence": "source-backed",
                    "score": candidate.score,
                }
            await db.commit()
            print(f"{world.name}: {len(candidates)} events")

        return {
            "worlds": len(worlds),
            "populated_worlds": populated_worlds,
            "skipped_curated_worlds": skipped_curated,
            "created": created,
            "updated": updated,
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", action="append", help="Only process this world slug; repeatable")
    parser.add_argument("--max-events-per-world", type=int, default=120)
    parser.add_argument("--include-curated-worlds", action="store_true")
    parser.add_argument("--refresh", action="store_true")
    return parser.parse_args()


async def main() -> None:
    result = await build(parse_args())
    for key, value in result.items():
        print(f"{key}: {value}")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
