from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SearchParams:
    roles: list[str] = field(default_factory=list)
    technologies: list[str] = field(default_factory=list)
    locations: list[str] = field(default_factory=list)
    experience_max: float | None = None
    employment_types: list[str] = field(default_factory=list)


class JobSource(ABC):
    """Contract for enabled sources. Implement only sources that permit automated access."""
    name: str

    @abstractmethod
    def fetch_jobs(self, search_params: SearchParams) -> list[dict[str, Any]]: ...

    @abstractmethod
    def parse_job(self, raw_job: dict[str, Any]) -> dict[str, Any]: ...

    @abstractmethod
    def normalize_job(self, job: dict[str, Any]) -> dict[str, Any]: ...

