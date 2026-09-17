from app.models.candidate import CandidateProfile
from app.models.job import Job
from app.models.matching import MatchResult, PolicyDecision
from app.services.matching import JobMatchingService


def test_candidate_profile_and_matching_result_models():
    candidate = CandidateProfile(
        experience_years=9,
        skills=["Python", "AWS", "Kubernetes", "RAG"],
        preferred_roles=["AI Engineer", "AI Architect"],
        preferred_locations=["Hyderabad", "Remote"],
    )

    result = MatchResult(
        job_id="job_123",
        match_score=91,
        recommendation="MATCH",
        eligible=True,
        matching_skills=["Python", "AWS"],
        missing_required_skills=[],
        reasoning="Strong alignment",
    )

    assert candidate.experience_years == 9
    assert candidate.skills[0] == "Python"
    assert result.match_score == 91
    assert result.eligible is True


def test_policy_engine_decides_eligibility():
    service = JobMatchingService()

    decision = service.evaluate_eligibility(
        match_score=88,
        required_experience_years=5,
        candidate_experience_years=9,
        role_match=True,
        location_match=True,
        missing_required_skills=[],
    )

    assert decision.eligible is True
    assert decision.reason == "Meets required experience and skills"


def test_matching_service_scores_and_decides_for_job():
    candidate = CandidateProfile(
        experience_years=9,
        skills=["Python", "AWS", "Kubernetes", "RAG", "Docker"],
        preferred_roles=["AI Engineer"],
        preferred_locations=["Hyderabad", "Remote"],
    )

    job = Job(
        portal="naukri",
        portal_job_id="123",
        title="AI Engineer",
        company="ABC Technologies",
        location="Hyderabad",
        description="We are looking for an AI Engineer with 5+ years in Python, AWS, Kubernetes, and AI/LLM systems.",
        posted_at="2026-09-17T07:20:00+05:30",
        url="https://example.com/job/123",
    )

    result = JobMatchingService().match_job(candidate, job)

    assert result.job_id == "naukri:123"
    assert result.match_score >= 80
    assert result.recommendation in {"MATCH", "REVIEW"}
    assert result.eligible is True
