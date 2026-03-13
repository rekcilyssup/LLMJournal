from abc import ABC, abstractmethod


class BaseLLMService(ABC):
    @abstractmethod
    async def analyze_emotion(self, text: str) -> dict:
        """Return a dict with exactly: emotion, keywords, summary."""
        raise NotImplementedError
