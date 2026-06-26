"""Linter — 设定冲突检查 & 管理 API"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import LintIssue
from app.schemas import LintIssueResponse, LintRunResponse

router = APIRouter(prefix="/api/linter", tags=["Linter"])


@router.get("/issues", response_model=list[LintIssueResponse])
async def list_issues(
    resolved: bool | None = None,
    severity: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(LintIssue).order_by(LintIssue.created_at.desc())
    if resolved is not None:
        stmt = stmt.where(LintIssue.resolved == resolved)
    if severity:
        stmt = stmt.where(LintIssue.severity == severity)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/run", response_model=LintRunResponse)
async def run_lint(db: AsyncSession = Depends(get_db)):
    """
    运行全量设定冲突检查。

    当前检查项：
    1. 时间线矛盾 — 同一实体在不同事件中的时间冲突
    2. 派系一致性
    3. 重复实体检测
    """
    # TODO: 集成 LLM 语义级检查
    # 当前返回空结果（骨架已就绪）
    return LintRunResponse(issues=[], summary={"error": 0, "warning": 0, "info": 0})
