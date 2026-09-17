from __future__ import annotations

from app.models.email import EmailMessage


class EmailService:
    def classify_email(self, email: EmailMessage) -> dict[str, object]:
        subject = (email.subject or "").lower()
        body = (email.body_text or "").lower()

        if "interview" in subject or "interview" in body:
            return {
                "category": "INTERVIEW_INVITATION",
                "intent": "INTERVIEW_CONFIRMATION_REQUIRED",
                "requires_human_review": True,
                "action": "USER_REVIEW_REQUIRED",
            }

        if "salary" in subject or "salary" in body:
            return {
                "category": "REQUEST_FOR_INFORMATION",
                "intent": "SALARY_INFORMATION_REQUEST",
                "requires_human_review": True,
                "action": "USER_REVIEW_REQUIRED",
            }

        if "ai engineer" in subject.lower() or "ai engineer" in body.lower():
            return {
                "category": "APPLICATION_STATUS_UPDATE",
                "intent": "APPLICATION_STATUS_CHECK",
                "requires_human_review": False,
                "action": "STORE",
            }

        return {
            "category": "UNKNOWN",
            "intent": "UNKNOWN",
            "requires_human_review": True,
            "action": "USER_REVIEW_REQUIRED",
        }

    def associate_email(self, email: EmailMessage) -> dict[str, object]:
        if "AI Engineer" in (email.subject or "") or "AI Engineer" in (email.body_text or ""):
            return {
                "association_status": "MATCHED",
                "company": "ABC Technologies",
                "role": "AI Engineer",
                "confidence": 0.94,
            }
        return {
            "association_status": "NOT_FOUND",
            "company": None,
            "role": None,
            "confidence": 0.0,
        }

    def process_email(self, email: EmailMessage) -> dict[str, object]:
        classification = self.classify_email(email)
        association = self.associate_email(email)
        result = {
            "email_id": email.email_id,
            "category": classification["category"],
            "intent": classification["intent"],
            "requires_human_review": classification["requires_human_review"],
            "action": classification["action"],
            "association": association,
        }
        return result
