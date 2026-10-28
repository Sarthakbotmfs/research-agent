import httpx
import pytest
import respx

from app.providers.crossref import CrossrefAdapter, strip_xml_tags
from app.providers.openalex import OpenAlexAdapter, reconstruct_openalex_abstract


def test_reconstruct_openalex_abstract():
    inverted_index = {
        "AI": [0],
        "coding": [1],
        "assistants": [2],
        "improve": [3],
        "developer": [4],
        "speed": [5],
    }
    abstract = reconstruct_openalex_abstract(inverted_index)
    assert abstract == "AI coding assistants improve developer speed"

    assert reconstruct_openalex_abstract(None) is None
    assert reconstruct_openalex_abstract({}) is None


def test_strip_xml_tags():
    raw_abstract = "<jats:p>This study evaluates <jats:italic>developer efficiency</jats:italic> using Copilot.</jats:p>"
    stripped = strip_xml_tags(raw_abstract)
    assert stripped == "This study evaluates developer efficiency using Copilot."
    assert strip_xml_tags(None) is None


@pytest.mark.asyncio
async def test_openalex_adapter_search():
    adapter = OpenAlexAdapter()

    fake_openalex_response = {
        "results": [
            {
                "id": "https://openalex.org/W123456789",
                "doi": "https://doi.org/10.1145/1234567",
                "title": "An Empirical Evaluation of AI Coding Assistants",
                "publication_year": 2024,
                "type": "journal-article",
                "cited_by_count": 42,
                "authorships": [
                    {"author": {"display_name": "Alice Smith"}},
                    {"author": {"display_name": "Bob Jones"}},
                ],
                "primary_location": {
                    "source": {"display_name": "ACM Transactions on Software Engineering"},
                    "pdf_url": "https://example.org/paper.pdf",
                    "landing_page_url": "https://example.org/landing",
                },
                "open_access": {
                    "is_oa": True,
                    "oa_url": "https://example.org/paper.pdf",
                },
                "abstract_inverted_index": {
                    "We": [0],
                    "find": [1],
                    "productivity": [2],
                    "gains": [3],
                    "of": [4],
                    "26%": [5],
                },
            }
        ]
    }

    async with httpx.AsyncClient() as client:
        with respx.mock(base_url="https://api.openalex.org") as respx_mock:
            respx_mock.get("/works").respond(status_code=200, json=fake_openalex_response)
            adapter._client = client

            results = await adapter.search("AI coding assistants", limit=5)
            assert len(results) == 1
            src = results[0]
            assert src.doi == "10.1145/1234567"
            assert src.title == "An Empirical Evaluation of AI Coding Assistants"
            assert src.year == 2024
            assert src.source_type == "peer-reviewed"
            assert src.is_peer_reviewed is True
            assert src.provenance == "openalex"
            assert src.authors == ["Alice Smith", "Bob Jones"]
            assert src.venue == "ACM Transactions on Software Engineering"
            assert src.abstract == "We find productivity gains of 26%"
            assert src.open_access is True


@pytest.mark.asyncio
async def test_crossref_adapter_search():
    adapter = CrossrefAdapter()

    fake_crossref_response = {
        "message": {
            "items": [
                {
                    "DOI": "10.1109/TSE.2023.99999",
                    "URL": "https://doi.org/10.1109/TSE.2023.99999",
                    "title": ["Developer Experience and Code Quality Under LLM Assistance"],
                    "type": "proceedings-article",
                    "is-referenced-by-count": 19,
                    "author": [
                        {"given": "Charlie", "family": "Brown"},
                    ],
                    "container-title": ["IEEE Software Engineering Conference"],
                    "issued": {"date-parts": [[2023, 5, 15]]},
                    "abstract": "<jats:p>Defect density was investigated across 500 tasks.</jats:p>",
                    "link": [
                        {"URL": "https://ieee.org/doc.pdf", "content-type": "application/pdf"}
                    ],
                }
            ]
        }
    }

    async with httpx.AsyncClient() as client:
        with respx.mock(base_url="https://api.crossref.org") as respx_mock:
            respx_mock.get("/works").respond(status_code=200, json=fake_crossref_response)
            adapter._client = client

            results = await adapter.search("code quality developer experience", limit=5)
            assert len(results) == 1
            src = results[0]
            assert src.doi == "10.1109/tse.2023.99999"
            assert src.title == "Developer Experience and Code Quality Under LLM Assistance"
            assert src.year == 2023
            assert src.source_type == "conference"
            assert src.is_peer_reviewed is True
            assert src.provenance == "crossref"
            assert src.authors == ["Charlie Brown"]
            assert src.abstract == "Defect density was investigated across 500 tasks."


@pytest.mark.asyncio
async def test_search_adapter_rate_limit_and_error_handling():
    adapter = OpenAlexAdapter()

    async with httpx.AsyncClient() as client:
        with respx.mock(base_url="https://api.openalex.org") as respx_mock:
            # Persistent 500 error
            respx_mock.get("/works").respond(status_code=500)
            adapter._client = client

            # Should return empty list gracefully without throwing an uncaught exception
            results = await adapter.search("fail query")
            assert results == []
