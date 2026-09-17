from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CandidateProfile:
    experience_years: int = 0
    skills: list[str] = field(default_factory=list)
    preferred_roles: list[str] = field(default_factory=list)
    preferred_locations: list[str] = field(default_factory=list)
    target_companies: list[str] = field(default_factory=list)
    work_mode: str | None = None
    resume_path: str | None = None
    email: str | None = None
    phone: str | None = None
    name: str | None = None
