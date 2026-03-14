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
            return self._heuristic_result(text)
