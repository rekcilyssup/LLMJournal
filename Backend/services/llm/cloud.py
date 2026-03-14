import asyncio

import httpx

from core.config import settings
from services.llm.base import BaseLLMService


class CloudLLMService(BaseLLMService):
    def __init__(self) -> None:
        self.base_url = settings.cloud_llm_base_url.rstrip("/")
        self.model = settings.cloud_llm_model
        self.api_key = settings.cloud_llm_api_key
        self.timeout = settings.cloud_llm_timeout_seconds
        self.max_retries = max(settings.cloud_llm_max_retries, 0)

    async def analyze_emotion(self, text: str) -> dict:
        if not self.api_key:
            return self._heuristic_result(text)

        prompt = (
            "Analyze the journal text and return strict JSON only with keys: "
            'emotion (string), keywords (string array), summary (string).\n'
            "Do not include markdown fences or extra explanations."
        )
        payload = {
            "model": self.model,
            "temperature": 0.2,
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": text},
            ],
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        endpoint = f"{self.base_url}/chat/completions"
        for attempt in range(self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(endpoint, headers=headers, json=payload)
                    response.raise_for_status()
                    body = response.json()
                    raw = body["choices"][0]["message"]["content"]
                    parsed = self._extract_json(raw)
                    return self._normalize_result(parsed, text)
            except Exception:
                if attempt < self.max_retries:
                    await asyncio.sleep(0.5 * (attempt + 1))
                    continue
                return self._heuristic_result(text)

        return self._heuristic_result(text)
