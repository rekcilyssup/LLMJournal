import json
import re

import httpx

from core.config import settings
from services.llm.base import BaseLLMService


class LocalLLMService(BaseLLMService):
    def __init__(self) -> None:
        self.base_url = settings.local_llm_base_url.rstrip("/")
        self.model = settings.local_llm_model

    async def analyze_emotion(self, text: str) -> dict:
        prompt = (
            "Analyze the journal text and return strict JSON only with keys: "
            'emotion (string), keywords (string array), summary (string).\n'
            "Do not include markdown fences or any extra text."
        )
        payload = {
            "model": self.model,
            "temperature": 0.2,
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": text},
            ],
        }

        endpoint = f"{self.base_url}/chat/completions"
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(endpoint, json=payload)
                response.raise_for_status()
                raw = response.json()["choices"][0]["message"]["content"]
                parsed = self._extract_json(raw)
                return self._normalize_result(parsed, text)
        except Exception:
            return self._fallback_result(text)

    def _extract_json(self, raw: str) -> dict:
        patterns = [
            r"```json\s*(\{[\s\S]*?\})\s*```",
            r"```[a-zA-Z0-9_]*\s*(\{[\s\S]*?\})\s*```",
            r"(\{[\s\S]*\})",
        ]

        for pattern in patterns:
            match = re.search(pattern, raw, flags=re.DOTALL)
            if not match:
                continue
            candidate = match.group(1).strip()
            try:
                obj = json.loads(candidate)
                if all(k in obj for k in ("emotion", "keywords", "summary")):
                    return obj
            except json.JSONDecodeError:
                continue

        # Last attempt: strip known markdown artifacts and retry.
        cleaned = re.sub(r"```[a-zA-Z0-9_]*|```", "", raw).strip()
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                obj = json.loads(cleaned[start : end + 1])
                if all(k in obj for k in ("emotion", "keywords", "summary")):
                    return obj
            except json.JSONDecodeError:
                pass

        return {}

    def _normalize_result(self, data: dict, text: str) -> dict:
        emotion = str(data.get("emotion") or "neutral").strip() or "neutral"

        raw_keywords = data.get("keywords")
        if isinstance(raw_keywords, list):
            keywords = [str(item).strip() for item in raw_keywords if str(item).strip()]
        else:
            keywords = []

        summary = str(data.get("summary") or "").strip()
        if not summary:
            summary = self._make_summary(text)

        return {"emotion": emotion, "keywords": keywords, "summary": summary}

    def _fallback_result(self, text: str) -> dict:
        lowered = text.lower()
        if any(token in lowered for token in ["happy", "grateful", "excited", "joy"]):
            emotion = "positive"
        elif any(token in lowered for token in ["sad", "down", "tired", "upset"]):
            emotion = "sad"
        elif any(token in lowered for token in ["anxious", "nervous", "worried", "stress"]):
            emotion = "anxious"
        else:
            emotion = "neutral"

        words = re.findall(r"[a-zA-Z]{4,}", text.lower())
        seen = set()
        keywords = []
        for word in words:
            if word in seen:
                continue
            seen.add(word)
            keywords.append(word)
            if len(keywords) == 5:
                break

        return {
            "emotion": emotion,
            "keywords": keywords,
            "summary": self._make_summary(text),
        }

    def _make_summary(self, text: str) -> str:
        trimmed = " ".join(text.split())
        if len(trimmed) <= 140:
            return trimmed
        return f"{trimmed[:137]}..."
