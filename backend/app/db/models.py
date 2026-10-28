import datetime
import uuid
from typing import List, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship as sa_relationship

from .base import Base


def utcnow() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


def generate_uuid() -> str:
    return uuid.uuid4().hex


# Association table connecting ResearchTask and Source for many-to-many reusability
task_sources = Table(
    "task_sources",
    Base.metadata,
    Column(
        "task_id", String(36), ForeignKey("research_tasks.id", ondelete="CASCADE"), primary_key=True
    ),
    Column("source_id", String(36), ForeignKey("sources.id", ondelete="CASCADE"), primary_key=True),
    Column("discovered_at", DateTime(timezone=True), default=utcnow, nullable=False),
    Column("query_used", String(255), nullable=True),
)


class ResearchTask(Base):
    __tablename__ = "research_tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    claim: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="pending", index=True, nullable=False)
    config: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )
    completed_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    subclaims: Mapped[List["Subclaim"]] = sa_relationship(
        "Subclaim", back_populates="task", cascade="all, delete-orphan"
    )
    sources: Mapped[List["Source"]] = sa_relationship(
        "Source", secondary=task_sources, back_populates="tasks"
    )
    evidence_items: Mapped[List["Evidence"]] = sa_relationship(
        "Evidence", back_populates="task", cascade="all, delete-orphan"
    )
    events: Mapped[List["ResearchEvent"]] = sa_relationship(
        "ResearchEvent",
        back_populates="task",
        cascade="all, delete-orphan",
        order_by="ResearchEvent.seq",
    )
    report: Mapped[Optional["Report"]] = sa_relationship(
        "Report", back_populates="task", uselist=False, cascade="all, delete-orphan"
    )


class Subclaim(Base):
    __tablename__ = "subclaims"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    task_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("research_tasks.id", ondelete="CASCADE"), index=True, nullable=False
    )
    subclaim_text: Mapped[str] = mapped_column(Text, nullable=False)
    aspect: Mapped[str] = mapped_column(String(128), default="general", nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )

    # Relationships
    task: Mapped["ResearchTask"] = sa_relationship("ResearchTask", back_populates="subclaims")
    evidence_items: Mapped[List["Evidence"]] = sa_relationship(
        "Evidence", back_populates="subclaim", cascade="all, delete-orphan"
    )


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    doi: Mapped[Optional[str]] = mapped_column(String(255), index=True, nullable=True)
    canonical_url: Mapped[str] = mapped_column(String(1024), index=True, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    authors: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    venue: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    source_type: Mapped[str] = mapped_column(String(64), default="unknown", nullable=False)
    is_peer_reviewed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    provenance: Mapped[str] = mapped_column(String(64), default="unknown", nullable=False)
    citation_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    open_access: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    abstract: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    full_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    extraction_status: Mapped[str] = mapped_column(String(64), default="pending", nullable=False)
    content_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    raw_metadata: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )

    # Relationships
    tasks: Mapped[List["ResearchTask"]] = sa_relationship(
        "ResearchTask", secondary=task_sources, back_populates="sources"
    )
    evidence_items: Mapped[List["Evidence"]] = sa_relationship("Evidence", back_populates="source")

    __table_args__ = (
        Index("idx_source_doi", "doi"),
        Index("idx_source_canonical_url", "canonical_url"),
    )


class Evidence(Base):
    __tablename__ = "evidence"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    task_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("research_tasks.id", ondelete="CASCADE"), index=True, nullable=False
    )
    subclaim_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("subclaims.id", ondelete="CASCADE"), index=True, nullable=False
    )
    source_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("sources.id", ondelete="CASCADE"), index=True, nullable=False
    )
    relationship: Mapped[str] = mapped_column(
        String(32), index=True, nullable=False
    )  # supports, contradicts, mixed, context, insufficient
    passage: Mapped[str] = mapped_column(Text, nullable=False)
    passage_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    limitations: Mapped[str] = mapped_column(Text, default="", nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    verification_status: Mapped[str] = mapped_column(String(32), default="verified", nullable=False)
    verification_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_independent: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )

    # Relationships
    task: Mapped["ResearchTask"] = sa_relationship("ResearchTask", back_populates="evidence_items")
    subclaim: Mapped["Subclaim"] = sa_relationship("Subclaim", back_populates="evidence_items")
    source: Mapped["Source"] = sa_relationship("Source", back_populates="evidence_items")

    __table_args__ = (Index("idx_evidence_task_rel", "task_id", "relationship"),)


class ResearchEvent(Base):
    __tablename__ = "research_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    seq: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    task_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("research_tasks.id", ondelete="CASCADE"), index=True, nullable=False
    )
    stage: Mapped[str] = mapped_column(String(64), nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    data: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )

    # Relationships
    task: Mapped["ResearchTask"] = sa_relationship("ResearchTask", back_populates="events")

    __table_args__ = (Index("idx_events_task_seq", "task_id", "seq"),)


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    task_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("research_tasks.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    executive_summary: Mapped[str] = mapped_column(Text, nullable=False)
    findings: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    common_ground: Mapped[str] = mapped_column(Text, default="", nullable=False)
    uncertainty_and_gaps: Mapped[str] = mapped_column(Text, default="", nullable=False)
    methodology: Mapped[str] = mapped_column(Text, nullable=False)
    limitations: Mapped[str] = mapped_column(Text, nullable=False)
    citations: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="complete", nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )

    # Relationships
    task: Mapped["ResearchTask"] = sa_relationship("ResearchTask", back_populates="report")
