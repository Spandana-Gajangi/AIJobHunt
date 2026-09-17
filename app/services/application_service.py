from __future__ import annotations

from datetime import datetime, timezone

from app.models.application import ApplicationResult
from app.models.candidate import CandidateProfile
from app.models.job import Job


class ApplicationService:
    def __init__(self, dry_run: bool = True) -> None:
        self.dry_run = dry_run
        self._applications: dict[str, str] = {}

    def prepare_application(self, candidate: CandidateProfile, job: Job) -> ApplicationResult:
        job_key = f"{job.portal}:{job.portal_job_id}"
        if job_key in self._applications:
            return ApplicationResult(
                application_id=self._applications[job_key],
                job_id=job_key,
                status="DUPLICATE",
                message="Application already exists for this job",
                automation_mode="DRY_RUN" if self.dry_run else "AUTO",
                reason="Application already exists for this job",
            )

        application_id = f"app_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        self._applications[job_key] = application_id

        if self.dry_run:
            return ApplicationResult(
                application_id=application_id,
                job_id=job_key,
                status="DRY_RUN_READY",
                message="Application prepared in dry-run mode",
                automation_mode="DRY_RUN",
                reason="Preview generated without submission",
            )

        return ApplicationResult(
            application_id=application_id,
            job_id=job_key,
            status="READY_FOR_SUBMISSION",
            message="Application prepared for submission",
            automation_mode="AUTO",
            reason="All validation checks passed",
        )
