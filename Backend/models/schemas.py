from pydantic import BaseModel, ConfigDict, Field


class JournalEntryCreate(BaseModel):
    userId: str = Field(min_length=1)
    ambience: str = Field(min_length=1)
    text: str = Field(min_length=1)


class JournalEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    userId: str
    ambience: str
    text: str
    date: str
    emotion: str | None = None
    keywords: list[str] | None = None
    summary: str | None = None


class AnalysisRequest(BaseModel):
    text: str = Field(min_length=1)


class AnalysisResult(BaseModel):
    emotion: str
    keywords: list[str]
    summary: str


class Insights(BaseModel):
    totalEntries: int
    topEmotion: str
    mostUsedAmbience: str
    recentKeywords: list[str]


class TimelineMentalStateInsights(BaseModel):
    entryCount: int
    fromDate: str
    toDate: str
    emotion: str
    keywords: list[str]
    summary: str
