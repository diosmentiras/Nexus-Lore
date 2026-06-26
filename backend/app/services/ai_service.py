"""AI 服务层 — 支持 Ollama / OpenAI / DeepSeek"""

from __future__ import annotations

from app.config import settings


class AiService:
    """统一的 AI 调用封装，支持多 Provider 切换"""

    def __init__(self):
        self.provider = settings.ai_provider
        self.endpoint = settings.ai_endpoint
        self.api_key = settings.ai_api_key
        self.model = settings.ai_model

    async def extract_entities(self, text: str, types: list[str]) -> list[dict]:
        """将原始文本解析为结构化实体列表"""
        # TODO: 实现 LLM 调用
        # - 构建 system prompt（NER 指令）
        # - 调用 LLM（流式 / 非流式）
        # - 解析 JSON 结果
        return []

    async def resolve_fuzzy_date(self, context: str) -> str | None:
        """解析模糊时间描述（如"三年后"）"""
        return None

    async def lint_timeline(self) -> list[dict]:
        """时间线一致性检查"""
        return []

    async def lint_factions(self) -> list[dict]:
        """派系一致性检查"""
        return []


ai_service = AiService()
