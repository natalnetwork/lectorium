from __future__ import annotations

import shutil
import uuid
from pathlib import Path

from fastapi import UploadFile

BASE_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = BASE_DIR / "data"
BOOKS_DIR = DATA_DIR / "books"
BOOK_ASSETS_DIR = DATA_DIR / "book-assets"


def ensure_dirs() -> None:
    BOOKS_DIR.mkdir(parents=True, exist_ok=True)
    BOOK_ASSETS_DIR.mkdir(parents=True, exist_ok=True)


def save_upload(file: UploadFile) -> tuple[str, Path]:
    ensure_dirs()

    book_id = str(uuid.uuid4())
    target_path = BOOKS_DIR / f"{book_id}.epub"

    with target_path.open("wb") as out:
        shutil.copyfileobj(file.file, out)

    return book_id, target_path


def save_book_asset(book_id: str, filename: str, content: bytes) -> str:
    ensure_dirs()
    safe_name = Path(filename).name
    target_dir = BOOK_ASSETS_DIR / book_id
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / safe_name
    target_path.write_bytes(content)
    return f"/book-assets/{book_id}/{safe_name}"


def delete_book_file(book_id: str) -> bool:
    target_path = BOOKS_DIR / f"{book_id}.epub"
    if target_path.exists():
        target_path.unlink()
        return True
    return False
