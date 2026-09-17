from __future__ import annotations

from typing import Iterable

from app.models.job import Job, RawJob


class JobDiscoveryService:
    def normalize_jobs(self, raw_jobs: Iterable[RawJob]) -> list[Job]:
        jobs: list[Job] = []
        for raw in raw_jobs:
            job = Job(
                portal=raw.source,
                portal_job_id=raw.raw_id,
                title=raw.raw_title,
                company=raw.raw_company,
                location=raw.raw_location,
                description=raw.raw_description,
                posted_at=raw.raw_posted_date,
                url=raw.raw_url,
                status="DISCOVERED",
                metadata={"source": raw.source, **raw.raw_metadata},
            )
            jobs.append(job)
        return jobs

    def deduplicate_jobs(self, jobs: Iterable[Job]) -> list[Job]:
        seen_by_portal_id: set[str] = set()
        seen_by_fingerprint: set[str] = set()
        deduped: list[Job] = []
        for job in jobs:
            portal_identity = f"{job.portal}:{job.portal_job_id}"
            if portal_identity in seen_by_portal_id or job.fingerprint in seen_by_fingerprint:
                continue
            seen_by_portal_id.add(portal_identity)
            seen_by_fingerprint.add(job.fingerprint)
            deduped.append(job)
        return deduped
