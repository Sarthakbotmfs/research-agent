import pytest
from pydantic import ValidationError

from app.schemas.research import TaskConfigSchema, TaskCreateRequest


def test_valid_claim():
    req = TaskCreateRequest(claim="AI coding assistants improve software developer productivity.")
    assert req.claim == "AI coding assistants improve software developer productivity."
    assert req.config.max_rounds == 3
    assert req.config.max_queries == 15


def test_claim_too_short():
    with pytest.raises(ValidationError) as exc:
        TaskCreateRequest(claim="Too short")
    assert "at least 10" in str(exc.value).lower()


def test_claim_empty_whitespace():
    with pytest.raises(ValidationError) as exc:
        TaskCreateRequest(claim="          ")
    assert "at least 10" in str(exc.value).lower()


def test_config_bounds():
    # Valid custom limits
    config = TaskConfigSchema(max_rounds=5, max_queries=25, max_sources=50)
    assert config.max_rounds == 5
    assert config.max_queries == 25

    # Out of bounds max_rounds (> 5)
    with pytest.raises(ValidationError):
        TaskConfigSchema(max_rounds=10)

    # Out of bounds max_queries (< 1)
    with pytest.raises(ValidationError):
        TaskConfigSchema(max_queries=0)
