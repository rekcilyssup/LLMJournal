import ast
from collections import Counter
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core.database import get_db
from models.schemas import (
    AnalysisRequest,
    AnalysisResult,
    Insights,
    JournalEntry,
    JournalEntryCreate,
    TimelineMentalStateInsights,
)
from services.dependencies import get_llm_service
from services.journal_service import JournalService
from services.llm.base import BaseLLMService

router = APIRouter(prefix="/api/journal", tags=["journal"])


@router.post("/analyze", response_model=AnalysisResult)
async def analyze_text(
    payload: AnalysisRequest,
    llm_service: BaseLLMService = Depends(get_llm_service),
) -> AnalysisResult:
    result = await llm_service.analyze_emotion(payload.text)
    if not all(key in result for key in ("emotion", "keywords", "summary")):
        raise HTTPException(status_code=502, detail="LLM provider returned invalid schema")

    keywords = result.get("keywords")
    if not isinstance(keywords, list):
        keywords = []

    return AnalysisResult(
        emotion=str(result.get("emotion", "neutral")),
        keywords=[str(item) for item in keywords],
        summary=str(result.get("summary", "")),
    )


@router.get("/insights/{userId}", response_model=Insights)
def get_user_insights(userId: str, db: Session = Depends(get_db)) -> Insights:
    return JournalService.get_insights(db, userId)


@router.post("/insights/{userId}/analyze-timeline", response_model=TimelineMentalStateInsights)
async def analyze_user_timeline(
    userId: str,
    db: Session = Depends(get_db),
    llm_service: BaseLLMService = Depends(get_llm_service),
) -> TimelineMentalStateInsights:
    timeline_rows = JournalService.get_timeline_analysis_rows(db, userId)
    if not timeline_rows:
        raise HTTPException(status_code=400, detail="No entries available for timeline analysis")

    timeline_input = JournalService.build_timeline_analysis_input(timeline_rows)
    llm_result = await llm_service.analyze_emotion(timeline_input)
    if not all(key in llm_result for key in ("emotion", "keywords", "summary")):
        raise HTTPException(status_code=502, detail="LLM provider returned invalid schema")

    keywords = _normalize_keywords(llm_result.get("keywords"))
    emotion = _normalize_emotion(llm_result.get("emotion"), timeline_rows)
    if not keywords:
        keywords = _derive_keywords_from_rows(timeline_rows)

    derived_trend = _derive_trend_from_rows(timeline_rows)
    if emotion.lower() in {"neutral", "unknown", ""} and derived_trend != "neutral":
        emotion = derived_trend

    summary = _normalize_summary(llm_result.get("summary"), timeline_rows)
    if _looks_like_prompt_echo(summary, timeline_input):
        summary = _build_timeline_summary(timeline_rows, emotion, keywords)

    return TimelineMentalStateInsights(
        entryCount=len(timeline_rows),
        fromDate=str(timeline_rows[0]["date"]),
        toDate=str(timeline_rows[-1]["date"]),
        emotion=emotion,
        keywords=keywords,
        summary=summary,
    )


@router.post("", response_model=JournalEntry, status_code=201)
async def save_journal_entry(
    payload: JournalEntryCreate,
    db: Session = Depends(get_db),
    llm_service: BaseLLMService = Depends(get_llm_service),
) -> JournalEntry:
    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="Text is required")

    llm_result = await llm_service.analyze_emotion(payload.text)
    if not all(key in llm_result for key in ("emotion", "keywords", "summary")):
        raise HTTPException(status_code=502, detail="LLM provider returned invalid schema")

    raw_keywords = llm_result.get("keywords")
    keywords = [str(item).strip() for item in raw_keywords if str(item).strip()] if isinstance(raw_keywords, list) else []

    return JournalService.create_entry(
        db,
        payload,
        emotion=str(llm_result.get("emotion", "neutral")).strip() or "neutral",
        keywords=keywords,
        summary=str(llm_result.get("summary", "")).strip(),
    )


