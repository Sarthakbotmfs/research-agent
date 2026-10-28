import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class CitationSchema(BaseModel):
    citation_id: str
    source_id: str
    title: str
    authors: List[str]
    year: Optional[int] = None
    venue: Optional[str] = None
    doi: Optional[str] = None
    canonical_url: str
    evidence_ids: List[str] = Field(default_factory=list)


class ReportResponse(BaseModel):
    id: str
    task_id: str
    title: str
    executive_summary: str
    findings: Dict[str, Any]
    common_ground: str
    uncertainty_and_gaps: str
    methodology: str
    limitations: str
    citations: List[CitationSchema]
    status: str
    created_at: datetime.datetime
