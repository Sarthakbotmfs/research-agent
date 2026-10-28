from typing import List

from pydantic import BaseModel, Field

from .enums import EvidenceRelationshipEnum


class SubclaimPlanItem(BaseModel):
    subclaim_text: str = Field(
        ..., description="A testable, specific subclaim component of the main claim"
    )
    aspect: str = Field(
        ..., description="The dimension or aspect, e.g. productivity, quality, cognitive load"
    )
    search_queries: List[str] = Field(
        ..., description="Scholarly search queries designed for OpenAlex and Crossref"
    )


class SubclaimPlanningOutput(BaseModel):
    subclaims: List[SubclaimPlanItem] = Field(..., min_length=1, max_length=5)


class EvidenceClassificationItem(BaseModel):
    subclaim_id: str = Field(
        ..., description="The ID or exact text of the subclaim being evaluated"
    )
    relationship: EvidenceRelationshipEnum = Field(
        ..., description="Relationship of source passage to subclaim"
    )
    exact_passage: str = Field(
        ..., description="Exact quoted excerpt from the text that substantiates this classification"
    )
    rationale: str = Field(
        ...,
        description="Objective explanation of how the passage supports/contradicts/qualifies the claim",
    )
    limitations: str = Field(
        default="",
        description="Threats to validity, methodology constraints, or sample limitations mentioned",
    )
    confidence_score: float = Field(default=0.8, ge=0.0, le=1.0)


class EvidenceClassificationOutput(BaseModel):
    evaluations: List[EvidenceClassificationItem] = Field(default_factory=list)


class CounterEvidenceGapOutput(BaseModel):
    identified_gaps: List[str] = Field(
        default_factory=list, description="Missing dimensions or lack of contradictory evidence"
    )
    counter_queries: List[str] = Field(
        default_factory=list,
        description="Search queries specifically formulated to surface refutations, negative results, or contradictory studies",
    )


class ReportSynthesisOutput(BaseModel):
    title: str = Field(..., description="Clear, neutral title for the research report")
    executive_summary: str = Field(
        ..., description="Rigorous 2-3 paragraph synthesis of current scholarly evidence"
    )
    findings_by_subclaim: List[dict] = Field(
        default_factory=list, description="Detailed subclaim findings with citation IDs"
    )
    common_ground: str = Field(
        ..., description="Synthesis of where literature agrees across methodologies"
    )
    uncertainty_and_gaps: str = Field(
        ..., description="Documented areas of insufficient evidence and conflicting results"
    )
    limitations: str = Field(
        ...,
        description="Limitations of this automated synthesis and the underlying retrieved literature",
    )
