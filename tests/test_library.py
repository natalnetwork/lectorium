from __future__ import annotations

from pathlib import Path

import pytest
from _pytest.monkeypatch import MonkeyPatch
from ebooklib import epub
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from backend.app import database
from backend.app.database import Base
from backend.app.models import db_models as _  # noqa: F401 – register ORM classes


@pytest.fixture(autouse=True)
def in_memory_db(monkeypatch: MonkeyPatch) -> None:
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(test_engine)
    monkeypatch.setattr(database, "engine", test_engine)


def _make_epub(path: Path) -> None:
    book = epub.EpubBook()
    book.set_title("Sample")  # type: ignore[reportUnknownMemberType]
    book.add_author("Author")  # type: ignore[reportUnknownMemberType]

    chapter = epub.EpubHtml(
        title="Intro",
        file_name="intro.xhtml",
        content="<p>Hello</p>",
    )
    book.add_item(chapter)  # type: ignore[reportUnknownMemberType]

    book.toc = (chapter,)  # type: ignore[reportUnknownMemberType]
    book.spine = ["nav", chapter]
    book.add_item(epub.EpubNcx())  # type: ignore[reportUnknownMemberType]
    book.add_item(epub.EpubNav())  # type: ignore[reportUnknownMemberType]

    epub.write_epub(str(path), book)  # type: ignore[reportUnknownMemberType]


def _auth_headers(client: TestClient, username: str = "alice", password: str = "secret") -> dict[str, str]:
    """Register (or login if already exists) and return auth headers."""
    response = client.post("/auth/register", json={"username": username, "password": password})
    if response.status_code == 409:
        response = client.post("/auth/login", json={"username": username, "password": password})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_upload_and_library_flow(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    from backend.app import main
    from backend.app.services import library, storage

    monkeypatch.setattr(storage, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(library, "COVERS_DIR", tmp_path / "covers")

    sample_path = tmp_path / "sample.epub"
    _make_epub(sample_path)

    client = TestClient(main.app)
    headers = _auth_headers(client)

    with sample_path.open("rb") as handle:
        response = client.post(
            "/upload",
            headers=headers,
            files={"file": ("sample.epub", handle, "application/epub+zip")},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["title"] == "Sample"

    list_response = client.get("/api/books", headers=headers)
    assert list_response.status_code == 200
    books = list_response.json()
    assert len(books) == 1

    book_id = books[0]["id"]
    book_response = client.get(f"/api/books/{book_id}", headers=headers)
    assert book_response.status_code == 200
    book = book_response.json()
    assert book["chapters"]

    progress_response = client.post(
        f"/api/books/{book_id}/progress",
        headers=headers,
        json={"chapter_index": 1, "position": 0},
    )
    assert progress_response.status_code == 200

    progress_get = client.get(f"/api/books/{book_id}/progress", headers=headers)
    assert progress_get.status_code == 200
    assert progress_get.json()["chapter_index"] == 1


def test_library_isolation(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    """Books uploaded by user A must not be visible to user B."""
    from backend.app import main
    from backend.app.services import library, storage

    monkeypatch.setattr(storage, "BOOKS_DIR", tmp_path / "books")
    monkeypatch.setattr(library, "COVERS_DIR", tmp_path / "covers")

    sample_path = tmp_path / "sample.epub"
    _make_epub(sample_path)

    client = TestClient(main.app)
    headers_a = _auth_headers(client, "alice", "pw1")
    headers_b = _auth_headers(client, "bob", "pw2")

    with sample_path.open("rb") as handle:
        client.post(
            "/upload",
            headers=headers_a,
            files={"file": ("sample.epub", handle, "application/epub+zip")},
        )

    books_a = client.get("/api/books", headers=headers_a).json()
    books_b = client.get("/api/books", headers=headers_b).json()

    assert len(books_a) == 1
    assert len(books_b) == 0
