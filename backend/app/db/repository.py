from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .models import (
    Evidence,
    Report,
    ResearchEvent,
    ResearchTask,
    Source,
    Subclaim,
    task_sources,
    utcnow,
)


class ResearchRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_task(self, claim: str, config: dict) -> ResearchTask:
        task = ResearchTask(
            claim=claim,
            config=config,
            status="pending",
        )
        self.session.add(task)
        await self.session.flush()
        return task

    async def get_task(self, task_id: str) -> Optional[ResearchTask]:
        query = (
            select(ResearchTask)
            .where(ResearchTask.id == task_id)
            .options(
                selectinload(ResearchTask.subclaims),
                selectinload(ResearchTask.sources),
                selectinload(ResearchTask.evidence_items),
                selectinload(ResearchTask.report),
            )
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def list_tasks(self, limit: int = 50, offset: int = 0) -> List[ResearchTask]:
        query = (
            select(ResearchTask)
            .order_by(ResearchTask.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update_task_status(
        self,
        task_id: str,
        status: str,
        error_message: Optional[str] = None,
        completed: bool = False,
    ) -> None:
        task = await self.session.get(ResearchTask, task_id)
        if task:
            task.status = status
            task.updated_at = utcnow()
            if error_message:
                task.error_message = error_message
            if completed:
                task.completed_at = utcnow()
            await self.session.flush()

    async def add_subclaims(self, task_id: str, subclaims: List[dict]) -> List[Subclaim]:
        created = []
        for sc_data in subclaims:
            sc = Subclaim(
                task_id=task_id,
                subclaim_text=sc_data["subclaim_text"],
                aspect=sc_data.get("aspect", "general"),
                status="investigating",
            )
            self.session.add(sc)
            created.append(sc)
        await self.session.flush()
        return created

    async def get_or_create_source(
        self, source_dict: dict, task_id: str, query_used: Optional[str] = None
    ) -> Source:
        """Finds existing source by DOI or canonical URL, or creates a new one, and links to task."""
        doi = source_dict.get("doi")
        url = source_dict.get("canonical_url")

        source = None
        if doi:
            q = select(Source).where(Source.doi == doi)
            res = await self.session.execute(q)
            source = res.scalars().first()

        if not source and url:
            q = select(Source).where(Source.canonical_url == url)
            res = await self.session.execute(q)
            source = res.scalars().first()

        if not source:
            source = Source(
                doi=doi,
                canonical_url=url,
                title=source_dict.get("title", "Untitled Document"),
                authors=source_dict.get("authors", []),
                venue=source_dict.get("venue"),
                year=source_dict.get("year"),
                source_type=source_dict.get("source_type", "unknown"),
                is_peer_reviewed=source_dict.get("is_peer_reviewed", False),
                provenance=source_dict.get("provenance", "unknown"),
                citation_count=source_dict.get("citation_count", 0),
                open_access=source_dict.get("open_access", False),
                abstract=source_dict.get("abstract"),
                full_text=source_dict.get("full_text"),
                extraction_status=source_dict.get(
                    "extraction_status",
                    "abstract_only" if source_dict.get("abstract") else "pending",
                ),
                content_hash=source_dict.get("content_hash"),
                raw_metadata=source_dict.get("raw_metadata", {}),
            )
            self.session.add(source)
            await self.session.flush()

        # Link to task if not already linked
        link_q = select(task_sources).where(
            task_sources.c.task_id == task_id,
            task_sources.c.source_id == source.id,
        )
        link_res = await self.session.execute(link_q)
        if not link_res.first():
            ins = task_sources.insert().values(
                task_id=task_id,
                source_id=source.id,
                discovered_at=utcnow(),
                query_used=query_used,
            )
            await self.session.execute(ins)
            await self.session.flush()

        return source

    async def add_evidence(
        self,
        task_id: str,
        subclaim_id: str,
        source_id: str,
        relationship: str,
        passage: str,
        passage_hash: str,
        rationale: str,
        limitations: str,
        confidence_score: float,
        verification_status: str = "verified",
        verification_details: Optional[str] = None,
        is_independent: bool = True,
    ) -> Evidence:
        ev = Evidence(
            task_id=task_id,
            subclaim_id=subclaim_id,
            source_id=source_id,
            relationship=relationship,
            passage=passage,
            passage_hash=passage_hash,
            rationale=rationale,
            limitations=limitations,
            confidence_score=confidence_score,
            verification_status=verification_status,
            verification_details=verification_details,
            is_independent=is_independent,
        )
        self.session.add(ev)
        await self.session.flush()
        return ev

    async def get_task_evidence(self, task_id: str) -> List[Evidence]:
        query = (
            select(Evidence)
            .where(Evidence.task_id == task_id)
            .options(
                selectinload(Evidence.source),
                selectinload(Evidence.subclaim),
            )
            .order_by(Evidence.created_at.asc())
        )
        res = await self.session.execute(query)
        return list(res.scalars().all())

    async def add_event(
        self,
        task_id: str,
        stage: str,
        event_type: str,
        message: str,
        data: Optional[dict] = None,
    ) -> ResearchEvent:
        # Get next seq number for this task
        seq_query = select(func.coalesce(func.max(ResearchEvent.seq), 0)).where(
            ResearchEvent.task_id == task_id
        )
        res = await self.session.execute(seq_query)
        max_seq = res.scalar() or 0

        event = ResearchEvent(
            seq=max_seq + 1,
            task_id=task_id,
            stage=stage,
            event_type=event_type,
            message=message,
            data=data or {},
        )
        self.session.add(event)
        await self.session.flush()
        return event

    async def get_events_after(self, task_id: str, after_seq: int = 0) -> List[ResearchEvent]:
        query = (
            select(ResearchEvent)
            .where(ResearchEvent.task_id == task_id, ResearchEvent.seq > after_seq)
            .order_by(ResearchEvent.seq.asc())
        )
        res = await self.session.execute(query)
        return list(res.scalars().all())

    async def save_report(
        self,
        task_id: str,
        title: str,
        executive_summary: str,
        findings: dict,
        common_ground: str,
        uncertainty_and_gaps: str,
        methodology: str,
        limitations: str,
        citations: list,
        status: str = "complete",
    ) -> Report:
        # Check if report already exists for task
        q = select(Report).where(Report.task_id == task_id)
        res = await self.session.execute(q)
        report = res.scalars().first()

        if report:
            report.title = title
            report.executive_summary = executive_summary
            report.findings = findings
            report.common_ground = common_ground
            report.uncertainty_and_gaps = uncertainty_and_gaps
            report.methodology = methodology
            report.limitations = limitations
            report.citations = citations
            report.status = status
        else:
            report = Report(
                task_id=task_id,
                title=title,
                executive_summary=executive_summary,
                findings=findings,
                common_ground=common_ground,
                uncertainty_and_gaps=uncertainty_and_gaps,
                methodology=methodology,
                limitations=limitations,
                citations=citations,
                status=status,
            )
            self.session.add(report)

        await self.session.flush()
        return report

    async def get_report(self, task_id: str) -> Optional[Report]:
        q = select(Report).where(Report.task_id == task_id)
        res = await self.session.execute(q)
        return res.scalars().first()
