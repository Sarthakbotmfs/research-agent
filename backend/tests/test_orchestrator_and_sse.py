import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repository import ResearchRepository
from app.providers.base import LLMProvider, NormalizedSource, ScholarlySearchAdapter
from app.research.orchestrator import ResearchOrchestrator
from app.schemas.llm_payloads import (
    CounterEvidenceGapOutput,
    EvidenceClassificationItem,
    EvidenceClassificationOutput,
    ReportSynthesisOutput,
    SubclaimPlanItem,
    SubclaimPlanningOutput,
)


class MockScholarlySearchAdapter(ScholarlySearchAdapter):
    def __init__(self, prefix: str):
        self.prefix = prefix

    async def search(self, query: str, limit: int = 10) -> list[NormalizedSource]:
        return [
            NormalizedSource(
                doi=f"10.1145/{self.prefix}_001",
                canonical_url=f"https://doi.org/10.1145/{self.prefix}_001",
                title=f"{self.prefix.upper()} Study on Developer Productivity",
                authors=["Test Author"],
                year=2024,
                venue="Journal of Software",
                source_type="peer-reviewed",
                is_peer_reviewed=True,
                provenance=self.prefix,
                abstract="Empirical evaluation indicates a 25% speedup with subtle defect risks.",
            )
        ]


class MockLLMProvider(LLMProvider):
    async def is_available(self) -> bool:
        return True

    async def generate_structured(self, prompt: str, system_prompt: str, response_model):
        if issubclass(response_model, SubclaimPlanningOutput):
            return SubclaimPlanningOutput(
                subclaims=[
                    SubclaimPlanItem(
                        subclaim_text="Developer completion time decreases for standard tasks",
                        aspect="speed",
                        search_queries=["developer velocity empirical study"],
                    ),
                    SubclaimPlanItem(
                        subclaim_text="Defect rates and bug density increase without human review",
                        aspect="quality",
                        search_queries=["AI coding defect density security"],
                    ),
                ]
            )
        elif issubclass(response_model, CounterEvidenceGapOutput):
            return CounterEvidenceGapOutput(
                identified_gaps=["Lack of long-term maintainability evidence"],
                counter_queries=["AI coding assistant code churn negative effects"],
            )
        elif issubclass(response_model, EvidenceClassificationOutput):
            return EvidenceClassificationOutput(
                evaluations=[
                    EvidenceClassificationItem(
                        subclaim_id="subclaim_test",
                        relationship="supports",
                        exact_passage="Empirical evaluation indicates a 25% speedup",
                        rationale="Controlled benchmark shows statistically significant time reduction.",
                        limitations="Conducted in laboratory environment.",
                        confidence_score=0.85,
                    )
                ]
            )
        elif issubclass(response_model, ReportSynthesisOutput):
            return ReportSynthesisOutput(
                title="Synthesized Findings on AI Coding Productivity",
                executive_summary="Empirical evidence validates speed increases alongside defect monitoring needs.",
                findings_by_subclaim=[],
                common_ground="Routine task acceleration is consistently documented.",
                uncertainty_and_gaps="Multi-year technical debt remains unmeasured.",
                limitations="Limited to accessible scholarly literature.",
            )
        raise ValueError(f"Unknown response model {response_model}")


@pytest.mark.asyncio
async def test_orchestrator_full_workflow(db_session: AsyncSession):
    repo = ResearchRepository(db_session)
    task = await repo.create_task(
        claim="AI coding assistants improve software developer productivity.",
        config={"max_rounds": 2, "max_queries": 4, "max_sources": 10},
    )
    await db_session.commit()

    orchestrator = ResearchOrchestrator(
        repo=repo,
        llm=MockLLMProvider(),
        openalex=MockScholarlySearchAdapter("openalex"),
        crossref=MockScholarlySearchAdapter("crossref"),
    )

    task_id = task.id
    await orchestrator.run_research(task_id)
    await db_session.commit()
    db_session.expire_all()

    # Verify task state
    updated_task = await repo.get_task(task_id)
    assert updated_task.status in ("completed", "partial")
    assert len(updated_task.subclaims) == 2
    assert len(updated_task.sources) >= 2
    assert len(updated_task.evidence_items) >= 1
    assert updated_task.report is not None
    assert updated_task.report.title == "Synthesized Findings on AI Coding Productivity"

    # Verify events were recorded
    events = await repo.get_events_after(task.id, after_seq=0)
    assert len(events) >= 6
    stages = [e.stage for e in events]
    assert "initialization" in stages
    assert "planning" in stages
    assert "searching" in stages
    assert "classifying" in stages
    assert "verifying" in stages
    assert "synthesizing" in stages


@pytest.mark.asyncio
async def test_sse_event_replay(db_session: AsyncSession):
    repo = ResearchRepository(db_session)
    task = await repo.create_task("Test claim for SSE replay", {})
    await db_session.commit()

    # Emit three sequential events
    await repo.add_event(task.id, "planning", "event_1", "Message 1")
    await repo.add_event(task.id, "searching", "event_2", "Message 2")
    await repo.add_event(task.id, "classifying", "event_3", "Message 3")
    await db_session.commit()

    # Replay from seq 0
    all_events = await repo.get_events_after(task.id, after_seq=0)
    assert len(all_events) == 3
    assert all_events[0].seq == 1
    assert all_events[1].seq == 2
    assert all_events[2].seq == 3

    # Replay with after_seq = 2 (reconnect scenario)
    replayed = await repo.get_events_after(task.id, after_seq=2)
    assert len(replayed) == 1
    assert replayed[0].seq == 3
    assert replayed[0].event_type == "event_3"
