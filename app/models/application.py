from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ApplicationRecord:
    application_id: str
    job_id: str
    portal: str
    portal_job_id: str
    company: str
    role: str
    url: str
    status: str = "DRAFT"
    match_score: int = 0
    resume: str | None = None
    automation_mode: str = "DRY_RUN"
    created_at: str = ""
    updated_at: str = ""
    reason: str = ""
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass
class ApplicationResult:
    application_id: str
    job_id: str
    status: str
    message: str
    automation_mode: str
    reason: str = ""
