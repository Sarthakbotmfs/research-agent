import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel

from .enums import EvidenceRelationshipEnum
from .research import SourceSummarySchema, SubclaimSchema


class EvidenceItemResponse(BaseModel):
    id: str
    task_id: str
    subclaim_id: str
    source_id: str
    relationship: EvidenceRelationshipEnum
    passage: str
    passage_hash: str
    rationale: str
    limitations: str
    confidence_score: float
    verification_status: str
    verification_details: Optional[str] = None
    is_independent: bool
    created_at: datetime.datetime
    source: Optional[SourceSummarySchema] = None
    subclaim: Optional[SubclaimSchema] = None


class EvidenceListResponse(BaseModel):
    task_id: str
    total_count: int
    counts_by_relationship: Dict[str, int]
    items: List[EvidenceItemResponse]
