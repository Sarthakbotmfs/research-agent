import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repository import ResearchRepository
from app.providers.base import NormalizedSource


def test_doi_normalization():
    s1 = NormalizedSource(
        doi="https://doi.org/10.1145/3540250.3549177",
        canonical_url="https://doi.org/10.1145/3540250.3549177",
        title="Test Source 1",
    )
    s2 = NormalizedSource(
        doi="10.1145/3540250.3549177",
        canonical_url="http://example.com/alt",
        title="Test Source 2",
    )
    s3 = NormalizedSource(
        doi="DOI:10.1145/3540250.3549177",
        canonical_url="http://example.com/alt2",
        title="Test Source 3",
    )

    assert s1.normalize_doi() == "10.1145/3540250.3549177"
    assert s2.normalize_doi() == "10.1145/3540250.3549177"
    assert s3.normalize_doi() == "10.1145/3540250.3549177"


@pytest.mark.asyncio
async def test_repository_source_deduplication_and_reuse(db_session: AsyncSession):
    repo = ResearchRepository(db_session)

    # Create two tasks
    task1 = await repo.create_task("Claim 1 about AI assistants", {})
    task2 = await repo.create_task("Claim 2 about code generation", {})
    await db_session.commit()

    source_data = {
        "doi": "10.1000/182",
        "canonical_url": "https://doi.org/10.1000/182",
        "title": "Universal Scholarly Paper",
        "authors": ["Dr. Researcher"],
        "year": 2024,
        "is_peer_reviewed": True,
        "provenance": "openalex",
    }

    # Add source to task1
    src1 = await repo.get_or_create_source(source_data, task_id=task1.id, query_used="query 1")
    await db_session.commit()

    # Add identical source (same DOI) to task2
    src2 = await repo.get_or_create_source(source_data, task_id=task2.id, query_used="query 2")
    await db_session.commit()

    # Both tasks should link to the exact same source record in the database!
    assert src1.id == src2.id

    # Verify task relations
    t1_reloaded = await repo.get_task(task1.id)
    t2_reloaded = await repo.get_task(task2.id)

    assert len(t1_reloaded.sources) == 1
    assert len(t2_reloaded.sources) == 1
    assert t1_reloaded.sources[0].id == src1.id
    assert t2_reloaded.sources[0].id == src1.id
