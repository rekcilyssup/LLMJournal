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

    keywords = JournalService.normalize_keywords(llm_result.get("keywords"))
    emotion = JournalService.normalize_emotion(llm_result.get("emotion"), timeline_rows)
    if not keywords:
        keywords = JournalService.derive_keywords_from_rows(timeline_rows)

    derived_trend = JournalService.derive_trend_from_rows(timeline_rows)
    if emotion.lower() in {"neutral", "unknown", ""} and derived_trend != "neutral":
        emotion = derived_trend

    summary = JournalService.normalize_summary(llm_result.get("summary"), timeline_rows)
    if JournalService.looks_like_prompt_echo(summary, timeline_input):
        summary = JournalService.build_timeline_summary(timeline_rows, emotion, keywords)

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
