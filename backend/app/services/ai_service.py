"""AI 服务层 — 支持 Ollama / OpenAI / DeepSeek"""

from __future__ import annotations

import json
from typing import Any

import httpx

from app.config import settings


class AiService:
    """统一的 AI 调用封装，支持多 Provider 切换"""

    def __init__(self):
        self.provider = settings.ai_provider
        self.endpoint = settings.ai_endpoint
        self.api_key = settings.ai_api_key
        self.model = settings.ai_model

    def _prompt(self, text: str, types: list[str]) -> list[dict[str, str]]:
        system = (
            "你是世界观设定资料整理助手。"
            "请从文章中抽取可复用的设定数据，只输出 JSON，不输出 Markdown。"
            "不要复述长段原文；用简洁中文总结，并保留出处线索。"
            "关系类型只能使用 ally, hostile, neutral, member, owns, located_at, other。"
            "实体类型只能使用 character, faction, item, location, event, containment。"
        )
        schema = {
            "entities": [
                {
                    "name": "实体名",
                    "entity_type": "character|faction|item|location|event|containment",
                    "summary": "一句话摘要",
                    "background": "较完整但不冗长的设定说明",
                    "tags": ["标签"],
                    "date": "明确时间，没有则为 null",
                    "date_context": "时间依据或模糊时间描述",
                    "relations": [
                        {"target": "另一实体名", "relation_type": "member|hostile|ally|neutral|owns|located_at|other", "label": "关系说明"}
                    ],
                }
            ],
            "events": [
                {
                    "title": "事件名",
                    "description": "事件摘要",
                    "date": "时间点或年代，没有明确时间则用 unknown",
                    "date_context": "时间依据",
                    "entities": ["相关实体名"],
                    "tags": ["标签"],
                }
            ],
        }
        user = (
            f"需要抽取的类型：{', '.join(types)}\n"
            f"输出 JSON 结构示例：{json.dumps(schema, ensure_ascii=False)}\n\n"
            f"文章正文：\n{text}"
        )
        return [{"role": "system", "content": system}, {"role": "user", "content": user}]

    def _empty_result(self) -> dict[str, list[dict[str, Any]]]:
        return {"entities": [], "events": []}

    def _normalize_result(self, result: Any) -> dict[str, list[dict[str, Any]]]:
        if not isinstance(result, dict):
            return self._empty_result()
        entities = result.get("entities") if isinstance(result.get("entities"), list) else []
        events = result.get("events") if isinstance(result.get("events"), list) else []
        return {"entities": entities, "events": events}

    async def extract_lore(self, text: str, types: list[str]) -> dict[str, list[dict[str, Any]]]:
        """将原始文本解析为实体、事件与关系。"""
        if not text.strip():
            return self._empty_result()

        messages = self._prompt(text, types)
        if self.provider == "ollama":
            return await self._extract_with_ollama(messages)
        if self.provider in {"openai", "deepseek"} and self.api_key:
            return await self._extract_with_openai_compatible(messages)
        return self._empty_result()

    async def extract_entities(self, text: str, types: list[str]) -> list[dict]:
        """兼容旧调用：只返回实体。"""
        result = await self.extract_lore(text, types)
        return result["entities"]

    def public_config(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "endpoint": self.endpoint,
            "model": self.model,
            "has_api_key": bool(self.api_key),
        }

    async def test_connection(self) -> dict[str, Any]:
        """Verify that the configured provider is reachable without generating text."""
        if self.provider == "ollama":
            url = self.endpoint.rstrip("/") + "/api/tags"
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(url)
                response.raise_for_status()
            models = [item.get("name") for item in response.json().get("models", []) if item.get("name")]
            return {"ok": True, "provider": self.provider, "models": models, "model_available": self.model in models}

        if self.provider in {"openai", "deepseek"}:
            if not self.api_key:
                return {"ok": False, "provider": self.provider, "detail": "API key is not configured"}
            endpoint = self.endpoint
            if self.provider == "openai" and endpoint == "http://localhost:11434":
                endpoint = "https://api.openai.com/v1"
            if self.provider == "deepseek" and endpoint == "http://localhost:11434":
                endpoint = "https://api.deepseek.com"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            async with httpx.AsyncClient(timeout=10, headers=headers) as client:
                response = await client.get(endpoint.rstrip("/") + "/models")
                response.raise_for_status()
            return {"ok": True, "provider": self.provider, "model_available": True}

        return {"ok": False, "provider": self.provider, "detail": "Unsupported AI provider"}

    async def _extract_with_ollama(self, messages: list[dict[str, str]]) -> dict[str, list[dict[str, Any]]]:
        url = self.endpoint.rstrip("/") + "/api/chat"
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                url,
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "format": "json",
                },
            )
            response.raise_for_status()
        content = response.json().get("message", {}).get("content", "{}")
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            return self._empty_result()
        return self._normalize_result(parsed)

    async def _extract_with_openai_compatible(self, messages: list[dict[str, str]]) -> dict[str, list[dict[str, Any]]]:
        from openai import AsyncOpenAI

        endpoint = self.endpoint
        if self.provider == "openai" and endpoint == "http://localhost:11434":
            endpoint = "https://api.openai.com/v1"
        if self.provider == "deepseek" and endpoint == "http://localhost:11434":
            endpoint = "https://api.deepseek.com"

        client = AsyncOpenAI(api_key=self.api_key, base_url=endpoint)
        response = await client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.1,
        )
        content = response.choices[0].message.content or "{}"
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            return self._empty_result()
        return self._normalize_result(parsed)

ai_service = AiService()
