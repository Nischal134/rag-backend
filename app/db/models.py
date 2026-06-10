# app/db/models.py

import uuid
from datetime import date, datetime, time

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, Time, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """
    Every table class will inherit from this.
    SQLAlchemy uses it to track all our tables.
    """
    pass


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(10), nullable=False)   # "pdf" or "txt"
    storage_path: Mapped[str] = mapped_column(String(512), nullable=False)
    chunking_strategy: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="processing")
    total_chunks: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # This tells SQLAlchemy: "a Document owns many Chunks"
    chunks: Mapped[list["Chunk"]] = relationship(
        "Chunk", back_populates="document", cascade="all, delete-orphan"
    )


class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False
    )
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    chunk_size: Mapped[int] = mapped_column(Integer, nullable=False)
    qdrant_vector_id: Mapped[str] = mapped_column(
        String(100), nullable=False, unique=True
    )
    chunking_strategy: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # This tells SQLAlchemy: "a Chunk belongs to one Document"
    document: Mapped["Document"] = relationship(
        "Document", back_populates="chunks"
    )


class InterviewBooking(Base):
    __tablename__ = "interview_bookings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    # session_id ties the booking to a Redis chat session, not a document
    session_id: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )
    candidate_name: Mapped[str] = mapped_column(String(200), nullable=False)
    candidate_email: Mapped[str] = mapped_column(String(254), nullable=False)
    interview_date: Mapped[date] = mapped_column(Date, nullable=False)
    interview_time: Mapped[time] = mapped_column(Time, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="confirmed")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )