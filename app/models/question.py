from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class QuestionAnswer:
    question: str
    question_type: str
    answer: str | None
    confidence: float
    requires_user_review: bool = False
    notes: str = ""
    metadata: dict[str, str] = field(default_factory=dict)
