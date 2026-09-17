from app.models.application import ApplicationRecord, ApplicationResult
from app.models.candidate import CandidateProfile
from app.models.job import Job
from app.services.application_service import ApplicationService
from app.services.question_engine import QuestionEngine


def test_application_record_tracks_a_dry_run_application():
    candidate = CandidateProfile(
        experience_years=9,
        skills=["Python", "AWS", "Kubernetes", "RAG"],
        preferred_roles=["AI Engineer"],
        preferred_locations=["Hyderabad", "Remote"],
        email="candidate@example.com",
        phone="+91-99999-99999",
    )

    job = Job(
        portal="naukri",
        portal_job_id="123456",
        title="AI Engineer",
        company="ABC Technologies",
        location="Hyderabad",
        description="We are looking for an AI Engineer with Python, AWS, and Kubernetes experience.",
        posted_at="2026-09-17T07:20:00+05:30",
        url="https://example.com/job/123456",
    )

    service = ApplicationService(dry_run=True)
    result = service.prepare_application(candidate, job)

    assert result.status == "DRY_RUN_READY"
    assert result.job_id == "naukri:123456"
    assert result.automation_mode == "DRY_RUN"
    assert result.application_id.startswith("app_")


def test_application_service_prevents_duplicate_submissions():
    candidate = CandidateProfile(
        experience_years=9,
        skills=["Python", "AWS", "Kubernetes"],
        preferred_roles=["AI Engineer"],
        preferred_locations=["Hyderabad"],
        email="candidate@example.com",
        phone="+91-99999-99999",
    )

    job = Job(
        portal="naukri",
        portal_job_id="duplicate-123",
        title="AI Engineer",
        company="ABC Technologies",
        location="Hyderabad",
        description="Python and AWS required.",
        posted_at="2026-09-17T07:20:00+05:30",
        url="https://example.com/job/duplicate-123",
    )

    service = ApplicationService(dry_run=True)
    first = service.prepare_application(candidate, job)
    second = service.prepare_application(candidate, job)

    assert first.status == "DRY_RUN_READY"
    assert second.status == "DUPLICATE"
    assert second.reason == "Application already exists for this job"


def test_question_engine_flags_unknown_question_for_review():
    engine = QuestionEngine()
    answer = engine.answer_question(
        question="How do you feel about working with a niche x-ray dataset?",
        candidate_profile={"skills": ["Python", "AWS", "Kubernetes"]},
    )

    assert answer["requires_user_review"] is True
    assert answer["answer"] is None
