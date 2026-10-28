import time
from dataclasses import dataclass, field


@dataclass
class ExecutionLimits:
    max_rounds: int = 3
    max_queries: int = 15
    max_sources: int = 40
    max_page_fetches: int = 20
    task_timeout_seconds: float = 600.0  # 10 minutes
    concurrency_limit: int = 4


@dataclass
class ResourceUsage:
    limits: ExecutionLimits = field(default_factory=ExecutionLimits)
    rounds_completed: int = 0
    queries_executed: int = 0
    unique_sources_count: int = 0
    page_fetches_count: int = 0
    start_time: float = field(default_factory=time.time)

    def elapsed_seconds(self) -> float:
        return time.time() - self.start_time

    def is_time_exceeded(self) -> bool:
        return self.elapsed_seconds() >= self.limits.task_timeout_seconds

    def can_start_round(self) -> bool:
        if self.is_time_exceeded():
            return False
        return self.rounds_completed < self.limits.max_rounds

    def can_execute_query(self) -> bool:
        if self.is_time_exceeded():
            return False
        return self.queries_executed < self.limits.max_queries

    def can_add_source(self) -> bool:
        return self.unique_sources_count < self.limits.max_sources

    def can_fetch_page(self) -> bool:
        if self.is_time_exceeded():
            return False
        return self.page_fetches_count < self.limits.max_page_fetches

    def record_query(self) -> None:
        self.queries_executed += 1

    def record_round(self) -> None:
        self.rounds_completed += 1

    def record_page_fetch(self) -> None:
        self.page_fetches_count += 1

    def set_sources_count(self, count: int) -> None:
        self.unique_sources_count = count
