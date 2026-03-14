import json
from datetime import timezone

from sqlalchemy import desc, func, or_, select
from sqlalchemy.orm import Session

from models.db_models import JournalEntryDB
from models.schemas import Insights, JournalEntry, JournalEntryCreate


class JournalService:
    @staticmethod
    def create_entry(
        db: Session,
        payload: JournalEntryCreate,
        emotion: str | None = None,
        keywords: list[str] | None = None,
        summary: str | None = None,
    ) -> JournalEntry:
        entry = JournalEntryDB(
            user_id=payload.userId,
            ambience=payload.ambience,
            text=payload.text,
            emotion=emotion,
            keywords_json=json.dumps(keywords) if keywords is not None else None,
            summary=summary,
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
    def get_history_chronological(db: Session, user_id: str) -> list[JournalEntry]:
        stmt = (
            select(JournalEntryDB)
            .where(JournalEntryDB.user_id == user_id)
            .order_by(JournalEntryDB.date.asc())
        )
        rows = db.execute(stmt).scalars().all()
        return [JournalService._to_schema(row) for row in rows]

    @staticmethod
    def get_timeline_analysis_rows(db: Session, user_id: str) -> list[dict[str, str | list[str]]]:
        """Fetch only timeline fields equivalent to: select date, emotion, keywords_json from journal_entries."""
        stmt = (
            select(JournalEntryDB.date, JournalEntryDB.emotion, JournalEntryDB.keywords_json)
            .where(JournalEntryDB.user_id == user_id)
            .order_by(JournalEntryDB.date.asc())
        )
        rows = db.execute(stmt).all()

        timeline_rows: list[dict[str, str | list[str]]] = []
        for date_value, emotion_value, keywords_json in rows:
            parsed_keywords: list[str] = []
            if keywords_json:
                try:
                    raw = json.loads(keywords_json)
                    if isinstance(raw, list):
                        parsed_keywords = [str(item).strip() for item in raw if str(item).strip()]
                except json.JSONDecodeError:
                    parsed_keywords = []

            date_iso = date_value
            if date_iso.tzinfo is None:
                date_iso = date_iso.replace(tzinfo=timezone.utc)

            timeline_rows.append(
                {
                    "date": date_iso.isoformat(),
                    "emotion": (emotion_value or "unknown").strip() if isinstance(emotion_value, str) else "unknown",
                    "keywords": parsed_keywords,
                }
            )

        return timeline_rows

    @staticmethod
    def build_timeline_analysis_input(rows: list[dict[str, str | list[str]]]) -> str:
        lines = [
            "Return strict JSON with keys: emotion (string), keywords (string array), summary (string).",
            "Analyze the emotional progression across these journal entries over time.",
            "Describe how feelings change from earlier to recent entries, possible triggers, and patterns.",
            "Write one clear paragraph with a brief supportive suggestion.",
            "In the summary, reference timing naturally using month/day labels like 'on March 12' or 'by March 14'.",
            "Do not return arrays, object-like text, quoted keys, or bullet points in emotion/summary.",
            "Entries:",
        ]

        for row in rows:
            keywords_value = row.get("keywords")
            keywords = ", ".join(keywords_value) if isinstance(keywords_value, list) and keywords_value else "none"
            date_value = str(row.get("date", ""))
            emotion = str(row.get("emotion", "unknown"))
            display_date = date_value
            try:
                display_date = date_value.split("T", 1)[0]
                year, month, day = display_date.split("-")
                month_name = [
                    "January",
                    "February",
                    "March",
                    "April",
                    "May",
                    "June",
                    "July",
                    "August",
                    "September",
                    "October",
                    "November",
                    "December",
                ][int(month) - 1]
                display_date = f"{month_name} {int(day)}, {year}"
            except Exception:
                pass

            lines.append(
                f"- date={date_value} ({display_date}); emotion={emotion}; keywords={keywords}"
            )

        return "\n".join(lines)

    @staticmethod
    def search_history(db: Session, user_id: str, query: str) -> list[JournalEntry]:
        normalized = query.strip()
        if not normalized:
            return JournalService.get_history(db, user_id)

        like_query = f"%{normalized}%"
        stmt = (
            select(JournalEntryDB)
            .where(
                JournalEntryDB.user_id == user_id,
                or_(
                    JournalEntryDB.text.ilike(like_query),
                    JournalEntryDB.emotion.ilike(like_query),
                    JournalEntryDB.summary.ilike(like_query),
                    JournalEntryDB.keywords_json.ilike(like_query),
                ),
            )
            .order_by(desc(JournalEntryDB.date))
        )
        rows = db.execute(stmt).scalars().all()
        return [JournalService._to_schema(row) for row in rows]

    @staticmethod
    def delete_entry(db: Session, user_id: str, entry_id: str) -> bool:
        stmt = select(JournalEntryDB).where(
            JournalEntryDB.id == entry_id,
            JournalEntryDB.user_id == user_id,
        )
        row = db.execute(stmt).scalar_one_or_none()
        if not row:
            return False

        db.delete(row)
        db.commit()
        return True

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
