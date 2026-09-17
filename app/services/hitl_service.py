from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from app.models.review import ReviewDecision, ReviewRequest


class HITLService:
    def __init__(self) -> None:
        self.reviews: dict[str, ReviewRequest] = {}

    def create_review(
        self,
        review_type: str,
        company: str,
        role: str,
        reason: str,
        expires_hours: int = 24,
    ) -> ReviewRequest:
        review_id = f"review_{uuid.uuid4().hex[:8]}"
        expires_at = (datetime.now(timezone.utc) + timedelta(hours=expires_hours)).isoformat()
        review = ReviewRequest(
            review_id=review_id,
            review_type=review_type,
            company=company,
            role=role,
            reason=reason,
            status="PENDING",
            expires_at=expires_at,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        self.reviews[review_id] = review
        return review

    def process_decision(self, review_id: str, decision: str) -> ReviewDecision:
        review = self.reviews.get(review_id)
        if review is None:
            return ReviewDecision(review_id=review_id, decision=decision, validated=False, reason="Review not found")

        if review.status == "CANCELLED":
            return ReviewDecision(review_id=review_id, decision=decision, validated=False, reason="Review is no longer valid")

        if review.expires_at:
            expires_at = datetime.fromisoformat(review.expires_at)
            if datetime.now(timezone.utc) >= expires_at:
                review.status = "EXPIRED"
                return ReviewDecision(review_id=review_id, decision=decision, validated=False, reason="Review has expired or is no longer valid")

        if decision.upper() not in {"CONFIRM", "REPLY_MANUALLY", "DECLINE", "ASK_FOR_ANOTHER_TIME", "IGNORE"}:
            return ReviewDecision(review_id=review_id, decision=decision, validated=False, reason="Ambiguous response; user clarification required")

        review.status = "COMPLETED"
        return ReviewDecision(review_id=review_id, decision=decision, validated=True, reason="Decision accepted")
