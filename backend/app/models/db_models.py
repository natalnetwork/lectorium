from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database import Base


class UserRow(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)

    books: Mapped[list[BookRow]] = relationship(
        "BookRow",
        back_populates="owner",
        cascade="all, delete-orphan",
    )


class BookRow(Base):
    __tablename__ = "books"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    author: Mapped[str] = mapped_column(String, nullable=False)
    language: Mapped[str] = mapped_column(String, nullable=False, default="unknown")
    cover_url: Mapped[str | None] = mapped_column(String, nullable=True)

    owner: Mapped[UserRow] = relationship("UserRow", back_populates="books")
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
