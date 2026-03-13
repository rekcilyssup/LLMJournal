import json
from datetime import timezone

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from models.db_models import JournalEntryDB
from models.schemas import Insights, JournalEntry, JournalEntryCreate


class JournalService:
    @staticmethod
    def create_entry(db: Session, payload: JournalEntryCreate) -> JournalEntry:
        entry = JournalEntryDB(
            user_id=payload.userId,
            ambience=payload.ambience,
            text=payload.text,
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return JournalService._to_schema(entry)

    @staticmethod
    def get_history(db: Session, user_id: str) -> list[JournalEntry]:
        stmt = (
            select(JournalEntryDB)
            .where(JournalEntryDB.user_id == user_id)
            .order_by(desc(JournalEntryDB.date))
        )
        rows = db.execute(stmt).scalars().all()
        return [JournalService._to_schema(row) for row in rows]

    @staticmethod
    def get_insights(db: Session, user_id: str) -> Insights:
        total_entries = db.scalar(
            select(func.count(JournalEntryDB.id)).where(JournalEntryDB.user_id == user_id)
        ) or 0

        top_emotion_row = db.execute(
            select(JournalEntryDB.emotion, func.count(JournalEntryDB.id).label("cnt"))
            .where(
                JournalEntryDB.user_id == user_id,
                JournalEntryDB.emotion.is_not(None),
                JournalEntryDB.emotion != "",
            )
            .group_by(JournalEntryDB.emotion)
            .order_by(desc("cnt"))
            .limit(1)
        ).first()
        top_emotion = top_emotion_row[0] if top_emotion_row else ""

        top_ambience_row = db.execute(
            select(JournalEntryDB.ambience, func.count(JournalEntryDB.id).label("cnt"))
            .where(JournalEntryDB.user_id == user_id)
            .group_by(JournalEntryDB.ambience)
            .order_by(desc("cnt"))
            .limit(1)
        ).first()
        top_ambience = top_ambience_row[0] if top_ambience_row else ""

        # Pull only a small recent slice, then derive unique recent keywords.
        keyword_rows = db.execute(
            select(JournalEntryDB.keywords_json)
            .where(
                JournalEntryDB.user_id == user_id,
                JournalEntryDB.keywords_json.is_not(None),
                JournalEntryDB.keywords_json != "",
            )
            .order_by(desc(JournalEntryDB.date))
            .limit(20)
        ).all()

        recent_keywords: list[str] = []
        seen: set[str] = set()
        for (raw_keywords,) in keyword_rows:
            if not raw_keywords:
                continue
            try:
                values = json.loads(raw_keywords)
            except json.JSONDecodeError:
                continue
            if not isinstance(values, list):
                continue
            for item in values:
                word = str(item).strip()
                if not word or word in seen:
                    continue
                seen.add(word)
                recent_keywords.append(word)
                if len(recent_keywords) >= 10:
                    break
            if len(recent_keywords) >= 10:
                break

        return Insights(
            totalEntries=total_entries,
            topEmotion=top_emotion,
            mostUsedAmbience=top_ambience,
            recentKeywords=recent_keywords,
        )

    @staticmethod
    def enrich_entry_analysis(
        db: Session,
        entry_id: str,
        emotion: str,
        keywords: list[str],
        summary: str,
    ) -> None:
        stmt = select(JournalEntryDB).where(JournalEntryDB.id == entry_id)
        row = db.execute(stmt).scalar_one_or_none()
        if not row:
            return
        row.emotion = emotion
        row.keywords_json = json.dumps(keywords)
        row.summary = summary
        db.add(row)
        db.commit()

    @staticmethod
    def _to_schema(row: JournalEntryDB) -> JournalEntry:
        keywords = None
        if row.keywords_json:
            try:
                parsed = json.loads(row.keywords_json)
                if isinstance(parsed, list):
                    keywords = [str(item) for item in parsed]
            except json.JSONDecodeError:
                keywords = None

        date_iso = row.date
        if row.date.tzinfo is None:
            date_iso = row.date.replace(tzinfo=timezone.utc)

        return JournalEntry(
            id=row.id,
            userId=row.user_id,
            ambience=row.ambience,
            text=row.text,
            date=date_iso.isoformat(),
            emotion=row.emotion,
            keywords=keywords,
            summary=row.summary,
        )
