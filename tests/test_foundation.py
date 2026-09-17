from app.core.config import get_settings
from app.models.job import ApplicationStatus, JobRecord


def test_default_settings_are_loaded():
    settings = get_settings()

    assert settings.app_name == "jobhunt"
    assert settings.storage_path.endswith("data")
    assert settings.dry_run is True


def test_job_record_defaults_are_valid():
    job = JobRecord(
        source="linkedin",
        title="Senior Python Engineer",
        company="Example Corp",
        url="https://example.com/jobs/123",
    )

    assert job.source == "linkedin"
    assert job.status == ApplicationStatus.DISCOVERED
    assert job.match_score == 0
