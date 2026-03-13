from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.database import get_db
from models.schemas import AnalysisRequest, AnalysisResult, Insights, JournalEntry, JournalEntryCreate
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


@router.post("", response_model=JournalEntry, status_code=201)
def save_journal_entry(
    payload: JournalEntryCreate,
    db: Session = Depends(get_db),
) -> JournalEntry:
    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="Text is required")
    return JournalService.create_entry(db, payload)


@router.get("/{userId}", response_model=list[JournalEntry])
def get_journal_history(userId: str, db: Session = Depends(get_db)) -> list[JournalEntry]:
    return JournalService.get_history(db, userId)
