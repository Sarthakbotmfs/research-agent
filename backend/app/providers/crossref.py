import asyncio
import datetime
import re
from typing import List, Optional

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from ..core.config import get_settings
from ..core.logging import get_logger
from .base import NormalizedSource, ScholarlySearchAdapter

logger = get_logger(__name__)

XML_TAG_PATTERN = re.compile(r"<[^>]+>")


def strip_xml_tags(text: Optional[str]) -> Optional[str]:
    if not text:
        return None
    cleaned = XML_TAG_PATTERN.sub(" ", text)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned or None


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


class CrossrefAdapter(ScholarlySearchAdapter):
    BASE_URL = "https://api.crossref.org/works"

    def __init__(self, client: Optional[httpx.AsyncClient] = None):
        self.settings = get_settings()
        self._client = client
        self._rate_limiter = asyncio.Semaphore(5)

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
            "User-Agent": f"ResearchAgent/1.0 (mailto:{self.settings.CROSSREF_MAILTO})",
            "Accept": "application/json",
        }
        params = {
            "query": query,
            "rows": min(limit, 25),
        }
        resp = await client.get(self.BASE_URL, params=params, headers=headers)
        if resp.status_code == 429:
            logger.warning("Crossref 429 Rate Limit encountered, backing off")
        resp.raise_for_status()
        return resp.json()

    async def search(self, query: str, limit: int = 10) -> List[NormalizedSource]:
        client = await self._get_client()
        should_close = client != self._client

        async with self._rate_limiter:
            try:
                data = await self._fetch_works(client, query, limit)
            except Exception as e:
                logger.error(f"Crossref search error for query '{query}': {e}")
                return []
            finally:
                if should_close:
                    await client.aclose()

        results: List[NormalizedSource] = []
        items = data.get("message", {}).get("items", [])

        for item in items:
            raw_title = item.get("title", [])
            title = raw_title[0] if (isinstance(raw_title, list) and raw_title) else raw_title
            if not title or not isinstance(title, str):
                continue

            doi = clean_doi(item.get("DOI"))
            canonical_url = item.get("URL") or (f"https://doi.org/{doi}" if doi else "")
            if not canonical_url:
                continue

            # Extract authors
            authors: List[str] = []
            for author_obj in item.get("author", []):
                given = author_obj.get("given", "")
                family = author_obj.get("family", "")
                full = f"{given} {family}".strip() or author_obj.get("name", "")
                if full:
                    authors.append(full)

            # Venue
            container = item.get("container-title", [])
            venue = container[0] if (isinstance(container, list) and container) else None

            # Year extraction from issued / published-print / published-online
            year = None
            for date_key in ("published-print", "published-online", "issued", "created"):
                date_parts = item.get(date_key, {}).get("date-parts", [])
                if date_parts and date_parts[0] and isinstance(date_parts[0][0], int):
                    year = date_parts[0][0]
                    break

            # Source Type
            raw_type = (item.get("type") or "unknown").lower()
            if raw_type in ("journal-article", "article"):
                source_type = "peer-reviewed"
                is_peer = True
            elif raw_type in ("proceedings-article", "conference-paper"):
                source_type = "conference"
                is_peer = True
            elif raw_type in ("posted-content", "preprint"):
                source_type = "preprint"
                is_peer = False
            elif raw_type in ("book", "book-chapter"):
                source_type = "book"
                is_peer = True
            else:
                source_type = "unknown"
                is_peer = False

            # Abstract
            abstract = strip_xml_tags(item.get("abstract"))

            # Link / Open Access
            full_text_url = None
            links = item.get("link", [])
            if isinstance(links, list):
                for link_item in links:
                    if link_item.get("content-type") == "application/pdf" or "pdf" in link_item.get("URL", ""):
                        full_text_url = link_item.get("URL")
                        break

            norm_source = NormalizedSource(
                doi=doi,
                canonical_url=canonical_url,
                title=title.strip(),
                authors=authors,
                venue=venue,
                year=year,
                source_type=source_type,
                is_peer_reviewed=is_peer,
                provenance="crossref",
                citation_count=item.get("is-referenced-by-count", 0),
                open_access=bool(full_text_url),
                abstract=abstract,
                full_text_url=full_text_url,
                raw_metadata={
                    "type": raw_type,
                    "publisher": item.get("publisher"),
                },
                retrieved_at=datetime.datetime.now(datetime.timezone.utc),
            )
            results.append(norm_source)

        return results
