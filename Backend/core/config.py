import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    database_url: str
    llm_provider: str
    local_llm_base_url: str
    local_llm_model: str
    cloud_llm_base_url: str
    cloud_llm_model: str
    cloud_llm_api_key: str
    cloud_llm_timeout_seconds: float
    cloud_llm_max_retries: int
    backend_cors_origins: list[str]
    backend_cors_origin_regex: Optional[str]



def _parse_cors_origins(raw: str) -> list[str]:
    values = [item.strip() for item in raw.split(",") if item.strip()]
    return values or ["http://localhost:3000"]


def _parse_float(raw: str, default: float) -> float:
    try:
        return float(raw)
    except (TypeError, ValueError):
        return default


def _parse_int(raw: str, default: int) -> int:
    try:
        return int(raw)
    except (TypeError, ValueError):
        return default


settings = Settings(
    database_url=os.getenv("DATABASE_URL", "sqlite:///./journal.db"),
    llm_provider=os.getenv("LLM_PROVIDER", "local").strip().lower(),
    local_llm_base_url=os.getenv("LOCAL_LLM_BASE_URL", "http://localhost:1234/v1").strip(),
    local_llm_model=os.getenv("LOCAL_LLM_MODEL", "local-model").strip(),
    cloud_llm_base_url=os.getenv("CLOUD_LLM_BASE_URL", "https://api.openai.com/v1").strip(),
    cloud_llm_model=os.getenv("CLOUD_LLM_MODEL", "gpt-4o-mini").strip(),
    cloud_llm_api_key=os.getenv("CLOUD_LLM_API_KEY", "").strip(),
    cloud_llm_timeout_seconds=_parse_float(os.getenv("CLOUD_LLM_TIMEOUT_SECONDS", "30"), 30.0),
    cloud_llm_max_retries=_parse_int(os.getenv("CLOUD_LLM_MAX_RETRIES", "2"), 2),
    backend_cors_origins=_parse_cors_origins(
        os.getenv("BACKEND_CORS_ORIGINS", "http://localhost:3000")
    ),
    backend_cors_origin_regex=(
        os.getenv(
            "BACKEND_CORS_ORIGIN_REGEX",
            r"^https?://(localhost|127\.0\.0\.1|0\.0\.0\.0|192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+|172\.(1[6-9]|2\d|3[0-1])\.\d+\.\d+):300[0-9]$",
        ).strip()
        or None
    ),
)
