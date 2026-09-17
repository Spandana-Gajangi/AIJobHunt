from app.models.deployment import DeploymentPlan, ObservabilitySnapshot
from app.services.production import CloudDeploymentService


def test_cloud_deployment_plan_includes_core_components() -> None:
    service = CloudDeploymentService()
    plan = service.build_plan("jobhunt")

    assert isinstance(plan, DeploymentPlan)
    assert "FastAPI" in plan.components
    assert "PostgreSQL" in plan.components
    assert "Queue" in plan.components
    assert plan.environment == "production"


def test_observability_snapshot_tracks_metrics() -> None:
    snapshot = ObservabilitySnapshot(
        service="api",
        latency_ms=120,
        error_rate=0.03,
        queue_depth=7,
        active_workers=2,
    )

    assert snapshot.service == "api"
    assert snapshot.latency_ms > 0
    assert snapshot.error_rate >= 0
    assert snapshot.queue_depth >= 0
