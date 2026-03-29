from __future__ import annotations

from sqlalchemy.orm import Session

from backend.app import database
from backend.app.models.db_models import ProgressRow


def save_progress(book_id: str, *, chapter_index: int, position: int) -> None:
    with Session(database.engine) as session:
        row = session.get(ProgressRow, book_id)
        if row is None:
            session.add(
                ProgressRow(
                    book_id=book_id,
                    chapter_index=chapter_index,
                    position=position,
                )
            )
        else:
            row.chapter_index = chapter_index
            row.position = position
        session.commit()


def get_progress(book_id: str) -> dict[str, int]:
    with Session(database.engine) as session:
        row = session.get(ProgressRow, book_id)
        if row is None:
            return {"chapter_index": 0, "position": 0}
        return {"chapter_index": row.chapter_index, "position": row.position}


def delete_progress(book_id: str) -> None:
    with Session(database.engine) as session:
        row = session.get(ProgressRow, book_id)
        if row is not None:
            session.delete(row)
            session.commit()