@router.get("/{userId}", response_model=list[JournalEntry])
def get_journal_history(
    userId: str,
    q: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[JournalEntry]:
    if q is not None:
        return JournalService.search_history(db, userId, q)
    return JournalService.get_history(db, userId)


@router.delete("/{userId}/{entryId}")
def delete_journal_entry(userId: str, entryId: str, db: Session = Depends(get_db)) -> dict[str, str]:
    deleted = JournalService.delete_entry(db, userId, entryId)
    if not deleted:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {"message": "Entry deleted successfully"}


def _looks_like_prompt_echo(summary: str, timeline_input: str) -> bool:
    if not summary:
        return True

    normalized_summary = " ".join(summary.lower().split())
    normalized_input = " ".join(timeline_input.lower().split())

    suspicious_markers = (
        "analyze this user's mental state over time",
        "analyze the journal text and return strict json",
        "entries:",
    )
    if any(marker in normalized_summary for marker in suspicious_markers):
        return True

    if normalized_input.startswith(normalized_summary[:80]):
        return True

    return False


def _build_timeline_summary(
    timeline_rows: list[dict[str, str | list[str]]],
    emotion: str,
    keywords: list[str],
) -> str:
    entry_count = len(timeline_rows)
    start_label = _format_date_label(str(timeline_rows[0].get("date", "")))
    end_label = _format_date_label(str(timeline_rows[-1].get("date", "")))

    if keywords:
        themes = ", ".join(keywords[:4])
        return (
            f"From {start_label} to {end_label} across {entry_count} entries, the overall emotional pattern appears {emotion}. "
            f"Recurring themes include {themes}. A helpful next step is a short daily check-in to notice early stress signals and protect momentum."
        )

    return (
        f"From {start_label} to {end_label} across {entry_count} entries, the overall emotional pattern appears {emotion}. "
        "A helpful next step is a short daily check-in to notice shifts earlier and respond with small, supportive adjustments."
    )


def _normalize_keywords(value: object) -> list[str]:
    if not isinstance(value, list):
        return []

    normalized: list[str] = []
    for item in value:
        if isinstance(item, list):
            joined = ", ".join(str(part).strip() for part in item if str(part).strip())
            if joined:
                normalized.append(joined)
            continue

        text = str(item).strip()
        if text:
            normalized.append(text)

    return normalized


def _normalize_emotion(value: object, timeline_rows: list[dict[str, str | list[str]]]) -> str:
    if isinstance(value, str):
        raw = value.strip()
        if raw.startswith("[") and raw.endswith("]"):
            try:
                parsed = ast.literal_eval(raw)
                if isinstance(parsed, list) and parsed:
                    return str(parsed[-1]).strip() or "neutral"
            except Exception:
                pass
        return raw or "neutral"

    if isinstance(value, list) and value:
        return str(value[-1]).strip() or "neutral"

    # Fall back to the most recent stored emotion from timeline rows.
    if timeline_rows:
        recent = str(timeline_rows[-1].get("emotion", "neutral")).strip()
        if recent:
            return recent

    return "neutral"


def _normalize_summary(value: object, timeline_rows: list[dict[str, str | list[str]]]) -> str:
    if isinstance(value, str):
        summary = value.strip()
        if summary.startswith("[") and summary.endswith("]"):
            try:
                parsed = ast.literal_eval(summary)
                if isinstance(parsed, list):
                    cleaned_parts = [str(item).strip() for item in parsed if str(item).strip()]
                    if cleaned_parts:
                        return " ".join(cleaned_parts)
            except Exception:
                pass
        return summary

    if isinstance(value, list):
        cleaned_parts = [str(item).strip() for item in value if str(item).strip()]
        if cleaned_parts:
            return " ".join(cleaned_parts)

    # Last-resort readable fallback with timing references.
    if timeline_rows:
        first_date = str(timeline_rows[0].get("date", "")).split("T", 1)[0]
        last_date = str(timeline_rows[-1].get("date", "")).split("T", 1)[0]
        return (
            f"From {first_date} to {last_date}, your emotional pattern shows meaningful changes over time, "
            "with recurring themes visible in your keywords; continue using small reflective check-ins to stay grounded."
        )

    return ""


def _derive_keywords_from_rows(timeline_rows: list[dict[str, str | list[str]]]) -> list[str]:
    seen: set[str] = set()
    keywords: list[str] = []
    for row in timeline_rows:
        raw = row.get("keywords")
        if not isinstance(raw, list):
            continue
        for item in raw:
            word = str(item).strip()
            if not word:
                continue
            lowered = word.lower()
            if lowered in seen:
                continue
            seen.add(lowered)
            keywords.append(word)
            if len(keywords) >= 6:
                return keywords
    return keywords


def _derive_trend_from_rows(timeline_rows: list[dict[str, str | list[str]]]) -> str:
    emotions: list[str] = []
    for row in timeline_rows:
        raw = str(row.get("emotion", "")).strip().lower()
        if raw and raw != "unknown":
            emotions.append(raw)

    if not emotions:
        return "neutral"

    if len(set(emotions)) >= 2:
        return "mixed"

    counts = Counter(emotions)
    return counts.most_common(1)[0][0]


def _format_date_label(value: str) -> str:
    if not value:
        return "the period"
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.strftime("%B %-d")
    except Exception:
        return value.split("T", 1)[0]
