#!/usr/bin/env python3
"""Import every SCP-CN canon hub as an isolated Nexus-Lore world.

The importer reads both the translated international canon index and the
Chinese branch canon index. Each hub becomes a world with a Lore dossier; the
hub's explicit internal article links become source documents. Links listed
under clear entity sections are also indexed as Lore entities.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import os
import re
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse, urlunparse

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))
os.environ.setdefault("DATABASE_URL", f"sqlite+aiosqlite:///{BACKEND_ROOT / 'data/dev.db'}")
os.environ.setdefault("DEBUG", "false")

import httpx
from bs4 import BeautifulSoup, Tag
from sqlalchemy import select

from app.db.session import async_session, engine
from app.models import Base, Entity, Event, SourceDocument, World


INDEX_URL = "https://scp-wiki-cn.wikidot.com/canon-hub"
CN_INDEX_URL = "https://scp-wiki-cn.wikidot.com/canon-hub-cn"
SITE_ROOT = "https://scp-wiki-cn.wikidot.com"
SOURCE_SITE = "scp-wiki-cn"
IMPORTER = "all-canon-hubs-v1"


@dataclass(frozen=True)
class CanonRef:
    name: str
    url: str
    description: str
    catalog: str
    maintained: bool = True

    @property
    def slug(self) -> str:
        return urlparse(self.url).path.strip("/")[:120]


@dataclass(frozen=True)
class ArticleRef:
    title: str
    url: str
    section: str


@dataclass(frozen=True)
class FetchedPage:
    requested_url: str
    resolved_url: str | None
    title: str
    content: str
    state: str
    error: str | None = None


EXCLUDED_SLUGS = {
    "", "canon-hub", "canon-hub-cn", "main", "about-the-scp-foundation",
    "faq", "guide-hub", "guide-for-newcomers", "how-to-write-an-scp",
    "scp-series", "scp-series-cn", "tales-by-title", "tales-by-author",
    "site-rules", "credits", "licensing-guide", "tag-guide", "tag-search",
    "top-rated-pages", "most-recently-created", "most-recently-edited",
    "random:random-page", "forum:start", "system:page-tags", "authors-pages",
}

EXCLUDED_PREFIXES = (
    "system:", "forum:", "user:", "nav:", "component:", "theme:",
    "css:", "local--files", "fragment:", "random:", "module-rate",
)

EXCLUDED_LABELS = {
    "此", "这里", "链接", "原文", "作者", "译者", "主页", "首页", "返回",
    "上一页", "下一页", "展开", "收起", "更多", "edit", "history", "files",
    "print", "site tools", "options", "backlinks", "讨论", "评分", "标签",
}


def clean_text(value: Any) -> str:
    return " ".join(str(value or "").replace("\xa0", " ").split()).strip(" :\n\t")


def normalized_hash(content: str) -> str:
    normalized = "\n".join(line.rstrip() for line in content.strip().splitlines())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def normalize_page_url(base_url: str, href: str | None) -> str | None:
    if not href or href.startswith(("#", "javascript:", "mailto:")):
        return None
    parsed = urlparse(urljoin(base_url, href))
    if parsed.netloc.lower() not in {
        "scp-wiki-cn.wikidot.com", "www.scp-wiki-cn.wikidot.com",
        "scp-wiki-cn.net", "www.scp-wiki-cn.net",
    }:
        return None
    slug = parsed.path.strip("/")
    if not slug or "/" in slug or slug.lower() in EXCLUDED_SLUGS:
        return None
    lowered = slug.lower()
    if lowered.startswith(EXCLUDED_PREFIXES):
        return None
    return urlunparse(("https", "scp-wiki-cn.wikidot.com", f"/{slug}", "", "", ""))


def page_text(soup: BeautifulSoup) -> str:
    root = soup.select_one("#page-content")
    if root is None:
        return ""
    copy = BeautifulSoup(str(root), "html.parser")
    for node in copy.select(
        "script, style, .page-rate-widget-box, .page-tags, .footnotes-footer, "
        ".licensebox, .creditRate, .printuser"
    ):
        node.decompose()
    return "\n".join(
        line.strip()
        for line in copy.get_text("\n").splitlines()
        if line.strip()
    )


def first_paragraphs(content: str, *, limit: int = 900, count: int = 4) -> str:
    lines = [clean_text(line) for line in content.splitlines() if clean_text(line)]
    useful: list[str] = []
    for line in lines:
        lowered = line.casefold()
        if len(line) < 12 or lowered.startswith(("评分", "页面标签", "脚注", "译者")):
            continue
        if line not in useful:
            useful.append(line)
        if len(useful) >= count:
            break
    text = "\n\n".join(useful)
    return text if len(text) <= limit else text[: limit - 3].rstrip() + "..."


def short_summary(content: str, fallback: str) -> str:
    paragraph = first_paragraphs(content, limit=260, count=2)
    return paragraph or fallback


def date_markers(content: str) -> list[str]:
    patterns = (
        r"(?<!\d)(?:1[0-9]{3}|20\d{2}|21\d{2})[-/.](?:0?[1-9]|1[0-2])(?:[-/.](?:0?[1-9]|[12]\d|3[01]))?",
        r"(?<!\d)(?:1[0-9]{3}|20\d{2}|21\d{2})年(?:\d{1,2}月(?:\d{1,2}日)?)?",
        r"(?<!\d)(?:1[0-9]{3}|20\d{2}|21\d{2})(?!\d)",
    )
    found: list[str] = []
    for pattern in patterns:
        for marker in re.findall(pattern, content):
            if marker not in found:
                found.append(marker)
    return found[:20]


def direct_description(block: Tag, heading: Tag | None) -> str:
    paragraphs = []
    for paragraph in block.find_all("p", recursive=False):
        if paragraph.find_parent(class_="snippet"):
            continue
        text = clean_text(paragraph.get_text(" ", strip=True))
        if text:
            paragraphs.append(text)
    if not paragraphs and heading:
        sibling = heading.find_next_sibling("p")
        if sibling:
            paragraphs.append(clean_text(sibling.get_text(" ", strip=True)))
    return " ".join(paragraphs)[:1800]


def parse_canon_indexes(main_html: str, cn_html: str) -> list[CanonRef]:
    canons: list[CanonRef] = []
    main = BeautifulSoup(main_html, "html.parser")
    selectors = (
        (".canon-wrapper:not(.sub) > .canon-block", "international", True),
        (".canon-block.the-world-kept-turning", "international", True),
        (".canon-wrapper.sub > .canon-block", "international-unmaintained", False),
    )
    for selector, catalog, maintained in selectors:
        for block in main.select(selector):
            heading = block.find(["h1", "h2", "h3"])
            link = heading.find("a", href=True) if heading else None
            url = normalize_page_url(INDEX_URL, link.get("href")) if link else None
            name = clean_text(link.get_text(" ", strip=True)) if link else ""
            if url and name:
                canons.append(CanonRef(name, url, direct_description(block, heading), catalog, maintained))

    cn = BeautifulSoup(cn_html, "html.parser")
    for block in cn.select("#page-content > .content-panel.centered.series"):
        heading = block.find(["h1", "h2", "h3"])
        link = heading.find("a", href=True) if heading else None
        url = normalize_page_url(CN_INDEX_URL, link.get("href")) if link else None
        name = clean_text(heading.get_text(" ", strip=True)) if heading else ""
        if url and name:
            canons.append(CanonRef(name, url, direct_description(block, heading), "scp-cn", True))

    unique: dict[str, CanonRef] = {}
    for canon in canons:
        unique.setdefault(canon.url, canon)
    return list(unique.values())


def parse_article_refs(hub_url: str, html: str, canon_urls: set[str]) -> list[ArticleRef]:
    soup = BeautifulSoup(html, "html.parser")
    root = soup.select_one("#page-content")
    if root is None:
        return []
    refs: dict[str, ArticleRef] = {}
    current_section = "未分类作品"
    for node in root.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "a"]):
        if node.name != "a":
            heading = clean_text(node.get_text(" ", strip=True))
            if heading:
                current_section = heading[:120]
            continue
        if not node.get("href"):
            continue
        if node.find_parent(class_=("printuser", "page-rate-widget-box", "licensebox", "creditRate")):
            continue
        title = clean_text(node.get_text(" ", strip=True))
        if not title or title.casefold() in EXCLUDED_LABELS:
            continue
        section_lower = current_section.casefold()
        title_lower = title.casefold()
        if "著作信息" in section_lower or "author information" in section_lower:
            continue
        if any(marker in title_lower for marker in ("作者页", "艺作页", "author page", "更多作品")):
            continue
        url = normalize_page_url(hub_url, node.get("href"))
        if not url or url == hub_url or url in canon_urls:
            continue
        refs.setdefault(url, ArticleRef(title[:255], url, current_section))
    return list(refs.values())


def classify_article(article: ArticleRef) -> str | None:
    slug = urlparse(article.url).path.strip("/").casefold()
    section = article.section.casefold()
    if slug.startswith("scp-") and any(character.isdigit() for character in slug):
        return "containment"
    rules = (
        (("人物", "角色", "人员", "character", "cast"), "character"),
        (("组织", "势力", "阵营", "派系", "团体", "organization", "group", "faction"), "faction"),
        (("地点", "位置", "地区", "站点", "location", "place"), "location"),
        (("物品", "装备", "遗物", "artifact", "object", "item"), "item"),
        (("异常", "项目", "scp", "anomal"), "containment"),
    )
    for words, entity_type in rules:
        if any(word in section for word in words):
            return entity_type
    return None


async def fetch_page(client: httpx.AsyncClient, semaphore: asyncio.Semaphore, article: ArticleRef) -> FetchedPage:
    last_error = "unknown error"
    async with semaphore:
        for attempt in range(2):
            try:
                response = await client.get(article.url)
                if response.status_code == 404:
                    return FetchedPage(article.url, None, article.title, "", "missing", "HTTP 404")
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")
                content = page_text(soup)
                if not content or soup.select_one(".new-page-box"):
                    return FetchedPage(article.url, str(response.url), article.title, "", "missing", "empty page")
                title_node = soup.select_one("#page-title")
                title = clean_text(title_node.get_text(" ", strip=True)) if title_node else article.title
                return FetchedPage(article.url, str(response.url), title or article.title, content, "available")
            except (httpx.HTTPError, ValueError) as exc:
                last_error = f"{type(exc).__name__}: {exc}"
                if attempt == 0:
                    await asyncio.sleep(0.8)
    return FetchedPage(article.url, None, article.title, "", "missing", last_error[:500])


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
        document = SourceDocument(world_id=world_id, title=title[:255], url=url, content=content)
        db.add(document)
    document.title = title[:255]
    document.source_site = SOURCE_SITE
    document.content = content
    document.content_hash = normalized_hash(content)
    document.status = status
    document.analysis_summary = summary
    document.meta = metadata
    await db.flush()
    return document


async def upsert_indexed_entity(
    db,
    *,
    world: World,
    article: ArticleRef,
    document: SourceDocument,
    entity_type: str,
) -> Entity:
    import_key = f"{IMPORTER}:entity:{article.url}"
    entities = (
        await db.execute(select(Entity).where(Entity.world_id == world.id))
    ).scalars().all()
    entity = next(
        (item for item in entities if isinstance(item.meta, dict) and item.meta.get("import_key") == import_key),
        None,
    )
    if entity is None:
        entity = Entity(world_id=world.id, name=document.title, entity_type=entity_type)
        db.add(entity)
    summary = short_summary(document.content, f"设定中心将《{document.title}》收录在“{article.section}”分区。")
    background = first_paragraphs(document.content, limit=1100, count=6) or summary
    excerpt = first_paragraphs(document.content, limit=420, count=3)
    entity.source_document_id = document.id
    entity.name = document.title[:255]
    entity.entity_type = entity_type
    entity.summary = summary
    entity.background = background
    entity.tags = [world.name, article.section, "来源目录提取"]
    entity.source_text = excerpt
    entity.extracted_by_ai = False
    entity.meta = {
        "importer": IMPORTER,
        "import_key": import_key,
        "canonical_url": article.url,
        "catalog_section": article.section,
        "stories": [{
            "title": document.title,
            "url": article.url,
            "document_id": str(document.id),
            "status": document.status,
            "analysis_summary": document.analysis_summary,
        }],
        "profile": {
            "version": 1,
            "kind_label": entity_type,
            "overview": summary,
            "story_count": 1,
            "available_story_count": 1 if document.status != "missing" else 0,
            "evidence": ([{
                "document_id": str(document.id),
                "title": document.title,
                "url": article.url,
                "matched_alias": article.section,
                "excerpt": excerpt,
            }] if excerpt else []),
            "co_entities": [],
            "date_markers": document.meta.get("date_markers", []),
            "source_note": "该条目依据设定中心的明确分区与原文归档生成，未使用未经原文支持的推断。",
        },
    }
    await db.flush()
    return entity


async def upsert_world_dossier(
    db,
    *,
    world: World,
    canon: CanonRef,
    hub_document: SourceDocument,
    article_documents: list[tuple[ArticleRef, SourceDocument]],
    indexed_entities: list[Entity],
) -> Entity:
    import_key = f"{IMPORTER}:dossier:{canon.slug}"
    existing = (
        await db.execute(select(Entity).where(Entity.world_id == world.id))
    ).scalars().all()
    dossier = next(
        (item for item in existing if isinstance(item.meta, dict) and item.meta.get("import_key") == import_key),
        None,
    )
    if dossier is None:
        dossier = Entity(world_id=world.id, name=canon.name, entity_type="world")
        db.add(dossier)

    available = [(article, document) for article, document in article_documents if document.status != "missing"]
    all_dates: list[str] = []
    for _, document in available:
        for marker in document.meta.get("date_markers", []):
            if marker not in all_dates:
                all_dates.append(marker)
    evidence = []
    hub_excerpt = first_paragraphs(hub_document.content, limit=420, count=3)
    if hub_excerpt:
        evidence.append({
            "document_id": str(hub_document.id), "title": canon.name, "url": canon.url,
            "matched_alias": "设定中心概述", "excerpt": hub_excerpt,
        })
    for article, document in available[:4]:
        excerpt = first_paragraphs(document.content, limit=360, count=2)
        if excerpt:
            evidence.append({
                "document_id": str(document.id), "title": document.title, "url": article.url,
                "matched_alias": article.section, "excerpt": excerpt,
            })

    description = canon.description or short_summary(hub_document.content, f"《{canon.name}》设定中心。")
    background = "\n\n".join([
        f"核心设定：{description}",
        f"资料范围：设定中心明确列出 {len(article_documents)} 篇站内作品，已读取 {len(available)} 篇，失效或暂时不可用 {len(article_documents) - len(available)} 篇。",
        f"结构化索引：从明确的人物、组织、地点、物品或异常分区建立了 {len(indexed_entities)} 个 Lore 条目；其余作品作为来源文档保留。",
    ])
    stories = [
        {
            "title": document.title,
            "url": article.url,
            "document_id": str(document.id),
            "status": document.status,
            "analysis_summary": document.analysis_summary,
        }
        for article, document in article_documents
    ]
    co_entities = [
        {
            "id": str(entity.id), "name": entity.name, "entity_type": entity.entity_type,
            "shared_story_count": 1, "shared_story_titles": [entity.meta.get("catalog_section", "设定中心目录")],
        }
        for entity in indexed_entities[:30]
    ]
    dossier.source_document_id = hub_document.id
    dossier.name = canon.name[:255]
    dossier.entity_type = "world"
    dossier.summary = description[:1000]
    dossier.background = background
    dossier.tags = ["世界观", "SCP-CN", "设定中心", canon.catalog]
    dossier.source_text = hub_excerpt
    dossier.extracted_by_ai = False
    dossier.meta = {
        "importer": IMPORTER,
        "import_key": import_key,
        "canonical_name": canon.name,
        "canonical_url": canon.url,
        "adaptation": canon.name,
        "stories": stories,
        "profile": {
            "version": 1,
            "kind_label": "世界观",
            "overview": description,
            "adaptation_note": "该条目是设定中心的世界观总档案。",
            "story_count": len(article_documents),
            "available_story_count": len(available),
            "evidence": evidence,
            "co_entities": co_entities,
            "date_markers": all_dates[:20],
            "source_note": "内容来自 SCP 基金会中文分部设定中心及其明确列出的站内作品；未明确说明之处不作推断。",
        },
    }
    await db.flush()
    return dossier


async def import_canon(
    client: httpx.AsyncClient,
    semaphore: asyncio.Semaphore,
    canon: CanonRef,
    canon_urls: set[str],
    args: argparse.Namespace,
) -> dict[str, int]:
    hub_ref = ArticleRef(canon.name, canon.url, "设定中心")
    hub_page = await fetch_page(client, semaphore, hub_ref)
    if hub_page.state == "available":
        hub_response = await client.get(canon.url)
        hub_response.raise_for_status()
        articles = parse_article_refs(canon.url, hub_response.text, canon_urls)
    else:
        hub_page = FetchedPage(
            requested_url=canon.url,
            resolved_url=None,
            title=canon.name,
            content=f"设定总览页收录了《{canon.name}》，但该设定中心页当前不可用。\n{canon.description}",
            state="missing",
            error=hub_page.error,
        )
        articles = []
    if args.max_articles is not None:
        articles = articles[: args.max_articles]

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async with async_session() as db:
        world = (await db.execute(select(World).where(World.slug == canon.slug))).scalar_one_or_none()
        if world is None:
            world = World(name=canon.name, slug=canon.slug)
            db.add(world)
        world.name = canon.name
        world.description = canon.description or short_summary(hub_page.content, f"《{canon.name}》设定中心。")
        world.source_url = canon.url
        await db.flush()

        hub_document = await upsert_document(
            db,
            world_id=str(world.id),
            title=hub_page.title or canon.name,
            url=canon.url,
            content=hub_page.content,
            status="analyzed" if hub_page.state == "available" else "missing",
            summary=(
                f"已读取设定中心正文 {len(hub_page.content)} 字，识别 {len(articles)} 个站内作品链接。"
                if hub_page.state == "available"
                else f"设定总览保留了《{canon.name}》的索引，但该中心页当前不可用。"
            ),
            metadata={
                "importer": IMPORTER, "document_kind": "world_hub",
                "catalog": canon.catalog, "maintained": canon.maintained,
                "date_markers": date_markers(hub_page.content),
                "link_state": hub_page.state, "fetch_error": hub_page.error,
            },
        )

        existing_documents = (
            await db.execute(select(SourceDocument).where(SourceDocument.world_id == world.id))
        ).scalars().all()
        by_url = {document.url: document for document in existing_documents if document.url}
        to_fetch = [
            article for article in articles
            if args.refresh or article.url not in by_url or by_url[article.url].status == "missing"
        ]
        fetched = await asyncio.gather(*(fetch_page(client, semaphore, article) for article in to_fetch))
        fetched_by_url = {page.requested_url: page for page in fetched}

        article_documents: list[tuple[ArticleRef, SourceDocument]] = []
        indexed_entities: list[Entity] = []
        missing = 0
        for article in articles:
            page = fetched_by_url.get(article.url)
            if page is None:
                document = by_url[article.url]
            else:
                markers = date_markers(page.content)
                state = "analyzed" if page.state == "available" else "missing"
                content = page.content or f"设定中心列出了《{article.title}》，但该页面当前不可用。"
                summary = (
                    f"已读取正文 {len(content)} 字；位于“{article.section}”分区，识别 {len(markers)} 个日期标记。"
                    if page.state == "available"
                    else f"链接当前不可用；保留设定中心的“{article.section}”目录映射。"
                )
                document = await upsert_document(
                    db,
                    world_id=str(world.id), title=page.title or article.title, url=article.url,
                    content=content, status=state, summary=summary,
                    metadata={
                        "importer": IMPORTER, "document_kind": "canon_article",
                        "catalog_section": article.section, "link_state": page.state,
                        "resolved_url": page.resolved_url, "date_markers": markers,
                        "fetch_error": page.error,
                    },
                )
            article_documents.append((article, document))
            if document.status == "missing":
                missing += 1
                continue
            entity_type = classify_article(article)
            if entity_type:
                indexed_entities.append(
                    await upsert_indexed_entity(
                        db, world=world, article=article, document=document, entity_type=entity_type
                    )
                )

        await upsert_world_dossier(
            db,
            world=world,
            canon=canon,
            hub_document=hub_document,
            article_documents=article_documents,
            indexed_entities=indexed_entities,
        )
        world.meta = {
            "source_site": SOURCE_SITE,
            "importer": IMPORTER,
            "catalog": canon.catalog,
            "maintained": canon.maintained,
            "hub_url": canon.url,
            "article_count": len(article_documents),
            "available_article_count": len(article_documents) - missing,
            "missing_article_count": missing,
            "indexed_entity_count": len(indexed_entities),
            "last_imported_at": datetime.now(UTC).isoformat(),
            "premise_points": [
                point.strip()
                for point in re.split(r"(?<=[。！？!?])", world.description or "")
                if len(point.strip()) >= 8
            ][:4],
        }
        await db.commit()
        return {
            "articles": len(article_documents),
            "available": len(article_documents) - missing,
            "missing": missing,
            "entities": len(indexed_entities) + 1,
        }


async def fetch_text(client: httpx.AsyncClient, url: str) -> str:
    response = await client.get(url)
    response.raise_for_status()
    return response.text


async def run(args: argparse.Namespace) -> None:
    headers = {"User-Agent": "Nexus-Lore/1.1 (canon archive importer; polite bounded concurrency)"}
    timeout = httpx.Timeout(args.timeout)
    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=timeout) as client:
        main_html, cn_html = await asyncio.gather(
            fetch_text(client, INDEX_URL), fetch_text(client, CN_INDEX_URL)
        )
        canons = parse_canon_indexes(main_html, cn_html)
        if args.only:
            requested = {item.strip() for item in args.only.split(",") if item.strip()}
            canons = [canon for canon in canons if canon.slug in requested or canon.name in requested]
        if not args.include_aces:
            canons = [canon for canon in canons if canon.slug != "aces-and-eights"]
        if args.limit_worlds is not None:
            canons = canons[: args.limit_worlds]

        print(f"discovered_canons: {len(parse_canon_indexes(main_html, cn_html))}", flush=True)
        print(f"selected_canons: {len(canons)}", flush=True)
        canon_urls = {canon.url for canon in parse_canon_indexes(main_html, cn_html)}
        semaphore = asyncio.Semaphore(args.concurrency)
        totals = {"worlds": 0, "failed": 0, "articles": 0, "available": 0, "missing": 0, "entities": 0}
        failures: list[tuple[str, str]] = []
        for index, canon in enumerate(canons, start=1):
            try:
                result = await import_canon(client, semaphore, canon, canon_urls, args)
                totals["worlds"] += 1
                for key in ("articles", "available", "missing", "entities"):
                    totals[key] += result[key]
                print(
                    f"[{index}/{len(canons)}] {canon.name}: "
                    f"articles={result['articles']} available={result['available']} "
                    f"missing={result['missing']} lore={result['entities']}",
                    flush=True,
                )
            except Exception as exc:
                totals["failed"] += 1
                failures.append((canon.name, f"{type(exc).__name__}: {exc}"))
                print(f"[{index}/{len(canons)}] {canon.name}: FAILED {type(exc).__name__}: {exc}", flush=True)

        print("\nsummary", flush=True)
        for key, value in totals.items():
            print(f"{key}: {value}", flush=True)
        for name, error in failures:
            print(f"failure: {name}: {error}", flush=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--concurrency", type=int, default=6)
    parser.add_argument("--timeout", type=float, default=25.0)
    parser.add_argument("--only", help="Comma-separated canon names or URL slugs")
    parser.add_argument("--limit-worlds", type=int)
    parser.add_argument("--max-articles", type=int)
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--include-aces", action="store_true")
    return parser.parse_args()


async def main() -> None:
    try:
        await run(parse_args())
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
