from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AuditEvent:
    kind: str
    status: str
    message: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RunState:
    name: str
    status: str = "QUEUED"
    current_step: str = "INITIALIZED"
    history: list[str] = field(default_factory=list)

    def advance(self, next_step: str) -> None:
        self.current_step = next_step
        self.history.append(next_step)

    def mark_started(self) -> None:
        self.status = "RUNNING"
        self.history.append("STARTED")

    def mark_completed(self) -> None:
        self.status = "COMPLETED"
        self.history.append("COMPLETED")


@dataclass
class WorkflowState:
    job_id: str
    status: str = "QUEUED"
    current_step: str = "DISCOVERY"
    history: list[str] = field(default_factory=list)

    def advance(self, next_step: str) -> None:
        self.current_step = next_step
        self.history.append(next_step)
        self.status = "IN_PROGRESS"

    def mark_started(self) -> None:
        self.status = "RUNNING"
        self.history.append("STARTED")

    def mark_completed(self) -> None:
        self.status = "COMPLETED"
        self.history.append("COMPLETED")
