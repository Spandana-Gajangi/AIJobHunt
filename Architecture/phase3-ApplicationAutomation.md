# Phase 3 — Application Agent

## Objective

Build the application execution layer that takes jobs marked as eligible by Phase 2 and executes the job application workflow.

Phase 3 transforms:

> **Eligible Job → Application → Application Status**

The Application Agent will interact with supported job portals, fill application forms using the candidate profile, handle application questions, upload the appropriate resume, and track the result.

The initial implementation will run in **dry-run mode** to allow verification before enabling automatic submission.

---

# 1. Scope

Phase 3 will:

- Read eligible jobs from Phase 2.
- Load candidate information from the candidate profile.
- Select the appropriate resume.
- Open the job/application URL.
- Identify the application workflow.
- Detect form fields.
- Map candidate profile data to application fields.
- Fill known fields.
- Handle common application questions.
- Use the LLM for questions that require semantic understanding.
- Upload the candidate's resume where appropriate.
- Validate fields before submission.
- Support dry-run mode.
- Support automatic submission after validation.
- Track application status.
- Prevent duplicate applications.
- Record application timestamps.
- Record failures and retry information.
- Maintain an audit trail.

---

# 2. Important Design Principle

The Application Agent must NOT have unrestricted control.

The architecture should separate:

```text
AI Reasoning
      ↓
Application Decision
      ↓
Policy Validation
      ↓
Tool Execution
      ↓
Application
```

The LLM can determine:

- What a question means.
- Which candidate information is relevant.
- How to formulate an answer.

The LLM must not independently decide to perform unrestricted external actions.

Critical actions such as submitting an application should pass through deterministic policies.

---

# 3. High-Level Architecture

```text
                         Phase 2
                      Eligible Jobs
                           │
                           ▼
                  ┌──────────────────┐
                  │ Application      │
                  │ Service          │
                  └────────┬─────────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │ Application      │
                  │ Agent            │
                  └────────┬─────────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
   Candidate Profile   Portal Adapter   Resume Manager
          │                │                │
          │                ▼                │
          │          Browser Automation     │
          │                │                │
          └────────────────┼────────────────┘
                           ▼
                    Application Form
                           │
                           ▼
                    Field Extraction
                           │
                           ▼
                    Field Mapper
                           │
                           ▼
                 ┌────────────────────┐
                 │ Application Answer │
                 │ Engine             │
                 └─────────┬──────────┘
                           │
                     LLM if required
                           │
                           ▼
                    Policy Validation
                           │
                    ┌──────┴──────┐
                    ▼             ▼
                  DRY RUN       SUBMIT
                    │             │
                    └──────┬──────┘
                           ▼
                  Application Result
                           │
                           ▼
                  Application Repository
```

---

# 4. Application Workflow

The complete workflow is:

```text
Eligible Job
     ↓
Check Duplicate
     ↓
Create Application Record
     ↓
Open Application URL
     ↓
Detect Application Flow
     ↓
Extract Form Fields
     ↓
Map Fields
     ↓
Fill Known Fields
     ↓
Process Questions
     ↓
Validate Answers
     ↓
Upload Resume
     ↓
Dry Run / Submit
     ↓
Capture Result
     ↓
Update Application Status
```

---

# 5. Application State Machine

Phase 3 extends the application lifecycle.

```text
DISCOVERED
    ↓
MATCHED
    ↓
ELIGIBLE
    ↓
APPLICATION_STARTED
    ↓
FORM_DETECTED
    ↓
FORM_FILLED
    ↓
VALIDATED
    ↓
SUBMITTED
```

Possible alternate states:

```text
SKIPPED
FAILED
BLOCKED
USER_REVIEW_REQUIRED
DUPLICATE
```

Later phases will extend the lifecycle with:

```text
EMAIL_RECEIVED
ACTION_REQUIRED
INTERVIEW
OFFER
REJECTED
```

---

# 6. Application Agent

The Application Agent is responsible for coordinating the application workflow.

Conceptually:

```python
class ApplicationAgent:

    async def apply(self, job, candidate):
        ...
```

The agent should have access only to explicitly defined tools.

Potential tools:

