from __future__ import annotations

import re
from pathlib import Path
from typing import Any, cast

from ebooklib import ITEM_DOCUMENT, ITEM_IMAGE, epub

from backend.app.models.book import Book, Chapter
from backend.app.services import library, storage


def _first_author(value: Any) -> str:
    if isinstance(value, list) and value:
        first = value[0]
        if isinstance(first, tuple) and first:
            return str(first[0])
        return str(first)
    return "Unknown author"


def _first_language(value: Any) -> str:
    if isinstance(value, list) and value:
        first = value[0]
        if isinstance(first, tuple) and first:
            return str(first[0])
        return str(first)
    return "unknown"


def parse_epub(file_path: Path, *, book_id: str) -> Book:
    epub_book: Any = epub.read_epub(str(file_path))

    title_meta: Any = epub_book.get_metadata("DC", "title")
    creator_meta: Any = epub_book.get_metadata("DC", "creator")
    language_meta: Any = epub_book.get_metadata("DC", "language")

    title = str(title_meta[0][0]) if title_meta else file_path.stem
    author = _first_author(creator_meta)
    language = _first_language(language_meta)

    chapters: list[Chapter] = []
    cover_url: str | None = None
    image_map: dict[str, str] = {}

    items = list(cast(list[Any], epub_book.get_items()))

    for item in items:
        if (
            item.get_type() == ITEM_IMAGE
            and "cover" in item.get_name().lower()
            and cover_url is None
        ):
            ext = Path(item.get_name()).suffix.lower() or ".jpg"
            cover_url = library.save_cover_bytes(book_id, item.get_content(), ext)

        if item.get_type() == ITEM_IMAGE:
            asset_url = storage.save_book_asset(
                book_id,
                item.get_name(),
                item.get_content(),
            )
            image_map[item.get_name()] = asset_url
            image_map[Path(item.get_name()).name] = asset_url

    for item in items:
        if item.get_type() == ITEM_DOCUMENT:
            html = item.get_content().decode("utf-8", errors="replace")
            html = _rewrite_image_sources(html, image_map)
            chapter_title = getattr(item, "title", None) or Path(item.get_name()).stem
            chapters.append(
                Chapter(
                    title=str(chapter_title),
                    html_content=html,
                )
            )

    return Book(
        id=book_id,
        title=title,
        author=author,
        language=language,
        cover_url=cover_url,
        chapters=chapters,
    )


def _rewrite_image_sources(html: str, image_map: dict[str, str]) -> str:
    if not image_map:
        return html

    def replace(match: re.Match[str]) -> str:
        prefix, src, suffix = match.groups()
        key = Path(src).name
        mapped = image_map.get(src) or image_map.get(key)
        if mapped:
            return f"{prefix}{mapped}{suffix}"
        return match.group(0)

    return re.sub(
        r'(<(?:img|image)[^>]+(?:src|xlink:href|href)=["\'])([^"\']+)(["\'])',
        replace,
        html,
    )
