# Phase 1 — Job Portal Discovery & Job Collection

## Objective

Build the first functional layer of the Job Hunt Agent that can discover and collect job listings from multiple job portals.

Phase 1 is responsible only for:

> **Discover → Collect → Normalize → Deduplicate → Store**

AI-based job matching and automatic job applications will be implemented in later phases.

---

# 1. Scope

Phase 1 will:

- Maintain a registry of supported job portals.
- Discover potential additional job portals.
- Validate discovered portals before enabling them.
- Use portal-specific adapters to collect job listings.
- Support different collection mechanisms per portal.
- Normalize jobs from different portals into a common schema.
- Identify duplicate jobs.
- Track the last successful collection run.
- Support searching jobs posted since the last run.
- Support searching jobs posted within the last `N` days.
- Persist jobs using the repository layer.
- Initially use JSON files for storage.
- Run manually through a CLI.
- Run automatically through Windows Task Scheduler.

Phase 1 will **not** perform job matching or applications.

---

# 2. High-Level Architecture

```text
                         ┌───────────────────┐
                         │  Windows Scheduler│
                         │    / Manual CLI   │
                         └─────────┬─────────┘
                                   │
                                   ▼
                       ┌───────────────────────┐
                       │   Job Hunt Runner     │
                       └───────────┬───────────┘
                                   │
                 ┌─────────────────┴─────────────────┐
                 │                                   │
                 ▼                                   ▼
       ┌──────────────────┐                ┌──────────────────┐
       │ Portal Registry  │                │ Run State        │
       │                  │                │                  │
       │ LinkedIn         │                │ last_run         │
       │ Naukri           │                │ run_id           │
       │ Indeed           │                │ status           │
       │ Foundit          │                └──────────────────┘
       │ ...              │
       └────────┬─────────┘
                │
                ▼
       ┌───────────────────┐
       │   Job Collector   │
       └─────────┬─────────┘
                 │
        ┌────────┼────────┐
        ▼        ▼        ▼
     Portal A Portal B Portal C
     Adapter   Adapter   Adapter
        │        │        │
        └────────┼────────┘
                 ▼
          Raw Job Listings
                 │
                 ▼
       ┌───────────────────┐
       │   Job Normalizer  │
       └─────────┬─────────┘
                 │
                 ▼
          Normalized Jobs
                 │
                 ▼
       ┌───────────────────┐
       │   Deduplicator    │
       └─────────┬─────────┘
                 │
                 ▼
       ┌───────────────────┐
       │   Job Repository  │
       └─────────┬─────────┘
                 │
                 ▼
              jobs.json
```

---

# 3. Core Components

## 3.1 Job Hunt Runner

The runner is the entry point for a complete job collection cycle.

Responsibilities:

1. Generate a run ID.
2. Load the previous successful run.
3. Determine the search window.
4. Load enabled portals.
5. Invoke the Job Collector.
6. Process collected jobs.
7. Persist jobs.
8. Update run state.
9. Produce a run summary.

Example:

```text
Run ID: run_20260918_090000

Search window:
2026-09-17 09:00 → 2026-09-18 09:00

Portals:
LinkedIn
Naukri
Indeed
Foundit

Collected: 158
Duplicates: 23
New jobs: 135

Status: SUCCESS
```

---

# 4. Portal Registry

The portal registry defines which job portals are known and enabled.

Example:

```json
{
  "portals": [
    {
      "name": "linkedin",
      "enabled": true,
      "adapter": "LinkedInAdapter"
    },
    {
      "name": "naukri",
      "enabled": true,
      "adapter": "NaukriAdapter"
    },
    {
      "name": "indeed",
      "enabled": false,
      "adapter": "IndeedAdapter"
    }
  ]
}
```

The registry should allow portals to be enabled or disabled without modifying application code.

---

# 5. Portal Discovery

The system should support discovering additional job portals instead of assuming that only LinkedIn and Naukri are available.

Discovery flow:

```text
Portal Discovery
       │
       ▼
Candidate Portals
       │
       ▼
Portal Validation
       │
       ▼
Capability Detection
       │
       ▼
Human Review
       │
       ▼
Portal Registry
```

A discovered portal should not automatically become an active production source.

Possible portal states:

```text
DISCOVERED
VALIDATED
REVIEW_REQUIRED
ENABLED
DISABLED
```

The discovery process may use search/web data, but actual collection must use a supported and permitted access method.

---

# 6. Portal Adapter Architecture

Different job portals have different:

- APIs
- HTML structures
- Authentication requirements
- Pagination
- Job identifiers
- Date formats
- Search parameters
- Access restrictions

Therefore, each portal should have its own adapter.

```text
JobPortal
   │
   ├── LinkedInAdapter
   ├── NaukriAdapter
   ├── IndeedAdapter
   ├── FounditAdapter
   ├── GlassdoorAdapter
   ├── CutshortAdapter
   ├── InstahyreAdapter
   └── FuturePortalAdapter
```

The core application should not contain portal-specific logic.

Conceptual interface:

```python
class JobPortal:

    @property
    def name(self) -> str:
        ...

    async def search_jobs(
        self,
        criteria: JobSearchCriteria
    ) -> list[RawJob]:
        ...
```

A portal may internally use:

- Public APIs
- Official integrations
- Public job pages
- Browser automation where permitted

The rest of the system should not need to know how a portal obtains its data.

---

# 7. Search Criteria

Create a common search criteria model.

Example:

```json
{
  "keywords": [
    "AI Engineer",
    "AI Architect",
    "Technical Lead",
    "Backend Engineer"
  ],
  "locations": [
    "Hyderabad",
    "Remote"
  ],
  "experience_min": 7,
  "experience_max": 12,
  "posted_after": "2026-09-17T09:00:00+05:30"
}
```

The system should support two search modes.

### Mode 1 — Since Last Run

```text
posted_at > last_successful_run
```

### Mode 2 — Last N Days

Example:

```bash
python -m app.jobs.run --days 3
```

This searches:

```text
current_time - 3 days
```

---

# 8. Run State

The system needs to remember when the previous successful run occurred.

File:

```text
data/run_state.json
```

Example:

```json
{
  "last_successful_run": "2026-09-17T09:00:00+05:30",
  "last_run_id": "run_20260917_090000",
  "status": "SUCCESS"
}
```

Important rule:

> Update `last_successful_run` only after the collection process completes successfully.

If a run partially fails, the system must not blindly advance the timestamp and lose potentially unprocessed jobs.

---

# 9. Raw Job Model

Portal-specific data should first be represented as a `RawJob`.

Example:

```text
RawJob

- source
- raw_id
- raw_title
- raw_company
- raw_location
- raw_description
- raw_posted_date
- raw_url
- raw_metadata
```

This allows each portal adapter to return its native representation without forcing portal-specific assumptions into the core domain model.

---

# 10. Job Normalization

The normalizer converts a `RawJob` into the application's standard `Job` model.

```text
Portal Adapter
      │
      ▼
   RawJob
      │
      ▼
 JobNormalizer
      │
      ▼
    Job
```

Example normalized job:

```json
{
  "job_id": "job_a82f91",
  "portal": "naukri",
  "portal_job_id": "123456",
  "title": "AI Engineer",
  "company": "ABC Technologies",
  "location": "Hyderabad",
  "description": "...",
  "posted_at": "2026-09-17T07:20:00+05:30",
  "url": "https://example.com/job/123456",
  "discovered_at": "2026-09-18T09:00:00+05:30"
}
```

The normalized model is the only job representation used by downstream services.

---

# 11. Job Identity

Every job should have two identities.

## Portal Job ID

The identifier supplied by the job portal.

Example:

```text
naukri:123456
linkedin:987654
```

## Internal Job ID

An identifier generated by our application.

Example:

```text
job_a82f91
```

This gives us:

```text
Internal ID
    ↓
job_a82f91

Portal Identity
    ↓
naukri:123456
```

---

# 12. Deduplication

Deduplication should happen at multiple levels.

## Level 1 — Same Portal

If:

```text
portal + portal_job_id
```

already exists, the job is considered an existing listing.

Example:

```text
naukri:123456
```

## Level 2 — Cross-Portal

The same job may appear on multiple portals.

Example:

```text
LinkedIn
ABC Technologies
AI Engineer
Hyderabad

Naukri
ABC Technologies
AI Engineer
Hyderabad
```

Create a normalized fingerprint using values such as:

