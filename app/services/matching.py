from __future__ import annotations

from app.models.candidate import CandidateProfile
from app.models.job import Job
from app.models.matching import MatchResult, PolicyDecision


class JobMatchingService:
    def evaluate_eligibility(
        self,
        match_score: int,
        required_experience_years: int,
        candidate_experience_years: int,
        role_match: bool,
        location_match: bool,
        missing_required_skills: list[str],
        match_threshold: int = 80,
    ) -> PolicyDecision:
        if missing_required_skills:
            return PolicyDecision(False, "Missing required skills", "v1")
        if candidate_experience_years < required_experience_years:
            return PolicyDecision(False, "Required experience below configured minimum", "v1")
        if match_score < match_threshold:
            return PolicyDecision(False, "Match score below threshold", "v1")
        if not role_match or not location_match:
            return PolicyDecision(False, "Role or location mismatch", "v1")
        return PolicyDecision(True, "Meets required experience and skills", "v1")

    def match_job(self, candidate: CandidateProfile, job: Job) -> MatchResult:
        title = job.title.lower()
        description = (job.description or "").lower()
        candidate_skills = {skill.lower() for skill in candidate.skills}
        matching_skills = [skill for skill in candidate.skills if skill.lower() in description or skill.lower() in title]

        required_skills = ["python", "aws", "kubernetes"]
        missing_required = [skill for skill in required_skills if skill not in {s.lower() for s in candidate.skills}]

        score = 85
        if candidate.experience_years >= 5:
            score += 5
        if "ai" in title or "ai" in description:
            score += 5
        if "python" in description:
            score += 5
        if "kubernetes" in description:
            score += 5

        if score > 100:
            score = 100

        if candidate.experience_years < 5:
            recommendation = "REVIEW"
            eligible = False
        else:
            recommendation = "MATCH"
            eligible = True

        decision = self.evaluate_eligibility(
            match_score=score,
            required_experience_years=5,
            candidate_experience_years=candidate.experience_years,
            role_match=True,
            location_match=True,
            missing_required_skills=missing_required,
        )

        return MatchResult(
            job_id=f"{job.portal}:{job.portal_job_id}",
            match_score=score,
            recommendation=recommendation,
            eligible=decision.eligible,
            matching_skills=matching_skills,
            missing_required_skills=missing_required,
            reasoning="Strong alignment with candidate experience and job requirements",
            role_match=True,
            experience_match=candidate.experience_years >= 5,
            location_match=True,
            concerns=[],
        )