```text
BrowserTool
ResumeTool
FormTool
LLMTool
ApplicationStatusTool
```

The agent should not have arbitrary access to the operating system or unrestricted browser actions.

---

# 7. Portal Adapter Architecture

The application flow is different for every portal.

Use portal-specific adapters:

```text
ApplicationPortal
       │
       ├── LinkedInApplicationAdapter
       ├── NaukriApplicationAdapter
       ├── IndeedApplicationAdapter
       └── FuturePortalAdapter
```

Conceptual interface:

```python
class ApplicationPortal:

    async def open_application(self, job):
        ...

    async def get_form_fields(self):
        ...

    async def fill_field(self, field, value):
        ...

    async def upload_resume(self, path):
        ...

    async def submit(self):
        ...
```

The Application Agent should not contain portal-specific selectors.

---

# 8. Browser Automation

Use:

```text
Playwright
```

for browser interaction where automation is permitted.

Architecture:

```text
Application Agent
       ↓
Portal Adapter
       ↓
Playwright
       ↓
Browser
       ↓
Application Form
```

The system should support:

- Browser launch
- Navigation
- Page detection
- Form discovery
- Input interaction
- File upload
- Validation
- Submission
- Result detection

Portal-specific selectors and workflows must remain inside the corresponding adapter.

---

# 9. Form Field Detection

The application page may contain:

```text
First Name
Last Name
Email
Phone
Location
Experience
Resume
LinkedIn URL
Notice Period
Salary
Skills
Cover Letter
Custom Questions
```

The system should represent fields using a normalized model.

Example:

```json
{
  "field_id": "input_123",
  "label": "Years of experience",
  "type": "number",
  "required": true,
  "value": null
}
```

---

# 10. Field Mapping

Create a mapping layer:

```text
Application Field
       ↓
Field Mapper
       ↓
Candidate Profile
```

Example:

```text
"Years of experience"
        ↓
candidate.experience_years

"Email address"
        ↓
candidate.email

"Phone number"
        ↓
candidate.phone
```

Known fields should be mapped deterministically.

The LLM should not be used for obvious mappings.

---

# 11. Application Question Engine

Some application questions require reasoning.

Example:

```text
"Describe your experience with Kubernetes."
```

The system can provide:

```text
Question
   ↓
Question Classifier
   ↓
Known Profile Data?
   │
   ├── YES → Generate answer
   │
   └── NO → User Review
```

The LLM can generate an answer based only on information present in the candidate profile/resume.

The system must not invent:

- Employment history
- Certifications
- Skills
- Projects
- Job titles
- Achievements
- Years of experience

---

# 12. Structured Question Processing

The LLM should return structured output.

Example:

```json
{
  "question": "Describe your experience with Kubernetes.",
  "question_type": "EXPERIENCE",
  "answer": "I have worked with Kubernetes...",
  "confidence": 0.91,
  "requires_user_review": false
}
```

For an unknown question:

```json
{
  "question": "Do you have experience with XYZ technology?",
  "question_type": "SKILL",
  "answer": null,
  "confidence": 0.21,
  "requires_user_review": true
}
```

Unknown information should result in review rather than hallucination.

---

# 13. Sensitive Questions

Certain questions should trigger human review.

Examples:

```text
Salary expectations
Relocation commitment
Work authorization
Legal declarations
Demographic information
Contractual declarations
Confidential information
```

Workflow:

```text
Question
   ↓
Question Classifier
   ↓
Sensitive?
   │
   └── YES
        ↓
USER_REVIEW_REQUIRED
```

The system should not automatically fabricate or make sensitive commitments on behalf of the candidate.

---

# 14. Resume Management

Create a Resume Manager.

```text
Resume Manager
      │
      ├── Validate resume exists
      ├── Select resume
      ├── Validate file type
      └── Provide path to portal adapter
```

Initial configuration:

```json
{
  "resume_path": "data/resume.pdf"
}
```

Future versions may support:

```text
General Resume
Backend Resume
AI Resume
Architect Resume
```

and select one based on job type.

---

# 15. Dry Run Mode

Dry-run mode is mandatory for the initial implementation.

Configuration:

```text
AUTO_APPLY=false
```

Workflow:

