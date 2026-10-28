from app.core.security import calculate_content_hash
from app.db.models import Evidence, Source
from app.research.verification import (
    check_source_independence,
    verify_evidence_passage,
    verify_source_metadata,
)
from app.schemas.enums import EvidenceRelationshipEnum


def test_evidence_classification_enums():
    assert EvidenceRelationshipEnum.SUPPORTS == "supports"
    assert EvidenceRelationshipEnum.CONTRADICTS == "contradicts"
    assert EvidenceRelationshipEnum.MIXED == "mixed"
    assert EvidenceRelationshipEnum.CONTEXT == "context"
    assert EvidenceRelationshipEnum.INSUFFICIENT == "insufficient"


def test_verify_source_metadata():
    valid_source = Source(
        id="s1",
        title="Valid Academic Publication Title",
        canonical_url="https://doi.org/10.1145/1234567",
        doi="10.1145/1234567",
        year=2024,
    )
    is_valid, msg = verify_source_metadata(valid_source)
    assert is_valid is True

    # Empty title
    bad_source = Source(
        id="s2",
        title="   ",
        canonical_url="https://example.org",
        year=2024,
    )
    is_valid, _ = verify_source_metadata(bad_source)
    assert is_valid is False

    # Out of bounds year
    bad_year_source = Source(
        id="s3",
        title="Future Sci-Fi Paper",
        canonical_url="https://example.org",
        year=2099,
    )
    is_valid, msg = verify_source_metadata(bad_year_source)
    assert is_valid is False
    assert "year" in msg.lower()


def test_verify_evidence_passage():
    source_full = "Our empirical controlled experiment demonstrated a 34% reduction in completion time for routine tasks."
    passage = "demonstrated a 34% reduction in completion time"
    phash = calculate_content_hash(passage)

    ev = Evidence(
        id="e1",
        task_id="t1",
        subclaim_id="sc1",
        source_id="s1",
        relationship="supports",
        passage=passage,
        passage_hash=phash,
        rationale="Clear effect size measured",
        confidence_score=0.9,
    )

    is_valid, msg = verify_evidence_passage(ev, source_full)
    assert is_valid is True

    # Tampered passage hash
    ev_tampered = Evidence(
        id="e2",
        task_id="t1",
        subclaim_id="sc1",
        source_id="s1",
        relationship="supports",
        passage=passage,
        passage_hash="tampered_hash_12345",
        rationale="Tampered",
        confidence_score=0.9,
    )
    is_valid, msg = verify_evidence_passage(ev_tampered, source_full)
    assert is_valid is False
    assert "mismatch" in msg.lower()


def test_check_source_independence():
    s1 = Source(
        id="s1",
        title="Study on LLM code generation",
        authors=["Smith, J.", "Doe, A."],
        year=2023,
        canonical_url="https://example.com/1",
    )
    s2 = Source(
        id="s2",
        title="Further notes on LLM code generation",
        authors=["Smith, J.", "Johnson, R."],
        year=2023,
        canonical_url="https://example.com/2",
    )
    s3 = Source(
        id="s3",
        title="Independent replication of LLM productivity",
        authors=["Taylor, M."],
        year=2024,
        canonical_url="https://example.com/3",
    )

    indep_map = check_source_independence([s1, s2, s3])
    assert indep_map["s1"] is True
    assert indep_map["s2"] is False  # Same first author, same year -> flagged as dependent
    assert indep_map["s3"] is True
