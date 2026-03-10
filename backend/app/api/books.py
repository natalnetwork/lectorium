from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, status

from backend.app.services import library, progress, storage

router = APIRouter()


@router.get("/api/books")
def get_books() -> list[dict[str, Any]]:
    return library.get_books_summary()


@router.get("/api/books/{book_id}")
def get_book(book_id: str) -> dict[str, Any]:
    book: dict[str, Any] | None = library.get_book(book_id)
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )
    return book


@router.post("/api/books/{book_id}/progress")
def save_book_progress(book_id: str, payload: dict[str, Any]) -> dict[str, str]:
    chapter_index = int(payload.get("chapter_index", 0))
    position = int(payload.get("position", 0))
    progress.save_progress(book_id, chapter_index=chapter_index, position=position)
    return {"status": "ok"}


@router.get("/api/books/{book_id}/progress")
def get_book_progress(book_id: str) -> dict[str, int]:
    return progress.get_progress(book_id)


@router.delete("/api/books/{book_id}")
def delete_book(book_id: str) -> dict[str, str]:
    removed = library.delete_book(book_id)
    if removed is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )

    storage.delete_book_file(book_id)
    progress.delete_progress(book_id)
    return {"status": "deleted"}
