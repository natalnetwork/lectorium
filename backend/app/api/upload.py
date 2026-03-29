from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from backend.app.api.deps import get_current_user
from backend.app.models.db_models import UserRow
from backend.app.services import epub_parser, library, storage

logger = logging.getLogger(__name__)

router = APIRouter()


class UploadResponse(BaseModel):
    title: str
    author: str
    chapters: int


@router.post("/upload", response_model=None)
def upload_epub(
    file: Annotated[UploadFile, File(...)],
    current_user: UserRow = Depends(get_current_user),
) -> Response:
    filename = file.filename or ""

    if not filename.lower().endswith(".epub"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .epub files are allowed",
        )

    book_id, file_path = storage.save_upload(file)
    book = epub_parser.parse_epub(file_path, book_id=book_id)
    library.upsert_book(book, current_user.id)

    logger.info("Upload processed: %s (%s chapters)", book.title, len(book.chapters))

    payload = UploadResponse(
        title=book.title,
        author=book.author,
        chapters=len(book.chapters),
    )

    return JSONResponse(content=payload.model_dump())
