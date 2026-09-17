from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.models.job import Job


class JobRepository:
    def __init__(self, storage_path: str | Path | None = None) -> None:
        self.storage_path = Path(storage_path) if storage_path else Path("data/jobs.json")
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage_path.exists():
            self.storage_path.write_text(json.dumps({"jobs": []}), encoding="utf-8")

    def _read_all(self) -> list[dict[str, Any]]:
        data = json.loads(self.storage_path.read_text(encoding="utf-8"))
        return data.get("jobs", [])

    def _write_all(self, jobs: list[dict[str, Any]]) -> None:
        self.storage_path.write_text(json.dumps({"jobs": jobs}, indent=2), encoding="utf-8")

    def save(self, job: Job) -> Job:
        all_jobs = self._read_all()
        if self.is_duplicate(job):
            return job
        all_jobs.append(
            {
                "portal": job.portal,
                "portal_job_id": job.portal_job_id,
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "description": job.description,
                "posted_at": job.posted_at,
                "url": job.url,
                "status": job.status,
                "fingerprint": job.fingerprint,
                "discovered_at": job.discovered_at,
                "metadata": job.metadata,
            }
        )
        self._write_all(all_jobs)
        return job

    def exists(self, portal_and_id: str) -> bool:
        for item in self._read_all():
            if f"{item.get('portal')}:{item.get('portal_job_id')}" == portal_and_id:
                return True
        return False

    def is_duplicate(self, job: Job) -> bool:
        for item in self._read_all():
            if item.get("portal") == job.portal and item.get("portal_job_id") == job.portal_job_id:
                return True
            if item.get("fingerprint") == job.fingerprint:
                return True
        return False

    def get_all(self) -> list[Job]:
        jobs: list[Job] = []
        for item in self._read_all():
            jobs.append(
                Job(
                    portal=item["portal"],
                    portal_job_id=item["portal_job_id"],
                    title=item["title"],
                    company=item["company"],
                    location=item["location"],
                    description=item.get("description", ""),
                    posted_at=item["posted_at"],
                    url=item["url"],
                    status=item.get("status", "DISCOVERED"),
                    fingerprint=item.get("fingerprint", ""),
                    discovered_at=item.get("discovered_at", item["posted_at"]),
                    metadata=item.get("metadata", {}),
                )
            )
        return jobs
