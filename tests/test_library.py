from __future__ import annotations

from pathlib import Path

from ebooklib import epub
from fastapi.testclient import TestClient

from backend.app import main
from backend.app.services import library, progress, storage


def _make_epub(path: Path) -> None:
    book = epub.EpubBook()
    book.set_title("Sample")
    book.add_author("Author")

    chapter = epub.EpubHtml(title="Intro", file_name="intro.xhtml", content="<p>Hello</p>")
    book.add_item(chapter)

    book.toc = (chapter,)
    book.spine = ["nav", chapter]
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    epub.write_epub(str(path), book)


def test_upload_and_library_flow(tmp_path, monkeypatch) -> None:
    books_dir = tmp_path / "books"
    db_dir = tmp_path / "db"

    monkeypatch.setattr(storage, "BOOKS_DIR", books_dir)
    monkeypatch.setattr(library, "DB_DIR", db_dir)
    monkeypatch.setattr(library, "LIBRARY_PATH", db_dir / "library.json")
    monkeypatch.setattr(progress, "DB_DIR", db_dir)
    monkeypatch.setattr(progress, "PROGRESS_PATH", db_dir / "progress.json")

    sample_path = tmp_path / "sample.epub"
    _make_epub(sample_path)

    client = TestClient(main.app)
    with sample_path.open("rb") as handle:
        response = client.post(
            "/upload",
            files={"file": ("sample.epub", handle, "application/epub+zip")},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["title"] == "Sample"

    list_response = client.get("/api/books")
    assert list_response.status_code == 200
    books = list_response.json()
    assert len(books) == 1

    book_id = books[0]["id"]
    book_response = client.get(f"/api/books/{book_id}")
    assert book_response.status_code == 200
    book = book_response.json()
    assert book["chapters"]

    progress_response = client.post(
        f"/api/books/{book_id}/progress",
        json={"chapter_index": 1, "position": 0},
    )
    assert progress_response.status_code == 200

    progress_get = client.get(f"/api/books/{book_id}/progress")
    assert progress_get.status_code == 200
    assert progress_get.json()["chapter_index"] == 1
