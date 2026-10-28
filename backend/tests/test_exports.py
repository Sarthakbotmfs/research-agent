import pytest

from app.db.models import Evidence, Report, ResearchTask, Source, Subclaim
from app.exports.json_export import generate_json_export
from app.exports.markdown_export import generate_markdown_report
from app.exports.pdf_export import generate_pdf_report


@pytest.fixture
def sample_research_records():
    task = ResearchTask(
        id="task_123",
        claim="AI coding assistants improve software developer productivity.",
        status="completed",
        config={"max_rounds": 3},
    )
    sc = Subclaim(
        id="sc_1",
        task_id="task_123",
        subclaim_text="Developer speed is increased during coding tasks.",
        aspect="productivity",
        status="evaluated",
    )
    src = Source(
        id="src_1",
        doi="10.1145/12345",
        canonical_url="https://doi.org/10.1145/12345",
        title="Empirical Evaluation of Copilot",
        authors=["Alice Researcher"],
        year=2024,
        venue="ACM Transactions",
        source_type="peer-reviewed",
        is_peer_reviewed=True,
    )
    ev = Evidence(
        id="ev_1",
        task_id="task_123",
        subclaim_id="sc_1",
        source_id="src_1",
        relationship="supports",
        passage="Developers using the assistant finished tasks 30% faster.",
        passage_hash="hash123",
        rationale="Controlled randomized trial measuring task completion time.",
        limitations="Sample composed of junior developers only.",
        confidence_score=0.88,
        verification_status="verified",
        is_independent=True,
    )
    report = Report(
        id="rep_1",
        task_id="task_123",
        title="Automated Research Report: AI Assistant Productivity",
        executive_summary="The synthesis indicates measurable task acceleration with quality caveats.",
        findings={"subclaim_findings": []},
        common_ground="Accelerates boilerplate tasks across studies.",
        uncertainty_and_gaps="Maintenance cost over 5-year lifecycles remains unstudied.",
        methodology="Systematic retrieval via OpenAlex and Crossref.",
        limitations="Abstract and open access retrieval only.",
        citations=[{"citation_id": "ref_1", "source_id": "src_1", "title": src.title}],
        status="complete",
    )
    return task, [sc], [src], [ev], report


def test_generate_markdown_report(sample_research_records):
    task, subclaims, sources, evidence, report = sample_research_records
    md = generate_markdown_report(task, subclaims, sources, evidence, report)

    assert "# Automated Research Report: AI Assistant Productivity" in md
    assert "Executive Summary" in md
    assert "Common Ground & Academic Consensus" in md
    assert "Validated References" in md
    assert "Developers using the assistant finished tasks 30% faster." in md
    assert "Alice Researcher" in md


def test_generate_json_export(sample_research_records):
    task, subclaims, sources, evidence, report = sample_research_records
    dossier = generate_json_export(task, subclaims, sources, evidence, report)

    assert dossier["export_metadata"]["format"] == "research_agent_dossier"
    assert dossier["task"]["id"] == "task_123"
    assert len(dossier["subclaims"]) == 1
    assert len(dossier["sources"]) == 1
    assert len(dossier["evidence"]) == 1
    assert dossier["report"]["title"] == "Automated Research Report: AI Assistant Productivity"


def test_generate_pdf_report(sample_research_records):
    task, subclaims, sources, evidence, report = sample_research_records
    pdf_bytes = generate_pdf_report(task, subclaims, sources, evidence, report)

    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 500
    assert pdf_bytes.startswith(b"%PDF-")  # Valid PDF signature
