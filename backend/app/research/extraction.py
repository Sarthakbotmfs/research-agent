import re
from typing import Optional, Tuple

import httpx

from ..core.limits import ResourceUsage
from ..core.logging import get_logger
from ..core.security import calculate_content_hash, is_safe_url, safe_fetch_url
from ..providers.base import NormalizedSource

logger = get_logger(__name__)


def clean_extracted_text(text: str) -> str:
    """Removes excessive whitespace and HTML/script artifacts."""
    # Basic script/style tag removal if HTML
    text = re.sub(r"<script[\s\S]*?</script>", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


class PassageExtractor:
    def __init__(self, client: Optional[httpx.AsyncClient] = None):
        self._client = client

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client and not self._client.is_closed:
            return self._client
        return httpx.AsyncClient(timeout=10.0)

    async def extract_source_content(
        self,
        source: NormalizedSource,
        usage: ResourceUsage,
        allow_full_text: bool = True,
    ) -> Tuple[str, str, str]:
        """
        Extracts content from a NormalizedSource.
        Returns (content_text, extraction_status, content_hash).
        extraction_status is one of: "abstract_only", "full_text_extracted", "metadata_only".
        """
        # If full text fetch is permitted and source has open access URL
        if (
            allow_full_text
            and source.open_access
            and source.full_text_url
            and usage.can_fetch_page()
        ):
            safe, reason = is_safe_url(source.full_text_url)
            if safe:
                client = await self._get_client()
                should_close = client != self._client
                try:
                    usage.record_page_fetch()
                    raw_text, chash = await safe_fetch_url(
                        client=client,
                        url=source.full_text_url,
                        max_size_bytes=1_500_000,
                        timeout=8.0,
                    )
                    cleaned = clean_extracted_text(raw_text)
                    if len(cleaned) > 200:
                        logger.info(
                            f"Successfully extracted open-access full text for: {source.title[:50]}"
                        )
                        return cleaned, "full_text_extracted", chash
                except Exception as e:
                    logger.warning(f"Could not fetch full text for {source.canonical_url}: {e}")
                finally:
                    if should_close:
                        await client.aclose()

        # Fallback to abstract if available
        if source.abstract and source.abstract.strip():
            abstract_text = clean_extracted_text(source.abstract)
            chash = calculate_content_hash(abstract_text)
            return abstract_text, "abstract_only", chash

        # Fallback to title and metadata
        meta_text = f"Title: {source.title}. Venue: {source.venue or 'Unknown'}. Year: {source.year or 'Unknown'}."
        chash = calculate_content_hash(meta_text)
        return meta_text, "metadata_only", chash
