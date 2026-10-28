import asyncio
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.logging import get_logger
from ..db.repository import ResearchRepository
from ..db.session import AsyncSessionLocal, get_db
from ..research.orchestrator import ResearchOrchestrator
from ..schemas.research import (
    SourceSummarySchema,
    SubclaimSchema,
    TaskCreateRequest,
    TaskDetailResponse,
    TaskResponse,
    TaskStatusEnum,
)

logger = get_logger(__name__)
router = APIRouter(prefix="/api/research", tags=["Research"])


async def run_orchestration_background(task_id: str) -> None:
    """Runs orchestrator in independent database session for background processing."""
    async with AsyncSessionLocal() as session:
        try:
            repo = ResearchRepository(session)
            orchestrator = ResearchOrchestrator(repo)
            await orchestrator.run_research(task_id)
            await session.commit()
        except Exception as e:
            logger.error(f"Background research orchestrator failed for {task_id}: {e}")
            await session.rollback()


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_research_task(
    request: TaskCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    repo = ResearchRepository(db)
    config_dict = request.config.model_dump() if request.config else {}

    task = await repo.create_task(
        claim=request.claim,
        config=config_dict,
    )
    await db.commit()
    await db.refresh(task)

    # Launch background research task
    asyncio.create_task(run_orchestration_background(task.id))

    return TaskResponse(
        id=task.id,
        claim=task.claim,
        status=TaskStatusEnum(task.status),
        config=task.config,
        error_message=task.error_message,
        created_at=task.created_at,
        updated_at=task.updated_at,
        completed_at=task.completed_at,
        subclaims=[],
        sources_count=0,
        evidence_count=0,
        has_report=False,
    )


@router.get("", response_model=List[TaskResponse])
async def list_research_tasks(
    limit: int = Query(default=30, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    repo = ResearchRepository(db)
    tasks = await repo.list_tasks(limit=limit, offset=offset)

    responses = []
    for t in tasks:
        # Load related counts
        full_t = await repo.get_task(t.id)
        if full_t:
            sc_schemas = [
                SubclaimSchema(
                    id=sc.id,
                    subclaim_text=sc.subclaim_text,
                    aspect=sc.aspect,
                    status=sc.status,
                    created_at=sc.created_at,
                )
                for sc in full_t.subclaims
            ]
            responses.append(
                TaskResponse(
                    id=full_t.id,
                    claim=full_t.claim,
                    status=TaskStatusEnum(full_t.status),
                    config=full_t.config,
                    error_message=full_t.error_message,
                    created_at=full_t.created_at,
                    updated_at=full_t.updated_at,
                    completed_at=full_t.completed_at,
                    subclaims=sc_schemas,
                    sources_count=len(full_t.sources),
                    evidence_count=len(full_t.evidence_items),
                    has_report=bool(full_t.report),
                )
            )
    return responses


@router.get("/{task_id}", response_model=TaskDetailResponse)
async def get_research_task(
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

    sc_schemas = [
        SubclaimSchema(
            id=sc.id,
            subclaim_text=sc.subclaim_text,
            aspect=sc.aspect,
            status=sc.status,
            created_at=sc.created_at,
        )
        for sc in task.subclaims
    ]

    source_schemas = [
        SourceSummarySchema(
            id=s.id,
            doi=s.doi,
            canonical_url=s.canonical_url,
            title=s.title,
            authors=s.authors,
            venue=s.venue,
            year=s.year,
            source_type=s.source_type,
            is_peer_reviewed=s.is_peer_reviewed,
            provenance=s.provenance,
            citation_count=s.citation_count,
            open_access=s.open_access,
            abstract=s.abstract,
            extraction_status=s.extraction_status,
            content_hash=s.content_hash,
        )
        for s in task.sources
    ]

    return TaskDetailResponse(
        id=task.id,
        claim=task.claim,
        status=TaskStatusEnum(task.status),
        config=task.config,
        error_message=task.error_message,
        created_at=task.created_at,
        updated_at=task.updated_at,
        completed_at=task.completed_at,
        subclaims=sc_schemas,
        sources_count=len(task.sources),
        evidence_count=len(task.evidence_items),
        has_report=bool(task.report),
        sources=source_schemas,
    )
