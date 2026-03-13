from functools import lru_cache

from core.config import settings
from services.llm.base import BaseLLMService
from services.llm.cloud import CloudLLMService
from services.llm.local import LocalLLMService


@lru_cache(maxsize=1)
def _local_service() -> LocalLLMService:
    return LocalLLMService()


@lru_cache(maxsize=1)
def _cloud_service() -> CloudLLMService:
    return CloudLLMService()


def get_llm_service() -> BaseLLMService:
    if settings.llm_provider == "cloud":
        return _cloud_service()
    return _local_service()
