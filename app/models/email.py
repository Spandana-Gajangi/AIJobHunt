from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class EmailMessage:
    email_id: str
    provider: str
    sender: str
    sender_name: str | None = None
    recipient: str | None = None
    subject: str = ""
    body_text: str = ""
    thread_id: str | None = None
    received_at: str = ""
    attachments: list[str] = field(default_factory=list)
    labels: list[str] = field(default_factory=list)
    message_url: str | None = None
    is_reply: bool = False


@dataclass
class EmailIntent:
    category: str
    intent: str
    company: str | None = None
    role: str | None = None
    requested_action: str | None = None
    interview_date: str | None = None
    interview_time: str | None = None
    deadline: str | None = None
    requested_information: list[str] = field(default_factory=list)
    confidence: float = 0.0
    requires_human_review: bool = False
    reasoning: str | None = None
