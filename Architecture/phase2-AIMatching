# Phase 2 — AI Job Matching

## Objective

Build the AI-powered job matching layer that evaluates collected job listings against the candidate profile and determines how closely each job matches the candidate's experience, skills, preferences, and career goals.

Phase 2 takes the normalized jobs produced by Phase 1 and adds:

> **Understand → Extract → Match → Score → Explain → Decide**

Phase 2 does **not** submit applications.

---

# 1. Scope

Phase 2 will:

- Load normalized jobs from Phase 1.
- Load the candidate profile.
- Extract relevant requirements from job descriptions.
- Compare job requirements against candidate capabilities.
- Use an LLM for semantic understanding and matching.
- Produce structured LLM output.
- Calculate a configurable match score.
- Apply deterministic eligibility rules.
- Explain why a job matches or does not match.
- Identify matching and missing skills.
- Identify potential concerns such as experience gaps or location mismatch.
- Store matching results.
- Prevent unnecessary repeated LLM processing.
- Support configurable match thresholds.
- Provide a CLI for manual execution.
- Prepare the output required by the future Application Agent.

Phase 2 will **not**:

- Apply to jobs.
- Fill application forms.
- Send emails.
- Send WhatsApp messages.
- Make external changes on behalf of the user.

---

# 2. High-Level Architecture

```text
                       Phase 1
                    Normalized Jobs
                          │
                          ▼
                  ┌───────────────┐
                  │ Job Matching   │
                  │    Service     │
                  └───────┬───────┘
                          │
             ┌────────────┴────────────┐
             │                         │
             ▼                         ▼
      Candidate Profile           Job Details
             │                         │
             └────────────┬────────────┘
                          ▼
                  ┌───────────────┐
                  │ Requirement   │
                  │   Extractor   │
                  └───────┬───────┘
                          │
                          ▼
                  Structured Job
                  Requirements
                          │
                          ▼
                  ┌───────────────┐
                  │ Matching Agent │
                  │                │
                  │ Gemini LLM     │
                  └───────┬───────┘
                          │
                          ▼
                  Structured Result
                          │
                          ▼
                  ┌───────────────┐
                  │ Policy Engine  │
                  └───────┬───────┘
                          │
                 ┌────────┴────────┐
                 ▼                 ▼
              MATCH             NO_MATCH
                 │
                 ▼
          Eligibility Check
                 │
                 ▼
          MATCHED / ELIGIBLE
                 │
                 ▼
             Storage
```

---

# 3. Core Architectural Principle

The LLM should provide **semantic intelligence**, but it should not control the final application decision.

Use:

```text
LLM
 │
 ├── Understand job
 ├── Extract requirements
 ├── Compare skills
 └── Explain match
          │
          ▼
   Structured Result
          │
          ▼
   Deterministic Policy
          │
          ▼
      ELIGIBLE?
```

Do not use:

```text
LLM
  ↓
"Looks good"
  ↓
Automatically apply
```

The Application Agent in Phase 3 will consume the `ELIGIBLE` jobs.

---

# 4. Candidate Profile

The candidate profile created in Phase 0 remains the source of truth.

Example:

```json
{
  "experience_years": 9,
  "skills": [
    "Python",
    "Node.js",
    "AWS",
    "Kubernetes",
    "Docker",
    "Kafka",
    "AI",
    "LLM",
    "RAG"
  ],
  "preferred_roles": [
    "AI Engineer",
    "AI Architect",
    "Technical Lead"
  ],
  "preferred_locations": [
    "Hyderabad",
    "Remote"
  ]
}
```

The profile should eventually contain richer information such as:

- Years of experience
- Technical skills
- Frameworks
- Cloud platforms
- Architecture experience
- Leadership experience
- Industry experience
- Preferred roles
- Preferred locations
- Work mode
- Salary expectations
- Notice period
- Education
- Certifications
- Resume information

The profile should remain configurable without changing application code.

---

# 5. Job Requirement Extraction

A job listing may contain unstructured information.

Example:

```text
We are looking for an AI Engineer with 5+ years of
experience in Python and cloud technologies.

Experience with AWS, Kubernetes, RAG and LLMs is preferred.
```

The LLM converts this into structured requirements:

```json
{
  "required_experience_years": 5,
  "required_skills": [
    "Python",
    "Cloud"
  ],
  "preferred_skills": [
    "AWS",
    "Kubernetes",
    "RAG",
    "LLM"
  ],
  "role": "AI Engineer"
}
```

This creates a stable representation for the matching process.

---

# 6. Requirement Categories

Requirements should be separated into categories.

```text
Required
Preferred
Optional
Unknown
```

