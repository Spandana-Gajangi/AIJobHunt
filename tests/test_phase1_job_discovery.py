from app.models.job import Job, JobSearchCriteria, PortalDefinition, PortalStatus, RawJob
from app.services.discovery import JobDiscoveryService
from app.services.repository import JobRepository


def test_portal_registry_and_search_criteria():
    registry = [
        PortalDefinition(name="linkedin", enabled=True, adapter="LinkedInAdapter"),
        PortalDefinition(name="naukri", enabled=True, adapter="NaukriAdapter"),
        PortalDefinition(name="indeed", enabled=False, adapter="IndeedAdapter"),
    ]

    criteria = JobSearchCriteria(
        keywords=["AI Engineer"],
        locations=["Hyderabad", "Remote"],
        days_back=3,
    )

    assert registry[0].name == "linkedin"
    assert registry[2].status == PortalStatus.DISABLED
    assert criteria.keywords == ["AI Engineer"]
    assert criteria.locations == ["Hyderabad", "Remote"]


def test_repository_saves_and_deduplicates_jobs(tmp_path):
    repo = JobRepository(storage_path=tmp_path / "jobs.json")
    job = Job(
        portal="naukri",
        portal_job_id="123456",
        title="AI Engineer",
        company="ABC Technologies",
        location="Hyderabad",
        description="Build AI systems.",
        posted_at="2026-09-17T07:20:00+05:30",
        url="https://example.com/job/123456",
    )

    repo.save(job)
    assert repo.exists("naukri:123456") is True
    assert len(repo.get_all()) == 1

    duplicate = Job(
        portal="naukri",
        portal_job_id="123456",
        title="AI Engineer",
        company="ABC Technologies",
        location="Hyderabad",
        description="Build AI systems.",
        posted_at="2026-09-17T07:20:00+05:30",
        url="https://example.com/job/123456",
    )

    assert repo.is_duplicate(duplicate) is True


def test_discovery_service_normalizes_and_deduplicates_jobs():
    service = JobDiscoveryService()

    raw_jobs = [
        RawJob(
            source="naukri",
            raw_id="123456",
            raw_title="AI Engineer",
            raw_company="ABC Technologies",
            raw_location="Hyderabad, Telangana",
            raw_description="Build AI systems and pipelines.",
            raw_posted_date="2026-09-17T07:20:00+05:30",
            raw_url="https://example.com/job/123456",
        ),
        RawJob(
            source="linkedin",
            raw_id="abc-123",
            raw_title="AI Engineer",
            raw_company="ABC Technologies",
            raw_location="Hyderabad",
            raw_description="Build AI systems and pipelines.",
            raw_posted_date="2026-09-17T07:20:00+05:30",
            raw_url="https://example.com/job/abc-123",
        ),
    ]

    jobs = service.normalize_jobs(raw_jobs)

    assert len(jobs) == 2
    assert jobs[0].portal == "naukri"
    assert jobs[0].fingerprint == "abc technologies|ai engineer|hyderabad"
    assert service.deduplicate_jobs(jobs)[0].portal == "naukri"
