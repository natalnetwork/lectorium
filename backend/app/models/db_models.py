from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database import Base


class BookRow(Base):
    __tablename__ = "books"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    author: Mapped[str] = mapped_column(String, nullable=False)
    language: Mapped[str] = mapped_column(String, nullable=False, default="unknown")
    cover_url: Mapped[str | None] = mapped_column(String, nullable=True)

    chapters: Mapped[list[ChapterRow]] = relationship(
        "ChapterRow",
        back_populates="book",
        order_by="ChapterRow.position",
        cascade="all, delete-orphan",
    )


class ChapterRow(Base):
    __tablename__ = "chapters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    book_id: Mapped[str] = mapped_column(ForeignKey("books.id"), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    html_content: Mapped[str] = mapped_column(Text, nullable=False)

    book: Mapped[BookRow] = relationship("BookRow", back_populates="chapters")


class ProgressRow(Base):
    __tablename__ = "reading_progress"

    book_id: Mapped[str] = mapped_column(String, primary_key=True)
    chapter_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
