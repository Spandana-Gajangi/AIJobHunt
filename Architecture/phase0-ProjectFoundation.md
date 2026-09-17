# Phase 0 — Project Foundation

### Objective

Create the foundational Python application for the Job Hunt Agent without implementing actual job scraping, application automation, email processing, or WhatsApp integration.

At the end of Phase 0, the project should:

- Start locally.
- Expose a FastAPI health endpoint.
- Load configuration safely from environment variables.
- Load candidate/job preferences from a profile file.
- Have Pydantic domain models.
- Have file-based repositories.
- Have a clean service/agent architecture.
- Have logging and error handling.
- Have unit tests.
- Have a placeholder LLM abstraction.
- Be ready for Phase 1 without restructuring the project.

---

# 1. Phase 0 Architecture

```text
                         ┌──────────────────────┐
                         │      FastAPI API     │
                         │      main.py         │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   Application Layer  │
                         │      Services        │
                         └──────────┬───────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              ▼                     ▼                     ▼
       ┌─────────────┐       ┌─────────────┐       ┌─────────────┐
       │ Job Service │       │ Application │       │ Email       │
       │             │       │ Service     │       │ Service     │
       └──────┬──────┘       └──────┬──────┘       └──────┬──────┘
              │                     │                     │
              └─────────────────────┼─────────────────────┘
                                    ▼
                         ┌──────────────────────┐
                         │      Domain Models   │
                         │ Job / Application /  │
                         │ Candidate / Email    │
                         └──────────┬───────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
             ┌──────────────┐                ┌──────────────┐
             │ Repositories │                │ LLM Provider │
             │ JSON Storage │                │  Abstraction │
             └──────────────┘                └──────────────┘
```

The important architectural principle is:

> **Business logic should not know whether data is stored in JSON, PostgreSQL, or whether Gemini/OpenAI/etc. is being used.**

---

# 2. Directory Structure

I'd use:

```text
jobHunt/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── health.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── logging.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── candidate.py
│   │   ├── job.py
│   │   ├── application.py
│   │   └── email.py
│   │
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── json_repository.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── candidate_service.py
│   │   ├── job_service.py
│   │   └── application_service.py
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   └── base.py
│   │
│   └── llm/
│       ├── __init__.py
│       ├── base.py
│       └── gemini.py
│
├── data/
│   ├── profile.json
│   ├── jobs.json
│   ├── applications.json
│   └── emails.json
│
├── tests/
│   ├── test_health.py
│   ├── test_models.py
│   ├── test_repository.py
│   └── test_config.py
│
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
└── run.py
```

Don't worry about every folder having functionality in Phase 0. Some are **extension points** for later phases.

---

# 3. Configuration

Use environment variables for secrets and runtime configuration.

### `.env`

```text
APP_ENV=development
LOG_LEVEL=INFO

GEMINI_API_KEY=your_key_here

AUTO_APPLY=false
MATCH_THRESHOLD=80
```

### `.env.example`

```text
APP_ENV=development
LOG_LEVEL=INFO

GEMINI_API_KEY=

AUTO_APPLY=false
MATCH_THRESHOLD=80
```

`.env` goes into `.gitignore`.

Never put:

```text
API keys
passwords
OAuth tokens
email credentials
WhatsApp credentials
```

into Git.

---

# 4. Candidate Profile

`data/profile.json`

```json
{
  "name": "Candidate",
  "email": "candidate@example.com",
  "phone": "",
  "location": "Hyderabad",
  "experience_years": 9,

  "skills": [
    "Python",
    "Node.js",
    "AWS",
    "Kubernetes"
  ],

  "preferred_roles": [
    "AI Engineer",
    "AI Architect",
    "Technical Lead"
  ],

  "preferred_locations": [
    "Hyderabad",
    "Remote"
  ],

  "resume_path": "data/resume.pdf"
}
```

For the actual repository, use a **dummy/example profile** rather than committing personal information.

---

# 5. Domain Models

These are extremely important.

### Candidate

```text
Candidate
 ├── identity
 ├── experience
 ├── skills
 ├── preferred_roles
 ├── preferred_locations
 └── resume
```

### Job

```text
Job
 ├── internal_job_id
 ├── portal
 ├── portal_job_id
 ├── title
 ├── company
 ├── location
 ├── description
 ├── skills
 ├── posted_at
 ├── url
 └── discovered_at
```

### Application

```text
Application
 ├── application_id
 ├── job_id
 ├── status
 ├── match_score
 ├── applied_at
 ├── source
 └── timestamps
```

### Email

```text
Email
 ├── email_id
 ├── thread_id
 ├── sender
 ├── subject
 ├── received_at
 ├── company
 ├── job_id
 ├── intent
 └── action_required
```

Use **Pydantic** models so invalid data is caught early.

---

# 6. Status State Machine

Define application states centrally.

```text
DISCOVERED
     │
     ▼
MATCHED
     │
     ▼
ELIGIBLE
     │
     ▼
APPLICATION_STARTED
     │
     ▼
APPLIED
     │
     ▼
EMAIL_RECEIVED
     │
     ▼
ACTION_REQUIRED
     │
     ▼
USER_NOTIFIED
     │
     ├──────► REPLIED
     │
     └──────► INTERVIEW
                    │
                    ▼
                  OFFER
```

