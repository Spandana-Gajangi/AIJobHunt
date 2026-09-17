from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ReviewRequest:
    review_id: str
    review_type: str
    company: str
    role: str
    reason: str
    status: str = "PENDING"
    expires_at: str | None = None
    created_at: str = ""


@dataclass
class ReviewDecision:
    review_id: str
    decision: str
    source: str = "WHATSAPP"
    validated: bool = False
    reason: str = ""