Example:

```json
{
  "required": [
    "Python",
    "AWS"
  ],
  "preferred": [
    "Kubernetes",
    "RAG"
  ],
  "optional": [
    "Terraform"
  ]
}
```

This prevents an optional skill from being treated as a hard requirement.

---

# 7. Matching Agent

The Matching Agent receives:

```text
Candidate Profile
        +
Job Requirements
        ↓
Matching Agent
        ↓
Structured Match Result
```

The agent should evaluate:

### Skills

```text
Candidate:
Python
AWS
Kubernetes
RAG

Job:
Python
AWS
Kubernetes
Terraform

Result:

Matching:
Python
AWS
Kubernetes

Missing:
Terraform
```

### Experience

Example:

```text
Candidate: 9 years
Job requirement: 5+ years

Experience match: TRUE
```

If:

```text
Candidate: 4 years
Job requirement: 8+ years
```

the result should identify the experience gap.

### Role relevance

Compare:

```text
Candidate preferred roles
        vs
Job title + description
```

### Location

Evaluate:

```text
Hyderabad
Remote
Bangalore
Mumbai
```

against the candidate's preferences.

### Career alignment

Evaluate whether the role is broadly aligned with the candidate's configured target roles and experience.

---

# 8. Match Result Schema

The LLM must return structured output.

Example:

```json
{
  "job_id": "job_a82f91",

  "match_score": 91,

  "role_match": true,

  "experience_match": true,

  "location_match": true,

  "matching_skills": [
    "Python",
    "AWS",
    "Kubernetes",
    "RAG"
  ],

  "missing_required_skills": [],

  "missing_preferred_skills": [
    "Terraform"
  ],

  "experience_gap": null,

  "concerns": [],

  "reasoning": "The role closely matches the candidate's...",
  
  "recommendation": "MATCH"
}
```

Possible recommendation values:

```text
MATCH
NO_MATCH
REVIEW
```

`REVIEW` should be used when the available job information is insufficient for a reliable decision.

---

# 9. Match Score

The system should produce a score between:

```text
0 → 100
```

The score represents **matching criteria**, not an absolute prediction of hiring success.

Example:

```text
90-100 → Strong match
80-89  → Good match
70-79  → Review
<70    → Low match
```

These ranges should remain configurable.

Example:

```text
MATCH_THRESHOLD=80
```

The system should not assume that a higher score guarantees an interview or offer.

---

# 10. Deterministic Policy Engine

The LLM result is passed to a policy engine.

Example:

```text
Match Result
     │
     ▼
Policy Engine
     │
     ├── Required experience satisfied?
     ├── Required skills satisfied?
     ├── Location acceptable?
     ├── Role acceptable?
     ├── Match score >= threshold?
     │
     ▼
Eligibility Decision
```

Example:

```json
{
  "eligible": true,
  "reason": "Meets required experience and skills",
  "policy_version": "v1"
}
```

Another example:

```json
{
  "eligible": false,
  "reason": "Required experience below configured minimum",
  "policy_version": "v1"
}
```

---

# 11. LLM Provider Architecture

Phase 0 introduced the LLM abstraction.

Phase 2 implements it.

```text
                  LLMProvider
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
      Gemini       OpenAI       Local LLM
     Provider      Provider      Provider
```

Initial implementation:

```text
GeminiProvider
```

Recommended model:

```text
Gemini Flash
```

A lighter model can be used for high-volume extraction/classification tasks where appropriate.

The matching service should depend on:

```text
LLMProvider
```

and not directly on the Gemini SDK.

---

# 12. Structured LLM Output

Avoid parsing free-form text such as:

```text
"I think this job is a good match..."
```

Instead require a defined schema:

```text
LLM
 ↓
Pydantic schema
 ↓
MatchResult
```

Benefits:

- Predictable output
- Validation
- Easier testing
- Easier persistence
- Easier downstream automation
- Safer agent behavior

---

# 13. Prompt Architecture

Prompts should not be embedded throughout the code.

Use a dedicated prompt layer:

```text
app/
└── llm/
    └── prompts/
        ├── job_requirements.txt
        └── job_matching.txt
```

The prompt should clearly define:

- Candidate data
- Job data
- Matching criteria
- Required output schema
- Rules
- Uncertainty handling

The model should be instructed not to invent information that isn't present in the job listing or candidate profile.

---

# 14. Matching Workflow

Complete Phase 2 flow:

