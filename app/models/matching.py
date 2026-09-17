from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class MatchResult:
    job_id: str
    match_score: int
    recommendation: str
    eligible: bool
    matching_skills: list[str] = field(default_factory=list)
    missing_required_skills: list[str] = field(default_factory=list)
    missing_preferred_skills: list[str] = field(default_factory=list)
    reasoning: str = ""
    role_match: bool = True
    experience_match: bool = True
    location_match: bool = True
    experience_gap: str | None = None
    concerns: list[str] = field(default_factory=list)


@dataclass
class PolicyDecision:
    eligible: bool
    reason: str
    policy_version: str = "v1"
