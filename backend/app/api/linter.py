"""Linter — 设定冲突检查 & 管理 API"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import Entity, Event, LintIssue, Relation, World
from app.schemas import LintIssueResponse, LintIssueUpdate, LintRunResponse
from app.services.lore_linter import ENGINE_VERSION, build_lint_candidates

router = APIRouter(prefix="/api/linter", tags=["Linter"])


@router.get("/issues", response_model=list[LintIssueResponse])
async def list_issues(
    world_id: str | None = None,
    resolved: bool | None = None,
    severity: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(LintIssue).order_by(LintIssue.created_at.desc())
    if world_id:
        stmt = stmt.where(LintIssue.world_id == world_id)
    if resolved is not None:
        stmt = stmt.where(LintIssue.resolved == resolved)
    if severity:
        stmt = stmt.where(LintIssue.severity == severity)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/run", response_model=LintRunResponse)
async def run_lint(world_id: str | None = None, db: AsyncSession = Depends(get_db)):
    """
    运行全量设定冲突检查。

    当前检查项：
    1. 时间线矛盾 — 同一实体在不同事件中的时间冲突
    2. 派系一致性
    3. 重复实体检测
    """
    world_stmt = select(World)
    if world_id:
        world_stmt = world_stmt.where(World.id == world_id)
    worlds = list((await db.execute(world_stmt)).scalars().all())
    if world_id and not worlds:
        raise HTTPException(404, "World not found")

    generated: list[LintIssue] = []
    summary = {"error": 0, "warning": 0, "info": 0}
    for world in worlds:
        current_world_id = str(world.id)
        entities = list(
            (await db.execute(select(Entity).where(Entity.world_id == current_world_id))).scalars().all()
        )
        relations = list(
            (await db.execute(select(Relation).where(Relation.world_id == current_world_id))).scalars().all()
        )
        events = list(
            (await db.execute(select(Event).where(Event.world_id == current_world_id))).scalars().all()
        )

        existing = list(
            (
                await db.execute(
                    select(LintIssue).where(
                        LintIssue.world_id == current_world_id,
                        LintIssue.resolved == False,
                    )
                )
            ).scalars().all()
        )
        for issue in existing:
            if (issue.meta or {}).get("engine") == ENGINE_VERSION:
                await db.delete(issue)

        for candidate in build_lint_candidates(current_world_id, entities, relations, events):
            issue = LintIssue(
                world_id=current_world_id,
                severity=candidate.severity,
                title=candidate.title,
                description=candidate.description,
                entity1_id=candidate.entity1_id,
                entity2_id=candidate.entity2_id,
                entity1_name=candidate.entity1_name,
                entity2_name=candidate.entity2_name,
                issue_type=candidate.issue_type,
                source_lore_id=candidate.source_lore_id,
                meta={"engine": ENGINE_VERSION, **candidate.meta},
            )
            db.add(issue)
            generated.append(issue)
            summary[candidate.severity] += 1

    await db.flush()
    return LintRunResponse(issues=generated, summary=summary)


@router.patch("/issues/{issue_id}", response_model=LintIssueResponse)
async def update_issue(issue_id: str, data: LintIssueUpdate, db: AsyncSession = Depends(get_db)):
    issue = await db.get(LintIssue, issue_id)
    if not issue:
        raise HTTPException(404, "Lint issue not found")
    issue.resolved = data.resolved
    await db.flush()
    await db.refresh(issue)
    return issue