```text
Eligible Job
     ↓
Application Agent
     ↓
Fill Form
     ↓
Generate Answers
     ↓
Validate
     ↓
STOP
     ↓
Generate Preview
```

Example:

```text
========================================
APPLICATION PREVIEW
========================================

Company: ABC Technologies
Role: AI Engineer

Fields:
----------------------------------------
Name              → Candidate
Email             → candidate@example.com
Experience        → 9
Location          → Hyderabad

Questions:
----------------------------------------
Q: Describe your AWS experience.

A:
Candidate has experience working with AWS...

Resume:
resume.pdf

Status:
READY_FOR_SUBMISSION

AUTO_APPLY=false
========================================
```

This allows the complete workflow to be tested without submitting applications.

---

# 16. Automatic Submission

After the workflow has been validated:

```text
AUTO_APPLY=true
```

The submission workflow becomes:

```text
Form Filled
    ↓
Validation
    ↓
Policy Engine
    ↓
Submission Allowed?
    │
    ├── NO → USER_REVIEW_REQUIRED
    │
    └── YES
          ↓
       Submit
```

The policy engine should verify:

- Correct job
- Correct candidate profile
- Required fields completed
- Required documents present
- No unresolved questions
- No sensitive unanswered questions
- Application hasn't already been submitted

---

# 17. Duplicate Protection

Before starting an application:

```text
Check:
portal + portal_job_id
```

and existing application records.

Example:

```text
naukri:123456
```

If already submitted:

```text
Status = DUPLICATE
```

and stop.

This protects against repeated applications when the cron job runs again.

---

# 18. Idempotency

The application process must be idempotent.

Example:

```text
Cron Run 1
    ↓
Application submitted

Cron Run 2
    ↓
Same job detected
    ↓
Existing application found
    ↓
Do NOT submit again
```

Use:

```text
application_id
job_id
portal_job_id
```

to maintain identity.

---

# 19. Application Record

Example:

```json
{
  "application_id": "app_7f82a1",
  "job_id": "job_a82f91",
  "portal": "naukri",
  "portal_job_id": "123456",
  "company": "ABC Technologies",
  "role": "AI Engineer",
  "url": "https://example.com/job/123456",

  "match_score": 91,

  "status": "SUBMITTED",

  "resume": "data/resume.pdf",

  "applied_at": "2026-09-18T10:30:00+05:30",

  "automation_mode": "AUTO",

  "agent_version": "v1",
  "created_at": "2026-09-18T10:20:00+05:30",
  "updated_at": "2026-09-18T10:30:00+05:30"
}
```

---

# 20. Audit Trail

Every important action should be recorded.

Example:

```json
{
  "application_id": "app_7f82a1",
  "events": [
    {
      "event": "APPLICATION_STARTED",
      "timestamp": "2026-09-18T10:20:00+05:30"
    },
    {
      "event": "FORM_DETECTED",
      "timestamp": "2026-09-18T10:21:00+05:30"
    },
    {
      "event": "FORM_FILLED",
      "timestamp": "2026-09-18T10:23:00+05:30"
    },
    {
      "event": "SUBMITTED",
      "timestamp": "2026-09-18T10:30:00+05:30"
    }
  ]
}
```

This becomes useful for debugging and interview demonstrations.

---

# 21. Error Handling

Application failures should be classified.

Example:

```text
BROWSER_TIMEOUT
LOGIN_REQUIRED
FORM_NOT_FOUND
FIELD_NOT_FOUND
RESUME_UPLOAD_FAILED
LLM_ERROR
VALIDATION_FAILED
SUBMISSION_FAILED
UNKNOWN_ERROR
```

Example:

```text
Application
    ↓
Error
    ↓
Classify
    ↓
Retryable?
   /     \
 YES      NO
  ↓        ↓
Retry    USER_REVIEW_REQUIRED
```

Do not blindly retry submission actions because they can create duplicate applications.

---

# 22. Retry Strategy

Safe retry examples:

```text
Page navigation timeout
Temporary network failure
LLM timeout
Temporary provider failure
```

Potentially unsafe retries:

```text
After clicking Submit
After successful application response
After an unknown submission state
```

If the submission result is unknown:

```text
UNKNOWN_SUBMISSION_STATE
```

The application should be marked for review instead of submitting again.

---

# 23. LLM Architecture

The Application Agent should use the existing abstraction:

```text
Application Agent
       ↓
LLMProvider
       ↓
Gemini
```

LLM responsibilities:

```text
✓ Understand application questions
✓ Generate answers
✓ Classify questions
✓ Determine whether profile information is sufficient
```

LLM should NOT directly:

```text
✗ Click Submit
✗ Navigate arbitrarily
✗ Change application status
✗ Access secrets
✗ Make financial/legal commitments
```

Those actions belong to deterministic application services and policies.

---

# 24. Application Policy Engine

Before submission:

```text
Application Data
       ↓
Policy Engine
       ↓
Validation
```

Example policies:

```text
Candidate information complete?
Resume available?
Required fields filled?
All generated answers validated?
No sensitive unanswered question?
Duplicate application?
AUTO_APPLY enabled?
```

Result:

```json
{
  "allowed": true,
  "reason": "All application policies satisfied",
  "policy_version": "v1"
}
```

Or:

```json
{
  "allowed": false,
  "reason": "Salary expectation requires user review",
  "policy_version": "v1"
}
```

---

# 25. Application Result

The portal adapter should return a structured result.

Example:

```json
{
  "success": true,
  "status": "SUBMITTED",
  "confirmation_id": "ABC123",
  "submitted_at": "2026-09-18T10:30:00+05:30"
}
```

If the portal doesn't provide confirmation:

```json
{
  "success": false,
  "status": "UNKNOWN_SUBMISSION_STATE",
  "confirmation_id": null
}
```

Never assume that reaching the final page means an application was successfully submitted.

---

# 26. CLI

Phase 3 should support manual execution.

Example:

```bash
python -m app.applications.run
```

Apply to a specific job:

```bash
python -m app.applications.run --job-id job_a82f91
```

Dry run:

```bash
python -m app.applications.run --dry-run
```

Force preview:

```bash
python -m app.applications.run --preview
```

---

# 27. Application Flow Example

```text
Phase 2
   │
   ▼
AI Engineer
ABC Technologies
Match Score: 91
Eligible: YES
   │
   ▼
Application Agent
   │
   ▼
Check duplicate
   │
   ▼
Open application
   │
   ▼
Detect form
   │
   ▼
Map candidate fields
   │
   ▼
Generate answers
   │
   ▼
Validate
   │
   ▼
Dry Run?
   │
 ┌─┴──────────┐
 │            │
YES          NO
 │            │
 ▼            ▼
Preview      Policy
               │
               ▼
            Submit
               │
               ▼
        Save application
```

---

# 28. Directory Structure

Phase 3 extends the previous phases:

```text
app/
│
├── applications/
│   ├── __init__.py
│   ├── service.py
│   ├── agent.py
│   ├── runner.py
│   ├── policy.py
│   ├── field_mapper.py
│   ├── question_engine.py
│   ├── resume_manager.py
│   │
│   └── portals/
│       ├── __init__.py
│       ├── base.py
│       ├── linkedin.py
│       ├── naukri.py
│       └── ...
│
├── browser/
│   ├── __init__.py
│   ├── browser_manager.py
│   └── page_utils.py
│
├── agents/
│   ├── base.py
│   ├── job_matching_agent.py
│   └── application_agent.py
│
├── llm/
│   ├── base.py
│   └── gemini.py
│
├── models/
│   ├── application.py
│   ├── application_question.py
│   └── ...
│
├── repositories/
│   └── ...
│
└── services/
    └── application_service.py

data/
├── profile.json
├── jobs.json
├── matches.json
├── applications.json
├── run_state.json
└── portal_registry.json

tests/
└── applications/
    ├── test_application_service.py
    ├── test_field_mapper.py
    ├── test_question_engine.py
    ├── test_policy.py
    └── test_duplicate_protection.py
```

---

# 29. Testing Strategy

## Field Mapping

Test:

```text
"Email" → candidate.email
"Phone" → candidate.phone
"Experience" → candidate.experience_years
```

---

## Question Engine

Test:

```text
Known question → generated answer
Unknown question → user review
Sensitive question → user review
```