Terminal/alternate states:

```text
SKIPPED
REJECTED
WITHDRAWN
FAILED
```

Phase 0 should define these statuses, but **not implement the transitions yet**.

---

# 7. Repository Layer

Initially:

```text
Service
   ↓
Repository Interface
   ↓
JSON Repository
   ↓
jobs.json
```

For example:

```python
class JobRepository:
    def save(self, job):
        ...

    def get(self, job_id):
        ...

    def get_all(self):
        ...

    def exists(self, job_id):
        ...
```

Then:

```text
                Repository Interface
                       │
              ┌────────┴────────┐
              ▼                 ▼
        JSONRepository    PostgreSQLRepository
         Phase 0/1          Future
```

This means moving to PostgreSQL later won't require rewriting your business logic.

---

# 8. LLM Abstraction

Even though we're not doing AI matching yet, **build the abstraction now**.

```text
Application
     │
     ▼
LLMProvider
     │
     ├── GeminiProvider
     │
     ├── OpenAIProvider       future
     │
     └── LocalLLMProvider     future
```

Something conceptually like:

```python
class LLMProvider:

    async def generate(
        self,
        prompt: str,
        response_schema=None
    ):
        ...
```

Later:

```text
Job
 ↓
JobMatchingAgent
 ↓
LLMProvider
 ↓
Gemini
 ↓
Structured MatchResult
```

This prevents your entire application from becoming tightly coupled to Gemini.

---

# 9. Agent Abstraction

Don't build actual agents yet.

Just define the concept.

```text
BaseAgent
   │
   ├── JobAnalysisAgent      Phase 2
   ├── ApplicationAgent      Phase 3
   └── EmailAgent            Phase 4
```

An agent should eventually have:

```text
Input
  ↓
Reasoning
  ↓
Tool selection
  ↓
Tool execution
  ↓
Structured result
```

But Phase 0 only establishes the interface.

---

# 10. API

FastAPI should initially expose only basic endpoints.

### Health

```http
GET /health
```

Response:

```json
{
  "status": "healthy",
  "environment": "development"
}
```

Later we'll add:

```text
POST /webhooks/email
GET  /jobs
GET  /applications
GET  /applications/{id}
```

But **don't implement them yet**.

---

# 11. Logging

Use Python's standard logging framework initially.

Every major operation should eventually have:

```text
timestamp
level
component
event
job_id
application_id
```

Example:

```text
INFO JobCollector - Job discovered - job_id=job_123
INFO JobMatcher - Match completed - score=91
INFO ApplicationAgent - Application started
ERROR EmailAgent - Failed to process email
```

Never log:

```text
API keys
passwords
OAuth tokens
full email contents
sensitive candidate data
```

---

# 12. Error Handling

Phase 0 should establish the pattern:

```text
Exception
    ↓
Application layer
    ↓
Log error
    ↓
Return controlled response
```

Later we'll add:

```text
Retry
Backoff
Dead-letter handling
Idempotency
```

Don't over-engineer these in Phase 0.

---

# 13. Testing

At minimum:

```text
tests/
├── test_health.py
├── test_models.py
├── test_repository.py
└── test_config.py
```

Test things such as:

### Model validation

```text
Invalid job → rejected
Missing title → rejected
Invalid date → rejected
```

### Repository

```text
save()
get()
get_all()
exists()
```

### Configuration

```text
Missing required configuration → appropriate error
```

### API

```text
GET /health → 200
```

---

# 14. What Phase 0 does NOT contain

This is important for keeping the scope controlled.

**Don't implement yet:**

```text
❌ Job portal scraping
❌ Portal discovery
❌ LinkedIn automation
❌ Naukri automation
❌ Application submission
❌ Resume tailoring
❌ LLM job matching
❌ Email webhook
❌ Email replies
❌ WhatsApp
❌ RAG
❌ PostgreSQL
❌ Docker
❌ AWS deployment
❌ Multi-agent orchestration
```

Those belong to later phases.

---

# 15. Phase 0 completion criteria

I'd consider Phase 0 complete when this works:

```text
Clone repository
      ↓
Create virtual environment
      ↓
Install dependencies
      ↓
Configure .env
      ↓
Start FastAPI
      ↓
GET /health
      ↓
       200 OK
```

And:

```text
profile.json
     ↓
Pydantic
     ↓
Candidate object
     ↓
Service
     ↓
Repository
     ↓
JSON
```

And:

```text
pytest
   ↓
All Phase 0 tests pass
```

And Git contains clean commits documenting the foundation.

---

## Git milestone

I'd make Phase 0 one clear milestone:

**`v0.1.0 — Project Foundation`**

Suggested commits:

```text
chore: initialize python project
feat: add application configuration
feat: add domain models
feat: add json repository
feat: add service layer
feat: add llm provider abstraction
feat: add agent abstraction
feat: add health endpoint
test: add foundation tests
docs: document phase 0 architecture
```

This gives you a very clean story later when you put the project on GitHub:

> **Phase 0 established the domain model, provider abstractions, persistence boundary, configuration, API foundation, and testing strategy before introducing AI or automation.**