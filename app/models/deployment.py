from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class DeploymentPlan:
    environment: str = "production"
    components: list[str] = field(
        default_factory=lambda: [
            "FastAPI",
            "PostgreSQL",
            "Queue",
            "Workers",
            "Monitoring",
            "Secrets",
            "CI/CD",
        ]
    )


@dataclass
class ObservabilitySnapshot:
    service: str
    latency_ms: int
    error_rate: float
    queue_depth: int
    active_workers: int
