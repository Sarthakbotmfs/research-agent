from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.repository import ResearchRepository
from ..db.session import get_db
from ..schemas.report import CitationSchema, ReportResponse

router = APIRouter(prefix="/api/research", tags=["Reports"])


@router.get("/{task_id}/report", response_model=ReportResponse)
async def get_task_report(
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

    report = await repo.get_report(task_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report for task '{task_id}' has not been generated yet. Current status: '{task.status}'.",
        )

    citations = [
        CitationSchema(
            citation_id=c.get("citation_id", ""),
            source_id=c.get("source_id", ""),
            title=c.get("title", ""),
            authors=c.get("authors", []),
            year=c.get("year"),
            venue=c.get("venue"),
            doi=c.get("doi"),
            canonical_url=c.get("canonical_url", ""),
            evidence_ids=c.get("evidence_ids", []),
        )
        for c in (report.citations or [])
    ]

    return ReportResponse(
        id=report.id,
        task_id=report.task_id,
        title=report.title,
        executive_summary=report.executive_summary,
        findings=report.findings,
        common_ground=report.common_ground,
        uncertainty_and_gaps=report.uncertainty_and_gaps,
        methodology=report.methodology,
        limitations=report.limitations,
        citations=citations,
        status=report.status,
        created_at=report.created_at,
    )
