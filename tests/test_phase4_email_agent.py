from app.models.email import EmailMessage, EmailIntent
from app.services.email_service import EmailService


def test_email_normalization_and_classification():
    service = EmailService()
    message = EmailMessage(
        email_id="gmail_123",
        provider="gmail",
        sender="recruiter@acme.com",
        sender_name="John Smith",
        recipient="candidate@example.com",
        subject="Interview Invitation - Senior AI Engineer",
        body_text="We would like to invite you for a technical interview on Monday at 2 PM. Please confirm your availability.",
        thread_id="thread_123",
    )

    result = service.process_email(message)

    assert result["category"] == "INTERVIEW_INVITATION"
    assert result["intent"] == "INTERVIEW_CONFIRMATION_REQUIRED"
    assert result["requires_human_review"] is True


def test_email_association_matches_application_record():
    service = EmailService()
    message = EmailMessage(
        email_id="gmail_456",
        provider="gmail",
        sender="recruiter@acme.com",
        sender_name="John Smith",
        recipient="candidate@example.com",
        subject="Follow up on AI Engineer role",
        body_text="Hi, thanks for your application to the AI Engineer role at ABC Technologies.",
        thread_id="thread_456",
    )

    association = service.associate_email(message)

    assert association["association_status"] == "MATCHED"
    assert association["company"] == "ABC Technologies"
    assert association["role"] == "AI Engineer"


def test_salary_email_requires_human_review():
    service = EmailService()
    message = EmailMessage(
        email_id="gmail_789",
        provider="gmail",
        sender="recruiter@acme.com",
        sender_name="John Smith",
        recipient="candidate@example.com",
        subject="Salary expectation",
        body_text="What are your salary expectations for this role?",
        thread_id="thread_789",
    )

    result = service.process_email(message)

    assert result["category"] == "REQUEST_FOR_INFORMATION"
    assert result["action"] == "USER_REVIEW_REQUIRED"
    assert result["requires_human_review"] is True
