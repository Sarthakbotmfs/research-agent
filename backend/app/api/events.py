import asyncio
import json
from typing import AsyncGenerator, Optional

from fastapi import APIRouter, Header, HTTPException, Query, Request, status
from fastapi.responses import StreamingResponse

from ..core.logging import get_logger
from ..db.repository import ResearchRepository
from ..db.session import AsyncSessionLocal

logger = get_logger(__name__)
router = APIRouter(prefix="/api/research", tags=["Events"])


async def event_generator(
    task_id: str,
    start_seq: int,
    request: Request,
) -> AsyncGenerator[str, None]:
    """Generates SSE formatted events for a research task with event replay."""
    last_seq = start_seq
    ping_counter = 0

    # Ensure orchestrator is active if task is pending (crucial in serverless environments)
    async with AsyncSessionLocal() as session:
        repo = ResearchRepository(session)
        task = await repo.get_task(task_id)
        if task and task.status == "pending":
            from .research import run_orchestration_background
            asyncio.create_task(run_orchestration_background(task_id))

    while True:
        # Check if client disconnected
        if await request.is_disconnected():
            logger.info(f"SSE client disconnected for task {task_id}")
            break

        async with AsyncSessionLocal() as session:
            repo = ResearchRepository(session)
            task = await repo.get_task(task_id)
            if not task:
                yield f"event: error\ndata: {json.dumps({'error': 'Task not found'})}\n\n"
                break

            events = await repo.get_events_after(task_id, after_seq=last_seq)
            for ev in events:
                payload = {
                    "id": ev.id,
                    "seq": ev.seq,
                    "task_id": ev.task_id,
                    "stage": ev.stage,
                    "event_type": ev.event_type,
                    "message": ev.message,
                    "data": ev.data,
                    "created_at": str(ev.created_at),
                }
                yield f"id: {ev.seq}\nevent: {ev.event_type}\ndata: {json.dumps(payload)}\n\n"
                last_seq = max(last_seq, ev.seq)

            # If task has completed, failed, or partial and all events emitted, terminate stream
            if task.status in ("completed", "partial", "failed") and not events:
                yield f"event: done\ndata: {json.dumps({'status': task.status})}\n\n"
                break

        ping_counter += 1
        if ping_counter >= 15:  # Send ping every ~7.5 seconds
            yield ": ping\n\n"
            ping_counter = 0

        await asyncio.sleep(0.5)


@router.get("/{task_id}/events")
async def stream_research_events(
    task_id: str,
    request: Request,
    last_event_id: Optional[str] = Header(None, alias="Last-Event-ID"),
    after_seq: int = Query(default=0, ge=0),
):
    start_seq = after_seq
    if last_event_id and last_event_id.isdigit():
        start_seq = max(start_seq, int(last_event_id))

    # Verify task exists before starting stream
    async with AsyncSessionLocal() as session:
        repo = ResearchRepository(session)
        task = await repo.get_task(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Research task '{task_id}' not found.",
            )

    return StreamingResponse(
        event_generator(task_id, start_seq, request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
