import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

from .enums import TaskStatusEnum


class TaskConfigSchema(BaseModel):
    max_rounds: int = Field(
        default=3, ge=1, le=5, description="Max iterative search and refinement rounds"
    )
    max_queries: int = Field(
        default=15, ge=1, le=30, description="Max search queries across all rounds"
    )
    max_sources: int = Field(
        default=40, ge=5, le=100, description="Max unique scholarly sources to gather"
    )
    max_page_fetches: int = Field(
        default=20, ge=1, le=50, description="Max open access full text or page fetches"
    )
    allow_full_text_fetch: bool = Field(
        default=True, description="Whether to fetch permitted open access web passages"
    )


class TaskCreateRequest(BaseModel):
    claim: str = Field(
        ..., min_length=10, max_length=1000, description="The research claim to investigate"
    )
    config: Optional[TaskConfigSchema] = Field(default_factory=TaskConfigSchema)

    @field_validator("claim")
    @classmethod
    def validate_claim_not_empty(cls, v: str) -> str:
        clean = v.strip()
        if len(clean) < 10:
            raise ValueError("Claim must be at least 10 non-whitespace characters long.")
        return clean


class SubclaimSchema(BaseModel):
    id: str
    subclaim_text: str
    aspect: str
    status: str
    created_at: datetime.datetime


class SourceSummarySchema(BaseModel):
    id: str
    doi: Optional[str] = None
    canonical_url: str
    title: str
    authors: List[str]
    venue: Optional[str] = None
    year: Optional[int] = None
    source_type: str
    is_peer_reviewed: bool
    provenance: str
    citation_count: int
    open_access: bool
    abstract: Optional[str] = None
    extraction_status: str
    content_hash: Optional[str] = None


class TaskResponse(BaseModel):
    id: str
    claim: str
    status: TaskStatusEnum
    config: Dict[str, Any]
    error_message: Optional[str] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime
    completed_at: Optional[datetime.datetime] = None
    subclaims: List[SubclaimSchema] = Field(default_factory=list)
    sources_count: int = 0
    evidence_count: int = 0
    has_report: bool = False


class TaskDetailResponse(TaskResponse):
    sources: List[SourceSummarySchema] = Field(default_factory=list)
