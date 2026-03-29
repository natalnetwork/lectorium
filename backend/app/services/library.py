from __future__ import annotations

from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from backend.app import database
from backend.app.models.book import Book
from backend.app.models.db_models import BookRow, ChapterRow

BASE_DIR: Path = Path(__file__).resolve().parents[3]
DATA_DIR: Path = BASE_DIR / "data"
COVERS_DIR: Path = DATA_DIR / "covers"


def save_cover_bytes(book_id: str, content: bytes, extension: str) -> str:
    COVERS_DIR.mkdir(parents=True, exist_ok=True)
    ext: str = extension if extension.startswith(".") else f".{extension}"
    target: Path = COVERS_DIR / f"{book_id}{ext}"
    target.write_bytes(content)
    return f"/covers/{target.name}"


def upsert_book(book: Book) -> None:
    with Session(database.engine) as session:
        existing = session.get(BookRow, book.id)
        if existing is not None:
            existing.title = book.title
            existing.author = book.author
            existing.language = book.language
            existing.cover_url = book.cover_url
            for ch in list(existing.chapters):
                session.delete(ch)
            session.flush()
        else:
            existing = BookRow(
                id=book.id,
                title=book.title,
                author=book.author,
                language=book.language,
                cover_url=book.cover_url,
            )
            session.add(existing)

        for i, chapter in enumerate(book.chapters):
            session.add(
                ChapterRow(
                    book_id=book.id,
                    position=i,
                    title=chapter.title,
                    html_content=chapter.html_content,
                )
            )

        session.commit()


def get_books_summary() -> list[dict[str, Any]]:
    with Session(database.engine) as session:
        rows = session.query(BookRow).all()
        return [
            {
                "id": row.id,
                "title": row.title,
                "author": row.author,
                "cover_url": row.cover_url,
            }
            for row in rows
        ]


def get_book(book_id: str) -> dict[str, Any] | None:
    with Session(database.engine) as session:
        row = session.get(BookRow, book_id)
        if row is None:
            return None
        return _book_to_dict(row)


def _book_to_dict(row: BookRow) -> dict[str, Any]:
    return {
        "id": row.id,
        "title": row.title,
        "author": row.author,
        "language": row.language,
        "cover_url": row.cover_url,
        "chapters": [
            {"title": ch.title, "html_content": ch.html_content}
            for ch in sorted(row.chapters, key=lambda c: c.position)
        ],
    }


def _delete_cover_file(cover_url: str | None) -> None:
    if not cover_url:
        return
    if not cover_url.startswith("/covers/"):
        return
    filename = Path(cover_url).name
    if not filename:
        return
    target = COVERS_DIR / filename
    if target.exists():
        target.unlink()


def delete_book(book_id: str) -> dict[str, Any] | None:
    with Session(database.engine) as session:
        row = session.get(BookRow, book_id)
        if row is None:
            return None
        result = _book_to_dict(row)
        session.delete(row)
        session.commit()
    _delete_cover_file(result.get("cover_url"))
    return result
