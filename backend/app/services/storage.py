from __future__ import annotations

import shutil
import uuid
from pathlib import Path

from fastapi import UploadFile

BASE_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = BASE_DIR / "data"
BOOKS_DIR = DATA_DIR / "books"


def ensure_dirs() -> None:
    BOOKS_DIR.mkdir(parents=True, exist_ok=True)


def save_upload(file: UploadFile) -> tuple[str, Path]:
    ensure_dirs()

    book_id = str(uuid.uuid4())
    target_path = BOOKS_DIR / f"{book_id}.epub"

    with target_path.open("wb") as out:
        shutil.copyfileobj(file.file, out)

    return book_id, target_path
