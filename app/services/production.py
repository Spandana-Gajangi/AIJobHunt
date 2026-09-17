from __future__ import annotations

from app.models.deployment import DeploymentPlan


class CloudDeploymentService:
    def build_plan(self, service_name: str) -> DeploymentPlan:
        plan = DeploymentPlan(environment="production")
        plan.components = [
            "FastAPI",
            "PostgreSQL",
            "Queue",
            "Workers",
            "Monitoring",
            "Secrets",
            "CI/CD",
            f"{service_name}-service",
        ]
        return plan
