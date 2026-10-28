import pytest
from pydantic import BaseModel

from app.providers.llm import (
    DiscoveryOnlyHeuristicProvider,
    LLMConfigurationError,
    OpenAICompatibleProvider,
    extract_json_block,
)
from app.schemas.llm_payloads import SubclaimPlanningOutput


class SampleModel(BaseModel):
    name: str
    count: int


def test_extract_json_block():
    raw_markdown = """```json
    {
      "name": "test_extraction",
      "count": 42
    }
    ```"""
    extracted = extract_json_block(raw_markdown)
    assert '"name": "test_extraction"' in extracted

    clean_json = '{"name": "direct", "count": 1}'
    assert extract_json_block(clean_json) == clean_json


@pytest.mark.asyncio
async def test_unconfigured_openai_provider_raises_error():
    provider = OpenAICompatibleProvider(api_key=None)
    assert await provider.is_available() is False

    with pytest.raises(LLMConfigurationError):
        await provider.generate_structured(
            prompt="Hello",
            system_prompt="Test",
            response_model=SampleModel,
        )


@pytest.mark.asyncio
async def test_discovery_only_heuristic_provider():
    provider = DiscoveryOnlyHeuristicProvider()
    assert await provider.is_available() is True

    result = await provider.generate_structured(
        prompt="AI coding assistants improve software developer productivity",
        system_prompt="",
        response_model=SubclaimPlanningOutput,
    )
    assert isinstance(result, SubclaimPlanningOutput)
    assert len(result.subclaims) > 0
    assert any("productivity" in sc.aspect.lower() for sc in result.subclaims)
    assert len(result.subclaims[0].search_queries) > 0