---

## Duplicate Protection

Test:

```text
Existing application
        ↓
No second submission
```

---

## Policy Engine

Test:

```text
All conditions satisfied
        ↓
ALLOW
```

and:

```text
Sensitive question
        ↓
BLOCK
```

---

## Application State

Test every valid state transition.

Example:

```text
ELIGIBLE
   ↓
APPLICATION_STARTED
   ↓
FORM_FILLED
   ↓
VALIDATED
   ↓
SUBMITTED
```

Invalid transitions should be rejected.

---

# 30. Security

The Application Agent must not expose:

- API keys
- Passwords
- Authentication tokens
- Session cookies
- Private candidate data

Credentials must remain in environment variables or secure local storage.

Do not commit:

```text
.env
browser profiles
session data
cookies
personal resume
personal profile
```

to GitHub.

---

# 31. Responsible Automation

Application automation must use supported/permitted access methods.

The project must not implement mechanisms intended to:

- Bypass CAPTCHA
- Circumvent authentication
- Evade anti-bot controls
- Circumvent rate limits
- Access restricted/private data

If a portal requires manual interaction, the application should transition to:

```text
USER_REVIEW_REQUIRED
```

rather than attempting to bypass the restriction.

---

# 32. Phase 3 Completion Criteria

Phase 3 is complete when the system can:

1. Read eligible jobs from Phase 2.
2. Check whether an application already exists.
3. Start a portal-specific application workflow.
4. Detect and normalize application fields.
5. Map known fields from the candidate profile.
6. Handle application questions.
7. Use the LLM for questions requiring semantic understanding.
8. Prevent hallucinated candidate information.
9. Upload the configured resume.
10. Validate the application.
11. Run successfully in dry-run mode.
12. Produce an application preview.
13. Submit applications when explicitly enabled and permitted.
14. Record the application result.
15. Handle failures safely.
16. Maintain an audit trail.

---

# 33. Example Final Run

```text
========================================
APPLICATION AGENT
========================================

Eligible jobs: 17
Already applied: 5
New applications: 12

Processing:

1. ABC Technologies
   Role: AI Engineer
   Match: 91
   Status: SUBMITTED

2. XYZ Corp
   Role: Technical Lead
   Match: 88
   Status: SUBMITTED

3. Company A
   Role: AI Architect
   Match: 93
   Status: USER_REVIEW_REQUIRED

   Reason:
   Application asks for salary expectation.

----------------------------------------
SUMMARY
----------------------------------------

Eligible:              17
Already applied:        5
Submitted:              11
User review required:   1
Failed:                 0

========================================
```

---

# 34. Phase 3 → Phase 4 Contract

Phase 3 produces application records that Phase 4 will monitor.

```text
                Phase 3
                   │
                   ▼
          Application Record
                   │
        ┌──────────┴──────────┐
        ▼                     ▼
     Job ID               Application ID
        │                     │
        └──────────┬──────────┘
                   ▼
                Phase 4
              Email Agent
```

Phase 4 will use these identifiers to associate recruiter emails with the correct application.

---

# 35. Explicitly Out of Scope

The following belong to Phase 4 or later:

- Recruiter email webhooks
- Email classification
- Email thread analysis
- Automatic email replies
- Interview scheduling
- WhatsApp notifications
- RAG
- Long-term candidate memory
- PostgreSQL
- Redis
- Cloud deployment
- Advanced multi-agent orchestration

---

# 36. Architectural Principle

Phase 3 establishes the boundary between **AI-assisted application reasoning** and **controlled external actions**.

```text
                 LLM
                  │
        Understand / Generate
                  │
                  ▼
          Structured Result
                  │
                  ▼
          Application Policy
                  │
          ┌───────┴────────┐
          ▼                ▼
       ALLOWED         REVIEW/BLOCK
          │                │
          ▼                ▼
       Browser          Human
       Action           Review
          │
          ▼
      Application
          │
          ▼
     Audit Record
```

The Application Agent should therefore be **bounded and tool-driven**, rather than a free-running autonomous agent.

Its responsibility is:

> **Take an eligible job, execute the permitted application workflow, and produce a reliable application record.**