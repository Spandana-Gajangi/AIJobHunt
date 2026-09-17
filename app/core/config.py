from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    app_name: str = "jobhunt"
    storage_path: str = field(default_factory=lambda: str(Path("data").resolve()))
    dry_run: bool = True
    cron_schedule: str = "0 */6 * * *"
    candidate_profile_path: str = "data/candidate_profile.json"


def get_settings() -> Settings:
    """Return the default local configuration for the Phase 0 foundation."""
    return Settings()
