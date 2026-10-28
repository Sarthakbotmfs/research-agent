import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repository import ResearchRepository


@pytest.mark.asyncio
async def test_health_check(async_client: AsyncClient):
    resp = await async_client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert "llm_configured" in data


@pytest.mark.asyncio
async def test_create_and_get_research_task(async_client: AsyncClient, db_session: AsyncSession):
    # Create task
    payload = {
        "claim": "AI coding assistants improve software developer productivity.",
        "config": {
            "max_rounds": 2,
            "max_queries": 10,
            "max_sources": 20,
        },
    }
    resp = await async_client.post("/api/research", json=payload)
    assert resp.status_code == 201
    task_data = resp.json()
    task_id = task_data["id"]
    assert task_data["claim"] == payload["claim"]
    assert task_data["status"] == "pending"

    # Get task detail
    detail_resp = await async_client.get(f"/api/research/{task_id}")
    assert detail_resp.status_code == 200
    detail_data = detail_resp.json()
    assert detail_data["id"] == task_id

    # List tasks
    list_resp = await async_client.get("/api/research")
    assert list_resp.status_code == 200
    tasks_list = list_resp.json()
    assert any(t["id"] == task_id for t in tasks_list)


@pytest.mark.asyncio
async def test_unknown_task_404(async_client: AsyncClient):
    resp = await async_client.get("/api/research/non_existent_id")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_evidence_and_report_endpoints(
    async_client: AsyncClient, db_session: AsyncSession
):
    repo = ResearchRepository(db_session)
    task = await repo.create_task("Claim with verified test report", {})
    await db_session.commit()

    # Evidence should be empty initially
    ev_resp = await async_client.get(f"/api/research/{task.id}/evidence")
    assert ev_resp.status_code == 200
    ev_data = ev_resp.json()
    assert ev_data["total_count"] == 0
    assert "counts_by_relationship" in ev_data

    # Report before creation should return 404
    rep_resp = await async_client.get(f"/api/research/{task.id}/report")
    assert rep_resp.status_code == 404

    # Save a report
    await repo.save_report(
        task_id=task.id,
        title="Test Report",
        executive_summary="Summary text",
        findings={},
        common_ground="Common ground text",
        uncertainty_and_gaps="Gaps text",
        methodology="Methodology text",
        limitations="Limitations text",
        citations=[],
    )
    await db_session.commit()

    # Report should now return 200
    rep_resp2 = await async_client.get(f"/api/research/{task.id}/report")
    assert rep_resp2.status_code == 200
    assert rep_resp2.json()["title"] == "Test Report"

    # Export endpoints
    export_md = await async_client.get(f"/api/research/{task.id}/export?format=md")
    assert export_md.status_code == 200
    assert "Test Report" in export_md.text

    export_json = await async_client.get(f"/api/research/{task.id}/export?format=json")
    assert export_json.status_code == 200
    assert export_json.json()["report"]["title"] == "Test Report"

    export_pdf = await async_client.get(f"/api/research/{task.id}/export?format=pdf")
    assert export_pdf.status_code == 200
    assert export_pdf.headers["content-type"] == "application/pdf"
