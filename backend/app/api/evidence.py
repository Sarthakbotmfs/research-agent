from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.repository import ResearchRepository
from ..db.session import get_db
from ..schemas.enums import EvidenceRelationshipEnum
from ..schemas.evidence import EvidenceItemResponse, EvidenceListResponse
from ..schemas.research import SourceSummarySchema, SubclaimSchema

router = APIRouter(prefix="/api/research", tags=["Evidence"])


@router.get("/{task_id}/evidence", response_model=EvidenceListResponse)
async def get_task_evidence(
    task_id: str,
    db: AsyncSession = Depends(get_db),
):
    repo = ResearchRepository(db)
    task = await repo.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Research task '{task_id}' not found.",
        )

    evidence_items = await repo.get_task_evidence(task_id)

    # Calculate counts by relationship
    counts: Dict[str, int] = {
        "supports": 0,
        "contradicts": 0,
        "mixed": 0,
        "context": 0,
        "insufficient": 0,
    }

    serialized_items = []
    for ev in evidence_items:
        rel = ev.relationship.lower()
        if rel in counts:
            counts[rel] += 1
        else:
            counts[rel] = 1

        src_schema = None
        if ev.source:
            src_schema = SourceSummarySchema(
                id=ev.source.id,
                doi=ev.source.doi,
                canonical_url=ev.source.canonical_url,
                title=ev.source.title,
                authors=ev.source.authors,
                venue=ev.source.venue,
                year=ev.source.year,
                source_type=ev.source.source_type,
                is_peer_reviewed=ev.source.is_peer_reviewed,
                provenance=ev.source.provenance,
                citation_count=ev.source.citation_count,
                open_access=ev.source.open_access,
                abstract=ev.source.abstract,
                extraction_status=ev.source.extraction_status,
                content_hash=ev.source.content_hash,
            )

        sc_schema = None
        if ev.subclaim:
            sc_schema = SubclaimSchema(
                id=ev.subclaim.id,
                subclaim_text=ev.subclaim_text
                if hasattr(ev, "subclaim_text")
                else ev.subclaim.subclaim_text,
                aspect=ev.subclaim.aspect,
                status=ev.subclaim.status,
                created_at=ev.subclaim.created_at,
            )

        serialized_items.append(
            EvidenceItemResponse(
                id=ev.id,
                task_id=ev.task_id,
                subclaim_id=ev.subclaim_id,
                source_id=ev.source_id,
                relationship=EvidenceRelationshipEnum(ev.relationship),
                passage=ev.passage,
                passage_hash=ev.passage_hash,
                rationale=ev.rationale,
                limitations=ev.limitations,
                confidence_score=ev.confidence_score,
                verification_status=ev.verification_status,
                verification_details=ev.verification_details,
                is_independent=ev.is_independent,
                created_at=ev.created_at,
                source=src_schema,
                subclaim=sc_schema,
            )
        )

    return EvidenceListResponse(
        task_id=task_id,
        total_count=len(serialized_items),
        counts_by_relationship=counts,
        items=serialized_items,
    )
