from __future__ import annotations

import uuid
from datetime import datetime
from typing import AsyncGenerator

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, relationship

from backend.config.logging import get_logger
from backend.config.settings import get_settings

logger = get_logger("database.postgres")

# ── Engine & Session Factory ────────────────────────────────────────────────

_settings = get_settings()

engine = create_async_engine(
    _settings.DATABASE_URL,
    echo=_settings.DB_ECHO,
    pool_size=_settings.DB_POOL_SIZE,
    max_overflow=_settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True,
)

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an async database session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ── Base Model ──────────────────────────────────────────────────────────────


class Base(DeclarativeBase):
    pass


# ── Models ──────────────────────────────────────────────────────────────────


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(
        Enum("admin", "manager", "viewer", name="user_role"),
        nullable=False,
        default="viewer",
    )
    avatar = Column(String(512), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    properties = relationship("Property", back_populates="owner", lazy="selectin")
    documents = relationship("Document", back_populates="user", lazy="selectin")


class Property(Base):
    __tablename__ = "properties"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(512), nullable=False)
    location = Column(String(512), nullable=False)
    coordinates = Column(JSONB, nullable=True)  # [lat, lon]
    area = Column(Float, nullable=False)
    area_unit = Column(
        Enum("sqft", "acres", "hectares", name="area_unit"),
        nullable=False,
        default="sqft",
    )
    status = Column(
        Enum("verified", "pending", "disputed", name="property_status"),
        nullable=False,
        default="pending",
    )
    value = Column(Float, nullable=True)
    survey_number = Column(String(100), nullable=True, index=True)
    registration_number = Column(String(100), nullable=True, index=True)
    khata_number = Column(String(100), nullable=True, index=True)
    district = Column(String(255), nullable=True)
    state = Column(String(255), nullable=True)
    owner_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    owner = relationship("User", back_populates="properties")
    documents = relationship("Document", back_populates="property", lazy="selectin")


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    property_id = Column(
        UUID(as_uuid=True),
        ForeignKey("properties.id", ondelete="SET NULL"),
        nullable=True,
    )
    title = Column(String(512), nullable=False)
    document_type = Column(
        Enum("deed", "survey", "legal", "tax", "insurance", "inspection", "other",
             name="document_type"),
        nullable=False,
        default="other",
    )
    file_path = Column(String(1024), nullable=False)
    file_hash = Column(String(64), nullable=False, unique=True, index=True)
    file_size = Column(Integer, nullable=False)
    page_count = Column(Integer, nullable=True)
    ocr_applied = Column(Boolean, default=False)
    metadata_extracted = Column(JSONB, nullable=True)
    status = Column(
        Enum("processing", "completed", "failed", name="document_status"),
        nullable=False,
        default="processing",
    )
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="documents")
    property = relationship("Property", back_populates="documents")
    chunks = relationship(
        "DocumentChunk", back_populates="document", cascade="all, delete-orphan"
    )


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    property_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
    )
    document_type = Column(String(50), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    embedding_id = Column(String(255), nullable=False, unique=True)
    chunk_metadata = Column("metadata", JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    document = relationship("Document", back_populates="chunks")

    __table_args__ = (
        Index("ix_chunk_user_property", "user_id", "property_id"),
        Index("ix_chunk_document_type", "document_type"),
    )


class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category = Column(String(100), nullable=False, index=True)
    title = Column(String(512), nullable=False)
    content = Column(Text, nullable=False)
    embedding_id = Column(String(255), nullable=True, unique=True)
    kb_metadata = Column("metadata", JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class ConversationSummary(Base):
    """Schema only — not implemented in Phase 1."""

    __tablename__ = "conversation_summaries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    property_id = Column(UUID(as_uuid=True), nullable=True)
    summary = Column(Text, nullable=False)
    message_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


# ── Table creation helper ───────────────────────────────────────────────────


async def init_db() -> None:
    """Create all tables if they do not exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables initialized")
