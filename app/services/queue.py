from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Any

from app.models.workflow import AuditEvent, RunState


class InMemoryQueue:
    def __init__(self) -> None:
        self._queue: deque[dict[str, Any]] = deque()
        self._seen: set[str] = set()

    def enqueue(self, item: dict[str, Any]) -> bool:
        job_id = str(item.get("job_id") or item.get("id") or item.get("key") or "")
        if job_id and job_id in self._seen:
            return False
        self._queue.append(item)
        if job_id:
            self._seen.add(job_id)
        return True

    def dequeue(self) -> dict[str, Any] | None:
        if not self._queue:
            return None
        item = self._queue.popleft()
        job_id = str(item.get("job_id") or item.get("id") or item.get("key") or "")
        if job_id:
            self._seen.discard(job_id)
        return item

    def pending_count(self) -> int:
        return len(self._queue)


@dataclass
class JobCollectionWorker:
    queue: InMemoryQueue | None = None

    def run_once(self) -> str | None:
        queue = self.queue or InMemoryQueue()
        item = queue.dequeue()
        if item is None:
            return None
        return str(item.get("job_id") or item.get("id") or item.get("key") or "")


@dataclass
class ApplicationWorker:
    def process(self, payload: dict[str, Any], state: RunState) -> AuditEvent:
        state.advance("APPLICATION")
        state.mark_started()
        state.mark_completed()
        return AuditEvent(
            kind="application",
            status="SUCCESS",
            message=f"Processed application for {payload.get('job_id')}",
            metadata={"job_id": payload.get("job_id")},
        )