```text
New Job
   │
   ▼
Load Candidate Profile
   │
   ▼
Check Existing Match Result
   │
   ├── Already processed → Skip LLM
   │
   └── New/Changed Job
            │
            ▼
    Extract Requirements
            │
            ▼
     Validate Extraction
            │
            ▼
      Match Candidate
            │
            ▼
      MatchResult
            │
            ▼
      Policy Engine
            │
       ┌────┴────┐
       ▼         ▼
    Eligible   Not Eligible
       │         │
       └────┬────┘
            ▼
       Save Result
```

---

# 15. Avoid Repeated LLM Calls

The system should not analyze the same job every time the cron job runs.

Store:

```text
job_id
job_content_hash
matching_result
model
prompt_version
matched_at
```

Example:

```json
{
  "job_id": "job_a82f91",
  "content_hash": "abc123",
  "match_score": 91,
  "model": "gemini",
  "prompt_version": "v1",
  "matched_at": "2026-09-18T10:00:00+05:30"
}
```

If:

```text
job_id + content_hash
```

has already been processed, reuse the previous result.

If the job description changes:

```text
new content_hash
```

the system can perform matching again.

---

# 16. Matching Storage

Create:

```text
data/matches.json
```

Example:

```json
{
  "matches": [
    {
      "job_id": "job_a82f91",
      "match_score": 91,
      "recommendation": "MATCH",
      "eligible": true,
      "matching_skills": [
        "Python",
        "AWS",
        "Kubernetes"
      ],
      "missing_skills": [
        "Terraform"
      ],
      "matched_at": "2026-09-18T10:00:00+05:30"
    }
  ]
}
```

The Application Agent in Phase 3 will consume:

```text
eligible = true
```

jobs.

---

# 17. Explainability

Every match should have a reason.

Example:

```text
Job:
AI Engineer

Match Score:
91

Why:
- 9 years candidate experience vs 5+ required
- Python matches
- AWS matches
- Kubernetes matches
- RAG matches
- Hyderabad matches preferred location

Missing:
- Terraform
```

The explanation should be generated from the structured result rather than relying solely on free-form LLM output.

---

# 18. Uncertainty Handling

The model must be allowed to say:

```text
UNKNOWN
```

when information isn't available.

Example:

```text
Job does not specify experience.
```

Do not assume:

```text
No experience mentioned
        ↓
Candidate qualifies
```

Instead:

```text
Experience requirement:
UNKNOWN
```

Similarly:

```text
Location:
UNKNOWN
```

should not automatically become:

```text
Location:
MATCH
```

---

# 19. Job Matching Agent vs Normal Service

The architecture should distinguish between:

### Job Matching Service

Responsible for orchestration:

```text
load data
call extractor
call matcher
validate result
call policy
persist result
```

### Matching Agent

Responsible for LLM-based reasoning:

```text
understand requirements
compare candidate and job
produce structured match
```

Therefore:

```text
JobMatchingService
        │
        ▼
  MatchingAgent
        │
        ▼
   LLMProvider
        │
        ▼
      Gemini
```

This separation allows the LLM component to evolve without changing the workflow.

---

# 20. CLI

Phase 2 should support manual execution.

Example:

```bash
python -m app.matching.run
```

Optional:

```bash
python -m app.matching.run --job-id job_a82f91
```

Process only new jobs:

```bash
python -m app.matching.run --new
```

Process all jobs:

```bash
python -m app.matching.run --all
```

---

# 21. Example Run

```text
========================================
AI JOB MATCHING
========================================

Jobs received: 135
Already matched: 82
New jobs: 53

Processing...

AI Engineer - ABC Technologies
Match: 91
Eligible: YES

Technical Lead - XYZ Corp
Match: 86
Eligible: YES

Senior Backend Engineer - Company A
Match: 74
Eligible: NO

AI Architect - Company B
Match: 93
Eligible: YES

----------------------------------------
SUMMARY
----------------------------------------

Processed:       53
Strong matches:  17
Review:           8
Not eligible:    28

Eligible jobs:   17

Status: SUCCESS
========================================
```

---

# 22. Error Handling

LLM failures should not stop processing every job.

```text
Job 1 → SUCCESS
Job 2 → SUCCESS
Job 3 → LLM TIMEOUT
Job 4 → SUCCESS
Job 5 → INVALID RESPONSE
```

The system should record failures:

```json
{
  "job_id": "job_xyz",
  "status": "FAILED",
  "error_type": "LLM_TIMEOUT",
  "retry_count": 2
}
```

The job can be retried later.

---

# 23. Cost and Token Control

Even with a free LLM tier, avoid sending unnecessary data.

Do not send the entire candidate profile and entire job description repeatedly if only a subset is needed.

Possible optimization:

```text
Job
 ↓
Deterministic preprocessing
 ↓
Relevant requirements
 ↓
LLM
```

