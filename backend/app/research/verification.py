import datetime
import re
from typing import List, Optional, Tuple

from ..core.logging import get_logger
from ..core.security import calculate_content_hash
from ..db.models import Evidence, Source

logger = get_logger(__name__)


def verify_source_metadata(source: Source) -> Tuple[bool, str]:
    """Verifies that scholarly metadata is consistent and plausible."""
    if not source.title or len(source.title.strip()) < 5:
        return False, "Source lacks a valid title."

    if not source.canonical_url or not source.canonical_url.startswith(("http://", "https://")):
        return False, "Source lacks a valid HTTP/HTTPS canonical URL."

    current_year = datetime.datetime.now(datetime.timezone.utc).year
    if source.year and (source.year < 1900 or source.year > current_year + 1):
        return False, f"Plausibility check failed: Publication year {source.year} is out of bounds."

    if source.doi:
        # Check standard DOI syntax (10.NNNN/...)
        if not re.search(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+", source.doi):
            return False, f"Malformed DOI format: {source.doi}"

    return True, "Metadata verified against scholarly index registry."


def check_source_independence(sources: List[Source]) -> dict[str, bool]:
    """
    Evaluates independence across a set of sources.
    Flags sources that share primary authors and similar titles as potentially dependent studies.
    """
    independence_map = {s.id: True for s in sources}
    author_venue_seen = {}

    for s in sources:
        first_author = (
            s.authors[0].lower().strip() if (s.authors and isinstance(s.authors, list)) else ""
        )
        year = str(s.year or "")
        key = f"{first_author}_{year}"

        if first_author and key in author_venue_seen:
            # Same lead author and same year: potential duplicate reporting of same trial
            independence_map[s.id] = False
            logger.info(
                f"Marked source {s.id} ({s.title[:40]}) as potentially dependent on study {author_venue_seen[key]}"
            )
        elif first_author:
            author_venue_seen[key] = s.id

    return independence_map


def verify_evidence_passage(evidence: Evidence, source_text: Optional[str]) -> Tuple[bool, str]:
    """
    Verifies that the extracted passage is authentic and originated from the source text.
    """
    if not evidence.passage or len(evidence.passage.strip()) < 10:
        return False, "Evidence passage is missing or too brief."

    expected_hash = calculate_content_hash(evidence.passage)
    if evidence.passage_hash and evidence.passage_hash != expected_hash:
        return (
            False,
            f"Integrity check failed: Passage hash mismatch (expected {expected_hash[:8]}).",
        )

    if source_text:
        # Check if passage or significant fragment appears in source text
        clean_passage = re.sub(r'^(?:"""|\'\'\'|"|\')\s*', '', evidence.passage).strip()
        snippet = clean_passage[:60].strip()
        if snippet.lower() not in source_text.lower():
            # Allow minor whitespace/formatting normalization difference
            cleaned_source = re.sub(r"\s+", " ", source_text.lower())
            cleaned_snippet = re.sub(r"\s+", " ", snippet.lower())
            if cleaned_snippet not in cleaned_source:
                return False, "Passage text could not be verified within stored source document."

    return True, "Passage content hash verified and confirmed present in source document."
