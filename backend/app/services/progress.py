from __future__ import annotations

import json
from pathlib import Path
from typing import Any

BASE_DIR: Path = Path(__file__).resolve().parents[3]
DATA_DIR: Path = BASE_DIR / "data"
DB_DIR: Path = DATA_DIR / "db"
PROGRESS_PATH: Path = DB_DIR / "progress.json"


def ensure_dirs() -> None:
    DB_DIR.mkdir(parents=True, exist_ok=True)


def _ensure_progress_file() -> None:
    ensure_dirs()
    if not PROGRESS_PATH.exists():
        PROGRESS_PATH.write_text("{}", encoding="utf-8")


def _load_progress() -> dict[str, Any]:
    _ensure_progress_file()
    return json.loads(PROGRESS_PATH.read_text(encoding="utf-8"))


def _save_progress(payload: dict[str, Any]) -> None:
    ensure_dirs()
    PROGRESS_PATH.write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )


def save_progress(book_id: str, *, chapter_index: int, position: int) -> None:
    payload: dict[str, Any] = _load_progress()
    payload[book_id] = {
        "chapter_index": chapter_index,
        "position": position,
    }
    _save_progress(payload)


def get_progress(book_id: str) -> dict[str, int]:
    payload: dict[str, Any] = _load_progress()
    entry = payload.get(book_id)

    if isinstance(entry, dict):
        return {
            "chapter_index": int(entry.get("chapter_index", 0)),
            "position": int(entry.get("position", 0)),
        }

    return {
        "chapter_index": 0,
        "position": 0,
    }
