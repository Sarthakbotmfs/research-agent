import asyncio
import datetime
from typing import Dict, List, Optional

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from ..core.config import get_settings
from ..core.logging import get_logger
from .base import NormalizedSource, ScholarlySearchAdapter

logger = get_logger(__name__)


def reconstruct_openalex_abstract(inverted_index: Optional[Dict[str, List[int]]]) -> Optional[str]:
    """Reconstructs text from OpenAlex's abstract_inverted_index representation."""
    if not inverted_index or not isinstance(inverted_index, dict):
        return None
    try:
        word_positions: List[tuple[int, str]] = []
        for word, positions in inverted_index.items():
            for pos in positions:
                word_positions.append((pos, word))
        word_positions.sort(key=lambda x: x[0])
        reconstructed = " ".join(word for _, word in word_positions)
        return reconstructed.strip() or None
    except Exception as e:
        logger.warning(f"Failed to reconstruct OpenAlex abstract: {e}")
        return None


def clean_doi(raw_doi: Optional[str]) -> Optional[str]:
    if not raw_doi:
        return None
    cleaned = raw_doi.lower().strip()
    cleaned = (
        cleaned.removeprefix("https://doi.org/")
        .removeprefix("http://doi.org/")
        .removeprefix("doi:")
    )
    return cleaned.strip() or None


class OpenAlexAdapter(ScholarlySearchAdapter):
    BASE_URL = "https://api.openalex.org/works"

    def __init__(self, client: Optional[httpx.AsyncClient] = None):
        self.settings = get_settings()
        self._client = client
        self._rate_limiter = asyncio.Semaphore(5)  # Max concurrent requests to OpenAlex

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client and not self._client.is_closed:
            return self._client
        return httpx.AsyncClient(timeout=15.0)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=4),
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)),
        reraise=True,
    )
    async def _fetch_works(self, client: httpx.AsyncClient, query: str, limit: int) -> dict:
        headers = {
            "User-Agent": f"ResearchAgent/1.0 (mailto:{self.settings.OPENALEX_EMAIL})",
            "Accept": "application/json",
        }
        params = {
            "search": query,
            "per_page": min(limit, 25),
        }
        if self.settings.OPENALEX_EMAIL:
            params["mailto"] = self.settings.OPENALEX_EMAIL

        resp = await client.get(self.BASE_URL, params=params, headers=headers)
        if resp.status_code == 429:
            logger.warning("OpenAlex 429 Rate Limit encountered, waiting before retry")
        resp.raise_for_status()
        return resp.json()

    async def search(self, query: str, limit: int = 10) -> List[NormalizedSource]:
        client = await self._get_client()
        should_close = client != self._client

        async with self._rate_limiter:
            try:
                data = await self._fetch_works(client, query, limit)
            except Exception as e:
                logger.error(f"OpenAlex search error for query '{query}': {e}")
                return []
            finally:
                if should_close:
                    await client.aclose()

        results: List[NormalizedSource] = []
        raw_results = data.get("results", [])

        for item in raw_results:
            title = item.get("title")
            if not title:
                continue

            doi = clean_doi(item.get("doi"))
            canonical_url = (
                item.get("doi") or item.get("id") or f"https://openalex.org/{item.get('id', '')}"
            )

            # Extract authors
            authors = []
            for authorship in item.get("authorships", []):
                author_name = authorship.get("author", {}).get("display_name")
                if author_name:
                    authors.append(author_name)

            # Venue / Publication location
            venue = None
            primary_loc = item.get("primary_location") or {}
            source_info = primary_loc.get("source") or {}
            if source_info.get("display_name"):
                venue = source_info.get("display_name")

            # Source Type
            item_type = (item.get("type") or "unknown").lower()
            if item_type in ("journal-article", "article"):
                source_type = "peer-reviewed"
                is_peer = True
            elif item_type in ("proceedings-article", "conference"):
                source_type = "conference"
                is_peer = True
            elif item_type == "preprint":
                source_type = "preprint"
                is_peer = False
            elif item_type in ("book", "book-chapter"):
                source_type = "book"
                is_peer = True
            elif item_type == "review":
                source_type = "review"
                is_peer = True
            else:
                source_type = "unknown"
                is_peer = False

            # Open Access details
            open_access_info = item.get("open_access") or {}
            is_oa = open_access_info.get("is_oa", False)
            full_text_url = (
                open_access_info.get("oa_url")
                or primary_loc.get("pdf_url")
                or primary_loc.get("landing_page_url")
            )

            # Abstract
            abstract = reconstruct_openalex_abstract(item.get("abstract_inverted_index"))

            norm_source = NormalizedSource(
                doi=doi,
                canonical_url=canonical_url,
                title=title.strip(),
                authors=authors,
                venue=venue,
                year=item.get("publication_year"),
                source_type=source_type,
                is_peer_reviewed=is_peer,
                provenance="openalex",
                citation_count=item.get("cited_by_count", 0),
                open_access=bool(is_oa),
                abstract=abstract,
                full_text_url=full_text_url if is_oa else None,
                raw_metadata={
                    "id": item.get("id"),
                    "type": item_type,
                    "open_access": open_access_info,
                },
                retrieved_at=datetime.datetime.now(datetime.timezone.utc),
            )
            results.append(norm_source)

        return results
