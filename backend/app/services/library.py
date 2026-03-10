from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from backend.app.models.book import Book

BASE_DIR: Path = Path(__file__).resolve().parents[3]
DATA_DIR: Path = BASE_DIR / "data"
DB_DIR: Path = DATA_DIR / "db"
COVERS_DIR: Path = DATA_DIR / "covers"
LIBRARY_PATH: Path = DB_DIR / "library.json"


def ensure_dirs() -> None:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    COVERS_DIR.mkdir(parents=True, exist_ok=True)


def _ensure_library_file() -> None:
    ensure_dirs()
    if not LIBRARY_PATH.exists():
        LIBRARY_PATH.write_text(
            json.dumps({"books": []}, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )


def _load_library() -> dict[str, Any]:
    _ensure_library_file()
    return json.loads(LIBRARY_PATH.read_text(encoding="utf-8"))


def _save_library(payload: dict[str, Any]) -> None:
    ensure_dirs()
    LIBRARY_PATH.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def save_cover_bytes(book_id: str, content: bytes, extension: str) -> str:
    ensure_dirs()
    ext: str = extension if extension.startswith(".") else f".{extension}"
    target: Path = COVERS_DIR / f"{book_id}{ext}"
    target.write_bytes(content)
    return f"/covers/{target.name}"


def upsert_book(book: Book) -> None:
    payload: dict[str, Any] = _load_library()
    books: list[dict[str, Any]] = payload.get("books", [])

    new_entry: dict[str, Any] = book.model_dump()

    replaced = False
    for index, existing in enumerate(books):
        if existing.get("id") == book.id:
            books[index] = new_entry
            replaced = True
            break

    if not replaced:
        books.append(new_entry)

    payload["books"] = books
    _save_library(payload)


def get_books() -> list[dict[str, Any]]:
    payload: dict[str, Any] = _load_library()
    books = payload.get("books", [])
    if isinstance(books, list):
        return books
    return []


def get_books_summary() -> list[dict[str, Any]]:
    books: list[dict[str, Any]] = get_books()
    result: list[dict[str, Any]] = []

    for book in books:
        result.append(
            {
                "id": book.get("id"),
                "title": book.get("title"),
                "author": book.get("author"),
                "cover_url": book.get("cover_url"),
            }
        )

    return result


def get_book(book_id: str) -> dict[str, Any] | None:
    books: list[dict[str, Any]] = get_books()
    for book in books:
        if book.get("id") == book_id:
            return book
    return None


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
    payload: dict[str, Any] = _load_library()
    books: list[dict[str, Any]] = payload.get("books", [])

    if not isinstance(books, list):
        return None

    removed: dict[str, Any] | None = None
    remaining: list[dict[str, Any]] = []

    for book in books:
        if book.get("id") == book_id:
            removed = book
        else:
            remaining.append(book)

    if removed is None:
        return None

    payload["books"] = remaining
    _save_library(payload)
    _delete_cover_file(removed.get("cover_url"))
    return removed