```text
normalized company
+
normalized title
+
normalized location
```

Example:

```text
ABC Technologies
AI Engineer
Hyderabad
```

Normalize values before generating the fingerprint.

Example:

```text
"AI Engineer"
        ↓
"ai engineer"

"Hyderabad, Telangana"
        ↓
"hyderabad"
```

A more advanced description-similarity system can be added in a later phase.

---

# 13. Job Repository

The business layer must interact with a repository abstraction.

```text
Job Service
     │
     ▼
Job Repository Interface
     │
     ▼
JSON Repository
     │
     ▼
jobs.json
```

Conceptual interface:

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

The repository implementation should be replaceable later.

Future:

```text
             JobRepository
                  │
          ┌───────┴────────┐
          ▼                ▼
   JSON Repository   PostgreSQL Repository
      Phase 1             Future
```

---

# 14. Job Storage

Initially:

```text
data/jobs.json
```

Example:

```json
{
  "jobs": [
    {
      "job_id": "job_a82f91",
      "portal": "naukri",
      "portal_job_id": "123456",
      "title": "AI Engineer",
      "company": "ABC Technologies",
      "location": "Hyderabad",
      "posted_at": "2026-09-17T07:20:00+05:30",
      "status": "DISCOVERED"
    }
  ]
}
```

The JSON repository should handle:

- File creation
- Reading
- Writing
- Validation
- Atomic updates where practical
- Missing/corrupt file handling

---

# 15. Job Status

Phase 1 should introduce the initial job status.

```text
DISCOVERED
```

Application lifecycle statuses belong to later phases.

Eventually:

```text
DISCOVERED
    ↓
MATCHED
    ↓
ELIGIBLE
    ↓
APPLICATION_STARTED
    ↓
APPLIED
```

Phase 1 only needs to establish the model and persistence mechanism.

---

# 16. Partial Failure Handling

A failure in one portal must not stop all other portals.

Bad:

```text
LinkedIn fails
     ↓
Entire job collection fails
```

Preferred:

```text
LinkedIn ── FAILED
Naukri   ── 67 jobs
Indeed   ── 31 jobs
Foundit  ── 18 jobs
```

The final run can be:

```text
PARTIAL_SUCCESS
```

with portal-level error information.

Example:

```json
{
  "portal": "linkedin",
  "status": "FAILED",
  "error_type": "TIMEOUT"
}
```

---

# 17. Retry Strategy

Each portal adapter should support configurable:

```text
timeout
retry_count
retry_delay
max_pages
max_jobs
```

Example:

```text
Request
   ↓
Timeout?
   ↓
Retry
   ↓
Retry
   ↓
Mark portal failure
```

Retries should not result in duplicate jobs.

---

# 18. Rate Limiting

Portal-specific collection should support controlled request rates.

Configuration can eventually include:

```json
{
  "request_delay_seconds": 2,
  "max_pages": 10,
  "max_jobs": 100
}
```

The system should respect applicable portal terms, robots/access controls, rate limits, and authentication requirements.

No CAPTCHA or anti-bot bypass mechanisms should be implemented.

---

# 19. CLI

Phase 1 should provide a manual execution mechanism.

Example:

```bash
python -m app.jobs.run
```

Default behavior:

```text
Use last successful run
```

Optional:

```bash
python -m app.jobs.run --days 3
```

This allows the scheduled process to be tested manually before configuring Windows Task Scheduler.

---

# 20. Scheduling

Because development is happening on a Windows laptop, use:

```text
Windows Task Scheduler
```

for the initial scheduled execution.

Architecture:

```text
Windows Task Scheduler
        ↓
Python Job Runner
        ↓
Job Collection Service
```

If the project is later deployed to Linux:

```text
cron
  ↓
Python Job Runner
```

The application itself should remain scheduler-independent.

---

# 21. Logging

Every collection run should log:

```text
run_id
portal
event
job_id
timestamp
status
error
```

Example:

```text
INFO  run_id=run_123 portal=naukri event=collection_started
INFO  run_id=run_123 portal=naukri event=jobs_collected count=67
INFO  run_id=run_123 event=duplicates_removed count=12
INFO  run_id=run_123 event=collection_completed
```

Do not log:

```text
API keys
passwords
OAuth tokens
personal credentials
sensitive candidate information
```

