import re

from core.config import settings
from services.llm.base import BaseLLMService


class CloudLLMService(BaseLLMService):
    async def analyze_emotion(self, text: str) -> dict:
        # Stub implementation. Replace this with real OpenAI/Gemini API integration.
        # Keep return schema stable so business logic and API routes do not change.
        if not settings.cloud_llm_api_key:
            return self._stub_result(text)

        # Example placeholder branch for when key exists but implementation is pending.
        return self._stub_result(text)

    def _stub_result(self, text: str) -> dict:
        lowered = text.lower()
        if any(token in lowered for token in ["happy", "grateful", "excited", "joy"]):
            emotion = "positive"
        elif any(token in lowered for token in ["sad", "down", "tired", "upset"]):
            emotion = "sad"
        elif any(token in lowered for token in ["anxious", "nervous", "worried", "stress"]):
            emotion = "anxious"
        else:
            emotion = "neutral"

        keywords = re.findall(r"[a-zA-Z]{4,}", text.lower())[:5]
        summary = " ".join(text.split())
        if len(summary) > 140:
            summary = f"{summary[:137]}..."

        return {"emotion": emotion, "keywords": keywords, "summary": summary}
