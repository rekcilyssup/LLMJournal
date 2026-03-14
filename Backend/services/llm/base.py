from abc import ABC, abstractmethod
import json
import re


class BaseLLMService(ABC):
    @abstractmethod
    async def analyze_emotion(self, text: str) -> dict:
        """Return a dict with exactly: emotion, keywords, summary."""
        raise NotImplementedError

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
                if all(key in obj for key in ("emotion", "keywords", "summary")):
                    return obj
            except json.JSONDecodeError:
                continue

        cleaned = re.sub(r"```[a-zA-Z0-9_]*|```", "", raw).strip()
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                obj = json.loads(cleaned[start : end + 1])
                if all(key in obj for key in ("emotion", "keywords", "summary")):
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

    def _heuristic_result(self, text: str) -> dict:
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
        seen: set[str] = set()
        keywords: list[str] = []
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
