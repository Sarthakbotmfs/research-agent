from enum import Enum


class TaskStatusEnum(str, Enum):
    PENDING = "pending"
    PLANNING = "planning"
    SEARCHING = "searching"
    EXTRACTING = "extracting"
    CLASSIFYING = "classifying"
    VERIFYING = "verifying"
    SYNTHESIZING = "synthesizing"
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"


class EvidenceRelationshipEnum(str, Enum):
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    MIXED = "mixed"
    CONTEXT = "context"
    INSUFFICIENT = "insufficient"


class SourceTypeEnum(str, Enum):
    PEER_REVIEWED = "peer-reviewed"
    PREPRINT = "preprint"
    CONFERENCE = "conference"
    REVIEW = "review"
    BOOK = "book"
    REPORT = "report"
    UNKNOWN = "unknown"
