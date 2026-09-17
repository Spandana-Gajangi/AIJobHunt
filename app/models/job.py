from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ApplicationStatus(str, Enum):
    DISCOVERED = "DISCOVERED"
    MATCHED = "MATCHED"
    ELIGIBLE = "ELIGIBLE"
    APPLICATION_STARTED = "APPLICATION_STARTED"
    APPLIED = "APPLIED"
    EMAIL_RECEIVED = "EMAIL_RECEIVED"
    ACTION_REQUIRED = "ACTION_REQUIRED"
    USER_NOTIFIED = "USER_NOTIFIED"
    REPLIED = "REPLIED"
    INTERVIEW = "INTERVIEW"
    OFFER = "OFFER"
    REJECTED = "REJECTED"
    SKIPPED = "SKIPPED"
    FAILED = "FAILED"


class PortalStatus(str, Enum):
    DISCOVERED = "DISCOVERED"
    VALIDATED = "VALIDATED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"


@dataclass
class JobRecord:
    source: str
    title: str
    company: str
    url: str
    status: ApplicationStatus = ApplicationStatus.DISCOVERED
    match_score: int = 0
    location: str | None = None
    notes: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PortalDefinition:
    name: str
    enabled: bool
    adapter: str
    status: PortalStatus = PortalStatus.ENABLED

    def __post_init__(self) -> None:
        if self.enabled:
            self.status = PortalStatus.ENABLED
        else:
            self.status = PortalStatus.DISABLED


@dataclass
class JobSearchCriteria:
    keywords: list[str] = field(default_factory=list)
    locations: list[str] = field(default_factory=list)
    experience_min: int | None = None
    experience_max: int | None = None
    posted_after: str | None = None
    days_back: int | None = None


@dataclass
class RawJob:
    source: str
    raw_id: str
    raw_title: str
    raw_company: str
    raw_location: str
    raw_description: str
    raw_posted_date: str
    raw_url: str
    raw_metadata: dict[str, Any] = field(default_factory=dict)


def _normalize_fingerprint_value(value: str) -> str:
    cleaned = value.lower().strip()
    cleaned = cleaned.replace("&", "and")
    cleaned = "".join(ch for ch in cleaned if ch.isalnum() or ch.isspace() or ch in {",", "-"})
    cleaned = cleaned.replace(",", " ")
    cleaned = " ".join(cleaned.split())
    if cleaned.endswith(" telangana"):
        cleaned = cleaned[: -len(" telangana")]
    return cleaned


@dataclass
class Job:
    portal: str
    portal_job_id: str
    title: str
    company: str
    location: str
    description: str
    posted_at: str
    url: str
    status: str = "DISCOVERED"
    fingerprint: str = ""
    discovered_at: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        normalized_company = _normalize_fingerprint_value(self.company)
        normalized_title = _normalize_fingerprint_value(self.title)
        normalized_location = _normalize_fingerprint_value(self.location)
        self.fingerprint = f"{normalized_company}|{normalized_title}|{normalized_location}"
        if not self.discovered_at:
            self.discovered_at = self.posted_at