---

# 22. Directory Structure

Phase 1 extends the Phase 0 structure:

```text
jobHunt/
│
├── app/
│   │
│   ├── jobs/
│   │   ├── __init__.py
│   │   ├── collector.py
│   │   ├── normalizer.py
│   │   ├── deduplicator.py
│   │   ├── criteria.py
│   │   ├── run.py
│   │   │
│   │   └── portals/
│   │       ├── __init__.py
│   │       ├── base.py
│   │       ├── registry.py
│   │       ├── linkedin.py
│   │       ├── naukri.py
│   │       └── ...
│   │
│   ├── models/
│   │   ├── job.py
│   │   └── ...
│   │
│   ├── repositories/
│   │   ├── base.py
│   │   └── json_repository.py
│   │
│   └── services/
│       └── job_service.py
│
├── data/
│   ├── jobs.json
│   ├── portal_registry.json
│   ├── run_state.json
│   └── profile.json
│
├── tests/
│   │
│   └── jobs/
│       ├── test_collector.py
│       ├── test_normalizer.py
│       ├── test_deduplicator.py
│       ├── test_registry.py
│       └── test_run_state.py
│
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

# 23. Testing Strategy

Tests should cover:

## Portal Registry

```text
- Load enabled portals
- Ignore disabled portals
- Invalid portal configuration
- Unknown adapter
```

## Normalization

```text
RawJob → Job
```

Test different:

- Date formats
- Location formats
- Missing optional fields
- Missing required fields

## Deduplication

Test:

```text
Same portal + same ID
```

and:

```text
Different portals + same normalized job
```

## Run State

Test:

```text
Read last successful run
Update successful run
Do not update state on failure
```

## Collector

Test:

```text
Multiple portals
One portal failure
All portals failure
Empty results
Duplicate results
```

---

# 24. Phase 1 Completion Criteria

Phase 1 is complete when the following workflow works:

```text
Run application
      ↓
Load last successful run
      ↓
Load enabled portals
      ↓
Build search criteria
      ↓
Collect jobs
      ↓
Normalize jobs
      ↓
Deduplicate jobs
      ↓
Save new jobs
      ↓
Update run state
      ↓
Generate run summary
```

Example final output:

```text
========================================
JOB HUNT COLLECTION
========================================

Run ID: run_20260918_090000

Search window:
2026-09-17 09:00 → 2026-09-18 09:00

PORTALS
----------------------------------------
LinkedIn       42 collected
Naukri         67 collected
Indeed         31 collected
Foundit        18 collected

SUMMARY
----------------------------------------
Total collected: 158
Duplicates:       23
New jobs:         135
Failed portals:    0

Run status: SUCCESS
========================================
```

---

# 25. Explicitly Out of Scope

The following are intentionally deferred:

- AI job matching
- Resume analysis
- LLM-based job scoring
- Application automation
- Application form filling
- Resume submission
- Recruiter email processing
- Email webhooks
- Email replies
- WhatsApp notifications
- RAG
- PostgreSQL
- Redis
- Docker
- AWS deployment
- Multi-agent orchestration

These will be introduced in later phases.

---

# 26. Architecture Principle

The core principle for Phase 1 is:

> **Separate portal-specific implementation from business logic.**

The system should be able to add a new job portal by implementing a new adapter rather than modifying the Job Collector, Job Normalizer, Deduplicator, Repository, or future AI services.

The normalized `Job` model becomes the contract between Phase 1 and all future phases.

```text
              PHASE 1
                  │
                  ▼
       ┌────────────────────┐
       │  Normalized Job    │
       │                    │
       │ portal             │
       │ portal_job_id      │
       │ title              │
       │ company            │
       │ location           │
       │ description        │
       │ posted_at          │
       │ url                │
       └─────────┬──────────┘
                 │
                 ▼
              PHASE 2
           AI Job Matching
                 │
                 ▼
              PHASE 3
        Application Agent
                 │
                 ▼
              PHASE 4
            Email Agent
```

---

## Phase 1 Deliverable

At the end of Phase 1, the project should be capable of answering:

> **"What new jobs have appeared across my configured job portals since my last successful run, and which of those listings are unique?"**

It should **not yet answer whether the candidate should apply**. That decision belongs to Phase 2.