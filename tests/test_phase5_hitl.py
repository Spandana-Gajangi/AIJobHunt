from app.models.review import ReviewDecision, ReviewRequest
from app.services.hitl_service import HITLService


def test_create_review_request_and_validate_decision():
    service = HITLService()
    review = service.create_review(
        review_type="INTERVIEW_CONFIRMATION",
        company="Example Corp",
        role="AI Architect",
        reason="Recruiter requested interview availability",
    )

    assert review.review_id.startswith("review_")
    assert review.status == "PENDING"

    decision = service.process_decision(review.review_id, "CONFIRM")
    assert isinstance(decision, ReviewDecision)
    assert decision.decision == "CONFIRM"
    assert decision.validated is True


def test_expired_review_is_rejected():
    service = HITLService()
    review = service.create_review(
        review_type="SALARY_REQUEST",
        company="Example Corp",
        role="AI Architect",
        reason="Recruiter asked for salary expectations",
        expires_hours=0,
    )

    decision = service.process_decision(review.review_id, "REPLY_MANUALLY")
    assert decision.validated is False
    assert decision.reason == "Review has expired or is no longer valid"


def test_ambiguous_decision_requires_clarification():
    service = HITLService()
    review = service.create_review(
        review_type="INTERVIEW_CONFIRMATION",
        company="Example Corp",
        role="AI Architect",
        reason="Recruiter requested interview availability",
    )

    decision = service.process_decision(review.review_id, "MAYBE")
    assert decision.validated is False
    assert decision.reason == "Ambiguous response; user clarification required"