Examples of deterministic filtering:

- Normalize skills
- Detect obvious location
- Detect experience numbers
- Remove duplicated text
- Remove irrelevant HTML

The LLM should handle the parts that require semantic understanding.

---

# 24. Security

Candidate information can be sensitive.

The system must:

- Keep `.env` out of Git.
- Avoid logging personal information.
- Avoid logging complete resumes.
- Avoid logging complete email contents.
- Store credentials only in environment variables.
- Minimize data sent to external LLM providers.
- Use example/dummy profile data in the public repository.

---

# 25. Testing Strategy

## Requirement Extraction

Test:

```text
Job description
      ↓
Expected requirements
```

Cases:

- Required skills
- Preferred skills
- Missing experience
- Missing location
- Ambiguous requirements
- Multiple experience ranges

---

## Matching

Test:

```text
Candidate + Job
      ↓
Expected MatchResult
```

Cases:

- Strong match
- Partial match
- Experience mismatch
- Skill mismatch
- Location mismatch
- Unknown requirements

LLM calls should be mocked during unit tests.

---

## Policy

Test deterministic rules independently:

```text
score = 90
required skills = satisfied
experience = satisfied
location = satisfied
      ↓
eligible = true
```

and:

```text
score = 90
required experience = not satisfied
      ↓
eligible = false
```

---

# 26. Directory Structure

Phase 2 extends Phase 1:

```text
app/
│
├── matching/
│   ├── __init__.py
│   ├── matcher.py
│   ├── extractor.py
│   ├── policy.py
│   ├── run.py
│   └── prompts/
│       ├── requirement_extraction.txt
│       └── job_matching.txt
│
├── agents/
│   ├── base.py
│   └── job_matching_agent.py
│
├── llm/
│   ├── base.py
│   └── gemini.py
│
├── models/
│   ├── job.py
│   ├── candidate.py
│   └── match.py
│
├── repositories/
│   └── ...
│
└── services/
    └── job_matching_service.py

data/
├── profile.json
├── jobs.json
├── matches.json
├── run_state.json
└── portal_registry.json

tests/
└── matching/
    ├── test_extractor.py
    ├── test_matcher.py
    ├── test_policy.py
    └── test_matching_service.py
```

---

# 27. Phase 2 Data Flow

```text
                    Phase 1
                 jobs.json
                     │
                     ▼
              Job Matching Service
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
    Candidate Profile          Job
          │                     │
          └──────────┬──────────┘
                     ▼
             Requirement
               Extraction
                     │
                     ▼
             Matching Agent
                     │
                     ▼
                 Gemini
                     │
                     ▼
              MatchResult
                     │
                     ▼
              Policy Engine
                     │
             ┌───────┴───────┐
             ▼               ▼
          ELIGIBLE         SKIP/REVIEW
             │
             ▼
          matches.json
             │
             ▼
                 Phase 3
          Application Agent
```

---

# 28. Phase 2 Completion Criteria

Phase 2 is complete when the system can:

1. Read new jobs from Phase 1.
2. Load the candidate profile.
3. Extract job requirements.
4. Send relevant information to the LLM.
5. Receive validated structured output.
6. Calculate/store a match result.
7. Apply deterministic eligibility rules.
8. Avoid reprocessing unchanged jobs.
9. Handle LLM failures gracefully.
10. Produce a useful matching report.
11. Persist results in `matches.json`.
12. Identify jobs eligible for Phase 3.

Example:

```text
135 jobs discovered
        ↓
135 jobs normalized
        ↓
135 jobs deduplicated
        ↓
135 jobs evaluated
        ↓
17 eligible
        ↓
17 ready for Application Agent
```

---

# 29. Explicitly Out of Scope

The following belong to later phases:

- Job application submission
- Application form automation
- Resume upload
- Application question answering
- Email webhooks
- Recruiter email classification
- Email replies
- WhatsApp notifications
- RAG
- PostgreSQL
- Redis
- Cloud deployment
- Advanced multi-agent orchestration

---

# 30. Architectural Principle

Phase 2 establishes the boundary between **AI reasoning** and **system control**.

```text
             LLM
              │
      Semantic Understanding
              │
              ▼
      Structured MatchResult
              │
              ▼
       Deterministic Policy
              │
              ▼
       Eligibility Decision
              │
              ▼
          Phase 3
```

The LLM answers:

> **"How well does this job match the candidate?"**

The policy engine answers:

> **"Does this job satisfy the rules required before it can proceed to application?"**

The Application Agent in Phase 3 will answer:

> **"How should the application workflow be executed?"**