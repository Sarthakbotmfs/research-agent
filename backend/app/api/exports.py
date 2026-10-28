import json

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.repository import ResearchRepository
from ..db.session import get_db
from ..exports.json_export import generate_json_export
from ..exports.markdown_export import generate_markdown_report
from ..exports.pdf_export import generate_pdf_report

router = APIRouter(prefix="/api/research", tags=["Exports"])


@router.get("/{task_id}/export")
async def export_research_task(
    task_id: str,
    format: str = Query(default="md", pattern="^(md|json|pdf)$"),
    db: AsyncSession = Depends(get_db),
):
    repo = ResearchRepository(db)
    task = await repo.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Research task '{task_id}' not found.",
        )

    subclaims = task.subclaims
    sources = task.sources
    evidence_items = await repo.get_task_evidence(task_id)
    report = await repo.get_report(task_id)

    if format == "md":
        content = generate_markdown_report(
            task=task,
            subclaims=subclaims,
            sources=sources,
            evidence_items=evidence_items,
            report=report,
        )
        return PlainTextResponse(
            content=content,
            media_type="text/markdown",
            headers={"Content-Disposition": f'attachment; filename="research_report_{task_id}.md"'},
        )

    elif format == "json":
        data = generate_json_export(
            task=task,
            subclaims=subclaims,
            sources=sources,
            evidence_items=evidence_items,
            report=report,
        )
        json_bytes = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
        return Response(
            content=json_bytes,
            media_type="application/json",
            headers={
                "Content-Disposition": f'attachment; filename="research_dossier_{task_id}.json"'
            },
        )

    elif format == "pdf":
        pdf_bytes = generate_pdf_report(
            task=task,
            subclaims=subclaims,
            sources=sources,
            evidence_items=evidence_items,
            report=report,
        )
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="research_report_{task_id}.pdf"'
            },
        )
