from __future__ import annotations


class QuestionEngine:
    def answer_question(self, question: str, candidate_profile: dict[str, object]) -> dict[str, object]:
        question_lower = question.lower()
        known_keywords = ["python", "aws", "kubernetes", "docker", "rag", "llm"]
        if any(keyword in question_lower for keyword in known_keywords):
            return {
                "question": question,
                "question_type": "SKILL",
                "answer": "I have experience with the relevant technologies in my candidate profile.",
                "confidence": 0.91,
                "requires_user_review": False,
            }
        return {
            "question": question,
            "question_type": "UNKNOWN",
            "answer": None,
            "confidence": 0.21,
            "requires_user_review": True,
        }
