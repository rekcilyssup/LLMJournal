from fastapi import APIRouter, Depends, HTTPException
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
    entries = JournalService.get_history_chronological(db, userId)
    if not entries:
        raise HTTPException(status_code=400, detail="No entries available for timeline analysis")

    timeline_input = JournalService.build_timeline_analysis_input(entries)
    llm_result = await llm_service.analyze_emotion(timeline_input)
    if not all(key in llm_result for key in ("emotion", "keywords", "summary")):
        raise HTTPException(status_code=502, detail="LLM provider returned invalid schema")

    raw_keywords = llm_result.get("keywords")
    keywords = [str(item).strip() for item in raw_keywords if str(item).strip()] if isinstance(raw_keywords, list) else []
    emotion = str(llm_result.get("emotion", "neutral")).strip() or "neutral"

    summary = str(llm_result.get("summary", "")).strip()
    if _looks_like_prompt_echo(summary, timeline_input):
        summary = _build_timeline_summary(len(entries), emotion, keywords)

    return TimelineMentalStateInsights(
        entryCount=len(entries),
        fromDate=entries[0].date,
        toDate=entries[-1].date,
        emotion=emotion,
        keywords=keywords,
        summary=summary,
    )


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


def _build_timeline_summary(entry_count: int, emotion: str, keywords: list[str]) -> str:
    if keywords:
        themes = ", ".join(keywords[:4])
        return (
            f"Across {entry_count} entries, the overall emotional trend appears {emotion}. "
            f"Recurring themes include {themes}."
        )

    return f"Across {entry_count} entries, the overall emotional trend appears {emotion}."


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
def get_journal_history(userId: str, db: Session = Depends(get_db)) -> list[JournalEntry]:
    return JournalService.get_history(db, userId)
