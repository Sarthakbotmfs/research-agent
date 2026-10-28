import datetime
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T", bound=BaseModel)


class NormalizedSource(BaseModel):
    doi: Optional[str] = None
    canonical_url: str
    title: str
    authors: List[str] = Field(default_factory=list)
    venue: Optional[str] = None
    year: Optional[int] = None
    source_type: str = "unknown"
    is_peer_reviewed: bool = False
    provenance: str = "unknown"
    citation_count: int = 0
    open_access: bool = False
    abstract: Optional[str] = None
    full_text_url: Optional[str] = None
    raw_metadata: Dict[str, Any] = Field(default_factory=dict)
    retrieved_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc)
    )

    def normalize_doi(self) -> Optional[str]:
        if not self.doi:
            return None
        cleaned = self.doi.lower().strip()
        cleaned = (
            cleaned.removeprefix("https://doi.org/")
            .removeprefix("http://doi.org/")
            .removeprefix("doi:")
        )
        return cleaned.strip()


class ScholarlySearchAdapter(ABC):
    @abstractmethod
    async def search(self, query: str, limit: int = 10) -> List[NormalizedSource]:
        """Executes an asynchronous query and returns normalized scholarly records."""
        pass


class LLMProvider(ABC):
    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        system_prompt: str,
        response_model: Type[T],
    ) -> T:
        """Generates a validated structured Pydantic response from the LLM."""
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """Checks if the LLM provider has credentials and is reachable."""
        pass
