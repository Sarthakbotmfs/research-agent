import datetime
from typing import Any, Dict

from pydantic import BaseModel, Field


class ResearchEventResponse(BaseModel):
    id: str
    seq: int
    task_id: str
    stage: str
    event_type: str
    message: str
    data: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime.datetime
