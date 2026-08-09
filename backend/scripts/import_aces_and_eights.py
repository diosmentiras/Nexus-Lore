#!/usr/bin/env python3
"""Import the Aces and Eights spoiler index into Nexus-Lore.

The hub's spoiler section is an authoritative mapping from baseline SCP
concepts to their western reinterpretations. This importer keeps that mapping,
fetches each referenced story once, and records missing/red links explicitly.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse, urlunparse

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))
os.environ.setdefault("DATABASE_URL", f"sqlite+aiosqlite:///{BACKEND_ROOT / 'data/dev.db'}")

import httpx
from bs4 import BeautifulSoup, Tag
from sqlalchemy import select

from app.db.session import async_session, engine
from app.models import Base, Entity, Event, Relation, SourceDocument, World
from app.services.entity_profile_service import build_entity_profile


DEFAULT_HUB_URL = "https://scp-wiki-cn.wikidot.com/aces-and-eights"
SOURCE_SITE = "scp-wiki-cn"
IMPORTER_NAME = "aces-and-eights-spoiler-index-v1"


@dataclass(frozen=True)
class StoryRef:
    title: str
    url: str


@dataclass(frozen=True)
class MappingEntry:
    index: int
    slot: int
    canonical_name: str
    canonical_url: str | None
    adaptation: str
    stories: tuple[StoryRef, ...]
    raw_text: str

    @property
    def import_key(self) -> str:
        return f"aces-and-eights:mapping:{self.index}:{self.slot}"


@dataclass(frozen=True)
class FetchedPage:
    requested_url: str
    resolved_url: str | None
    title: str
    content: str
    state: str


def clean_text(value: str) -> str:
    return " ".join(value.replace("\xa0", " ").split()).strip(" :\n\t")


def content_hash(content: str) -> str:
    normalized = "\n".join(line.rstrip() for line in content.strip().splitlines())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def absolute_url(hub_url: str, href: str | None) -> str | None:
    if not href or href.startswith("javascript:"):
        return None
    return urljoin(hub_url, href)


def parse_spoiler_mappings(hub_url: str, html: str) -> list[MappingEntry]:
    soup = BeautifulSoup(html, "html.parser")
    spoiler = next(
        (heading for heading in soup.select("#page-content h1") if "剧透" in heading.get_text()),
        None,
    )
    if spoiler is None or spoiler.parent is None:
        raise RuntimeError("未找到‘剧透预警’区块")

    block = spoiler.parent.find_next_sibling("div", class_="collapsible-block")
    root = block.select_one(".collapsible-block-content > ul") if block else None
    if root is None:
        raise RuntimeError("未找到剧透区设定映射列表")

    entries: list[MappingEntry] = []
    for index, row in enumerate(root.find_all("li", recursive=False), start=1):
        sources = row.find_all("strong", recursive=False)
        adaptations = row.find_all("em", recursive=False)
        story_list = row.find("ul", recursive=False)
        stories: list[StoryRef] = []
        if story_list:
            seen_story_urls: set[str] = set()
            for link in story_list.select("a[href]"):
                url = absolute_url(hub_url, link.get("href"))
                if not url or url in seen_story_urls:
                    continue
                seen_story_urls.add(url)
                stories.append(StoryRef(clean_text(link.get_text(" ", strip=True)), url))

        raw_text = clean_text(row.get_text(" ", strip=True))
        for slot, source in enumerate(sources, start=1):
            source_link = source.find("a", href=True)
            canonical_name = clean_text(source.get_text(" ", strip=True))
            adaptation = clean_text(
                adaptations[slot - 1].get_text(" ", strip=True)
                if slot <= len(adaptations)
                else raw_text
            )
            entries.append(
                MappingEntry(
                    index=index,
                    slot=slot,
                    canonical_name=canonical_name,
                    canonical_url=absolute_url(hub_url, source_link.get("href")) if source_link else None,
                    adaptation=adaptation,
                    stories=tuple(stories),
                    raw_text=raw_text,
                )
            )
    return entries


def fallback_urls(url: str) -> list[str]:
    parsed = urlparse(url)
    urls = [url]
    if parsed.netloc in {"scp-wiki-cn.wikidot.com", "www.scp-wiki.net", "scp-wiki-cn.net", "www.scp-wiki-cn.net"}:
        fallback = urlunparse(parsed._replace(netloc="scp-wiki.wikidot.com"))
        if fallback not in urls:
            urls.append(fallback)
    return urls


def page_text(soup: BeautifulSoup) -> str:
    content = soup.select_one("#page-content")
    if content is None:
        return ""
    for node in content.select("script, style, .page-rate-widget-box, .page-tags, .footnotes-footer"):
        node.decompose()
    return "\n".join(
        line.strip()
        for line in content.get_text("\n").splitlines()
        if line.strip()
    )


async def fetch_page(
    client: httpx.AsyncClient,
    semaphore: asyncio.Semaphore,
    story: StoryRef,
) -> FetchedPage:
    errors: list[str] = []
    async with semaphore:
        for candidate in fallback_urls(story.url):
            try:
                response = await client.get(candidate)
                if response.status_code == 404:
                    errors.append(f"{candidate}: 404")
                    continue
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")
                content = page_text(soup)
                if not content:
                    errors.append(f"{candidate}: empty page")
                    continue
                title_node = soup.select_one("#page-title")
                title = clean_text(title_node.get_text(" ", strip=True)) if title_node else story.title
                return FetchedPage(story.url, str(response.url), title, content, "available")
            except (httpx.HTTPError, ValueError) as exc:
                errors.append(f"{candidate}: {type(exc).__name__}")

    note = "设定中心收录了该作品链接，但当前中文站与英文站的相应页面均不可用。"
    return FetchedPage(story.url, None, story.title, note, "missing")


UNCHANGED_MARKERS = (
    "基本上没变",
    "基本完全没变",
    "几乎完全相同",
    "largely unchanged",
    "largely the same",
)


def entity_name(entry: MappingEntry) -> str:
    source = entry.canonical_name.strip(" ,.")
    adaptation = entry.adaptation.strip(" :.,")
    lower = adaptation.lower()
    if any(marker in lower for marker in UNCHANGED_MARKERS):
        return source

    special_names = {
        "SCP-3055": "Fantasyland Players",
        "The offspring of the Scarlet King": "Flynn family",
        'SCP-2721 -LORD, AKA "bones",': "bones",
        "St. Christopher's Mental Institution in Mayford, Tennessee": "Christopher Mayford庄园",
    }
    if source in special_names:
        return special_names[source]

    named_prefixes = ("Agent ", "Detective ", "Dr. ", "Daniel ", "Elias ", "Iris ", "Leslie ", "Renard ", "Tobias ")
    if adaptation.startswith(named_prefixes) and "," in adaptation:
        return adaptation.split(",", 1)[0]
    if adaptation.startswith("the ") and len(adaptation.split()) <= 6:
        adaptation = adaptation[4:]
    if adaptation and len(adaptation) <= 80 and not adaptation.startswith(
        ("一个", "一名", "在", "a ", "an ", "the former", "his ")
    ):
        return adaptation
    return f"{source}（死者手牌版本）"


def entity_type(entry: MappingEntry, name: str) -> str:
    source = entry.canonical_name.lower()
    adaptation = entry.adaptation.lower()
    combined = f"{source} {adaptation} {name.lower()}"

    item_sources = {"scp-500", "bright 的护身符", "scp-268"}
    if source in item_sources or any(word in combined for word in ("护身符", "剑杖")):
        return "item"
    if any(
        word in combined
        for word in (
            "site-19",
            "酒吧",
            "scranton, nevada",
            "新多伦多",
            "观形坪",
            "plantation",
            "庄园",
        )
    ):
        return "location"
    if any(
        word in combined
        for word in (
            "事故处",
            "调查处",
            "联邦调查处",
            "联盟",
            "consortium",
            "教会",
            "团契",
            "公司",
            "义肢",
            "分裂者",
            "检查员",
            "骑兵旅",
            "哈佛1876届",
            "players",
            "messengers",
            "family",
            "site-87的人员",
            "colony of",
        )
    ):
        return "faction"
    if re.search(r"\bscp-\d+", source) and not any(
        word in combined for word in ("doctor", "博士", "agent", "特工", "男青年", "dog", "lucky", "leslie")
    ):
        return "containment"
    return "character"


def date_markers(content: str) -> list[str]:
    patterns = (
        r"(?<!\d)(?:18|19)\d{2}[-/.](?:0?[1-9]|1[0-2])(?:[-/.](?:0?[1-9]|[12]\d|3[01]))?",
        r"(?<!\d)(?:18|19)\d{2}年(?:\d{1,2}月(?:\d{1,2}日)?)?",
        r"(?<!\d)(?:18|19)\d{2}(?!\d)",
    )
    found: list[str] = []
    for pattern in patterns:
        for match in re.findall(pattern, content):
            if match not in found:
                found.append(match)
    return found[:20]


async def upsert_document(
    db,
    *,
    world_id: str,
    title: str,
    url: str,
    content: str,
    status: str,
    summary: str,
    metadata: dict[str, Any],
) -> SourceDocument:
    document = (
        await db.execute(
            select(SourceDocument).where(
                SourceDocument.world_id == world_id,
                SourceDocument.url == url,
            )
        )
    ).scalar_one_or_none()
    if document is None:
        document = SourceDocument(world_id=world_id, title=title, url=url, content=content)
        db.add(document)
    document.title = title[:255]
    document.source_site = SOURCE_SITE
    document.content = content
    document.content_hash = content_hash(content)
    document.status = status
    document.analysis_summary = summary
    document.meta = metadata
    await db.flush()
    return document


async def import_world(args: argparse.Namespace) -> dict[str, int]:
    timeout = httpx.Timeout(args.timeout)
    headers = {"User-Agent": "Nexus-Lore/1.0 (worldbuilding research importer)"}
    async with httpx.AsyncClient(follow_redirects=True, timeout=timeout, headers=headers) as client:
        hub_response = await client.get(args.hub_url)
        hub_response.raise_for_status()
        hub_html = hub_response.text
        hub_soup = BeautifulSoup(hub_html, "html.parser")
        hub_content = page_text(hub_soup)
        mappings = parse_spoiler_mappings(args.hub_url, hub_html)

        stories_by_url: dict[str, StoryRef] = {}
        for entry in mappings:
            for story in entry.stories:
                stories_by_url.setdefault(story.url, story)
        semaphore = asyncio.Semaphore(args.concurrency)
        fetched_pages = await asyncio.gather(
            *(fetch_page(client, semaphore, story) for story in stories_by_url.values())
        )

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async with async_session() as db:
        world = (
            await db.execute(select(World).where(World.slug == args.world_slug))
        ).scalar_one_or_none()
        if world is None:
            world = World(name=args.world_name, slug=args.world_slug)
            db.add(world)
        world.name = args.world_name
        world.description = (
            "这是一个将 SCP 神话改写为美国旧西部传奇的架空世界。"
            "在这条时间线中，内战直到 1867 年才结束，巴尔的摩遭到毁灭，幸存者涌向西部。"
            "SCP 基金会作为组织并不存在，但熟悉的博士、特工、异常和超自然组织会以牛仔、酒馆、"
            "骑兵旅、侦探社和边疆怪谈的形态重新出现。"
        )
        world.source_url = args.hub_url
        world.meta = {
            "source_site": SOURCE_SITE,
            "canonical_title": "Aces and Eights",
            "importer": IMPORTER_NAME,
            "mapping_rows": len({entry.index for entry in mappings}),
            "mapping_entities": len(mappings),
            "era": "美国旧西部，从 1867 年内战结束后展开",
            "premise_points": [
                "美国内战延续至 1867 年，李将军在里士满向谢尔曼投降。",
                "巴尔的摩在停战前被夷为平地，幸存者带着联邦补偿向西迁徙。",
                "SCP 基金会不存在；其人物、异常和相关组织被改造为西部时代对应物。",
                "同一人物或组织的早期描写构成后续故事应遵循的连续性。",
            ],
        }
        await db.flush()

        hub_document = await upsert_document(
            db,
            world_id=str(world.id),
            title="死者手牌",
            url=args.hub_url,
            content=hub_content,
            status="analyzed",
            summary=f"已解析剧透区 {len(mappings)} 个设定映射实体。",
            metadata={
                "importer": IMPORTER_NAME,
                "document_kind": "world_hub",
                "mapping_rows": len({entry.index for entry in mappings}),
                "mapping_entities": len(mappings),
            },
        )

        entries_by_story: dict[str, list[MappingEntry]] = {}
        for entry in mappings:
            for story in entry.stories:
                entries_by_story.setdefault(story.url, []).append(entry)

        story_documents: dict[str, SourceDocument] = {}
        for page in fetched_pages:
            linked_entries = entries_by_story.get(page.requested_url, [])
            markers = date_markers(page.content)
            if page.requested_url == args.hub_url:
                hub_document.meta = {
                    **hub_document.meta,
                    "resolved_url": page.resolved_url,
                    "date_markers": markers,
                    "mapped_canonical_names": [entry.canonical_name for entry in linked_entries],
                }
                story_documents[page.requested_url] = hub_document
                continue
            status = "analyzed" if page.state == "available" else "missing"
            summary = (
                f"已读取正文 {len(page.content)} 字，关联 {len(linked_entries)} 个设定映射"
                f"，识别 {len(markers)} 个日期标记。"
                if page.state == "available"
                else f"链接当前不可用；设定中心仍将其与 {len(linked_entries)} 个映射关联。"
            )
            story_documents[page.requested_url] = await upsert_document(
                db,
                world_id=str(world.id),
                title=page.title,
                url=page.requested_url,
                content=page.content,
                status=status,
                summary=summary,
                metadata={
                    "importer": IMPORTER_NAME,
                    "document_kind": "story",
                    "link_state": page.state,
                    "resolved_url": page.resolved_url,
                    "date_markers": markers,
                    "mapped_canonical_names": [entry.canonical_name for entry in linked_entries],
                },
            )

        existing_entities = (
            await db.execute(select(Entity).where(Entity.world_id == world.id))
        ).scalars().all()
        entities_by_key = {
            entity.meta.get("import_key"): entity
            for entity in existing_entities
            if isinstance(entity.meta, dict) and entity.meta.get("import_key")
        }
        entity_by_canonical: dict[str, Entity] = {}
        for entry in mappings:
            name = entity_name(entry)
            kind = entity_type(entry, name)
            entity = entities_by_key.get(entry.import_key)
            if entity is None:
                entity = Entity(world_id=world.id, name=name, entity_type=kind)
                db.add(entity)
            story_meta = [
                {
                    "title": story.title,
                    "url": story.url,
                    "document_id": str(story_documents[story.url].id) if story.url in story_documents else None,
                }
                for story in entry.stories
            ]
            entity.source_document_id = hub_document.id
            entity.name = name[:255]
            entity.entity_type = kind
            entity.summary = (
                f"{entry.canonical_name} 在‘死者手牌’世界中的对应设定：{entry.adaptation}。"
            )
            entity.background = entry.raw_text
            entity.tags = ["死者手牌", "SCP-CN", "设定映射", *[story.title for story in entry.stories]]
            entity.meta = {
                "importer": IMPORTER_NAME,
                "import_key": entry.import_key,
                "mapping_index": entry.index,
                "mapping_slot": entry.slot,
                "canonical_name": entry.canonical_name,
                "canonical_url": entry.canonical_url,
                "adaptation": entry.adaptation,
                "stories": story_meta,
            }
            entity.source_text = entry.raw_text
            entity.extracted_by_ai = False
            await db.flush()
            entities_by_key[entry.import_key] = entity
            entity_by_canonical[entry.canonical_name] = entity

        for story_url, document in story_documents.items():
            linked = entries_by_story.get(story_url, [])
            document.meta = {
                **document.meta,
                "mapped_entity_ids": [str(entity_by_canonical[e.canonical_name].id) for e in linked],
            }

        imported_entities = list(entities_by_key.values())
        documents_by_id = {
            str(document.id): document
            for document in [hub_document, *story_documents.values()]
        }
        for entity in imported_entities:
            summary, background, profile = build_entity_profile(entity, documents_by_id, imported_entities)
            entity.summary = summary
            entity.background = background
            entity.meta = {**entity.meta, "profile": profile}

        relation_specs = (
            ("Site-87的人员", "特异事故处", "member", "隶属于联邦调查处"),
            ("SCP-507", "特异事故处", "member", "UIU特工"),
            ("Penelope Gore", "特异事故处", "member", "Union Investigation Unit特工"),
            ("Ezra Everest", "全球超自然联盟", "member", "GOC执法者"),
            ("SCP-105", "Site-19", "located_at", "19号酒吧的新闻工作者"),
            ("SCP-3005", "SCP-3001", "located_at", "Scranton的The Anchor酒馆"),
            ("3T", "Percy Pinwheel", "other", "配偶"),
            ("解说者", "简化者", "other", "兄弟"),
        )
        existing_relations = (
            await db.execute(select(Relation).where(Relation.world_id == world.id))
        ).scalars().all()
        relations_by_key = {
            relation.meta.get("import_key"): relation
            for relation in existing_relations
            if isinstance(relation.meta, dict) and relation.meta.get("import_key")
        }
        relation_count = 0
        for source_name, target_name, relation_type, label in relation_specs:
            source = entity_by_canonical.get(source_name)
            target = entity_by_canonical.get(target_name)
            if source is None or target is None:
                continue
            import_key = f"aces-and-eights:relation:{source_name}:{target_name}:{label}"
            relation = relations_by_key.get(import_key)
            if relation is None:
                relation = Relation(source_id=source.id, target_id=target.id)
                db.add(relation)
            relation.world_id = world.id
            relation.source_document_id = hub_document.id
            relation.relation_type = relation_type
            relation.label = label
            relation.meta = {"importer": IMPORTER_NAME, "import_key": import_key}
            relation_count += 1

        timeline = (
            (
                "第682骑兵旅在第一次葛底斯堡战役现身",
                "1867-12-06之前",
                "报纸回顾了第一次葛底斯堡战役；传说中的黑色骑手与第682骑兵旅带来死亡与黑暗。",
                ["SCP-682"],
            ),
            (
                "巴尔的摩大毁灭",
                "1867-12-06前数日",
                "巴尔的摩在投降条款签署前数日被夷为平地，幸存者成为难民。",
                [],
            ),
            (
                "美国内战结束",
                "1867-12-06",
                "李将军在里士满向谢尔曼将军投降；条款宣布南方各州奴隶制非法，但其余部分被视为近乎南方的胜利。",
                [],
            ),
            (
                "林肯辞职并西行",
                "1867-12",
                "投降条款要求林肯总统辞职；他随后与家人乘火车向西进发。",
                [],
            ),
            (
                "巴尔的摩幸存者获得西部土地",
                "1867-12",
                "联邦向巴尔的摩大毁灭幸存者发放50美元，并承诺在西部分配土地，引发新一轮西迁。",
                [],
            ),
        )
        existing_events = (
            await db.execute(select(Event).where(Event.world_id == world.id))
        ).scalars().all()
        events_by_key = {
            event.meta.get("import_key"): event
            for event in existing_events
            if isinstance(event.meta, dict) and event.meta.get("import_key")
        }
        for order, (title, date, description, canonical_names) in enumerate(timeline, start=1):
            import_key = f"aces-and-eights:event:{order}"
            event = events_by_key.get(import_key)
            if event is None:
                event = Event(world_id=world.id, title=title, date=date)
                db.add(event)
            event.source_document_id = hub_document.id
            event.title = title
            event.description = description
            event.date = date
            event.date_context = "死者手牌设定中心的《巴尔的摩星报》历史简介"
            event.date_order = order
            event.entity_ids = [
                str(entity_by_canonical[name].id)
                for name in canonical_names
                if name in entity_by_canonical
            ]
            event.tags = ["死者手牌", "时间线", "历史简介"]
            event.meta = {"importer": IMPORTER_NAME, "import_key": import_key}
            event.source_text = description
            event.extracted_by_ai = False

        await db.commit()
        missing_count = sum(page.state == "missing" for page in fetched_pages)
        return {
            "mapping_rows": len({entry.index for entry in mappings}),
            "entities": len(mappings),
            "story_documents": len(fetched_pages),
            "available_documents": len(fetched_pages) - missing_count,
            "missing_documents": missing_count,
            "relations": relation_count,
            "events": len(timeline),
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hub-url", default=DEFAULT_HUB_URL)
    parser.add_argument("--world-name", default="死者手牌（SCP-CN）")
    parser.add_argument("--world-slug", default="aces-and-eights")
    parser.add_argument("--concurrency", type=int, default=8)
    parser.add_argument("--timeout", type=float, default=30.0)
    return parser.parse_args()


async def main() -> None:
    result = await import_world(parse_args())
    for key, value in result.items():
        print(f"{key}: {value}")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
