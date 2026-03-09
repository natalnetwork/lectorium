from __future__ import annotations

from pydantic import BaseModel, Field


class Chapter(BaseModel):
    title: str
    html_content: str


class Book(BaseModel):
    id: str
    title: str
    author: str
    language: str = "unknown"
    cover_url: str | None = None
    chapters: list[Chapter] = Field(default_factory=list)
