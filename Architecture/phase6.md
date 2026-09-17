# Phase 6 — PostgreSQL, Background Workers & Reliable Workflows

## 1. Objective

Phase 6 evolves the Job Hunt & Career Operations Agent from a local JSON-based prototype into a more reliable application architecture.

The main focus is:

- PostgreSQL
- Database repositories
- Background workers
- Job queues
- Retry mechanisms
- Persistent workflow state
- Scheduled execution
- Reliable asynchronous processing
- Transaction management
- Concurrency control

The system should now be capable of processing multiple jobs, applications, and emails without relying on JSON files as the primary source of truth.

---

# 2. Phase 6 Goal

The architecture evolves from:

```text
FastAPI
   ↓
JSON Files
   ↓
Direct Processing
```

to:

```text
                    FastAPI
                       │
                       ▼
                Application Services
                       │
              ┌────────┴────────┐
              ▼                 ▼
         PostgreSQL          Job Queue
                                │
                                ▼
                         Background Workers
                                │
              ┌─────────────────┼─────────────────┐
              ▼                 ▼                 ▼
          Job Worker       Application Worker   Email Worker
```

---

# 3. Why PostgreSQL

JSON storage was intentionally used during the early phases because it is simple and easy to understand.

However, the system now needs:

- Concurrent access
- Transactions
- Relationships
- Querying
- Indexes
- Constraints
- Durable state
- Audit history
- Scalable storage

PostgreSQL becomes the primary persistent datastore.

---

# 4. Database Architecture

```text
Application
     │
     ▼
Repository Interface
     │
     ▼
PostgreSQL Repository
     │
     ▼
PostgreSQL
```

Business logic must not directly execute SQL.

Use:

```text
Service
   ↓
Repository
   ↓
Database
```

This preserves the architecture established in earlier phases.

---

# 5. Repository Abstraction

The repository interface should remain independent of the database implementation.

Example:

```python
class JobRepository:
    def get(self, job_id):
        pass

    def save(self, job):
        pass

    def update(self, job):
        pass

    def list(self, filters=None):
        pass
```

Existing JSON repositories can remain available for local tests.

New implementation:

```text
JobRepository
 ├── JsonJobRepository
 └── PostgresJobRepository
```

The same pattern should be applied to:

```text
Candidate
Job
Application
Email
Review
AuditEvent
RunState
```

---

# 6. Database Technology

Initial stack:

```text
PostgreSQL
SQLAlchemy
Alembic
Pydantic
FastAPI
```

Recommended architecture:

```text
Pydantic Models
      ↓
Service Layer
      ↓
SQLAlchemy Repository
      ↓
PostgreSQL
```

---

# 7. Database Entities

The initial schema should include:

```text
candidates
jobs
job_portals
applications
emails
email_threads
reviews
decisions
audit_events
run_states
```

Additional tables can be introduced when required.

---

# 8. Candidate Table

Example fields:

```text
candidates
-----------
id
name
email
phone
location
experience_years
resume_path
created_at
updated_at
```

Candidate-specific structured data can be stored using appropriate PostgreSQL types where useful.

---

# 9. Jobs Table

Example:

```text
jobs
----
id
portal
portal_job_id
title
company
location
description
posted_at
url
discovered_at
content_hash
created_at
updated_at
```

Important indexes:

```text
portal + portal_job_id
company
posted_at
content_hash
```

---

# 10. Applications Table

Example:

```text
applications
------------
id
job_id
candidate_id
portal
portal_job_id
company
role
status
match_score
resume_path
automation_mode
agent_version
applied_at
created_at
updated_at
```

A uniqueness constraint should prevent duplicate applications.

Example:

```text
candidate_id + portal + portal_job_id
```

---

# 11. Emails Table

Example:

```text
emails
------
id
provider
provider_message_id
thread_id
sender
recipient
subject
category
intent
application_id
job_id
processing_status
received_at
processed_at
created_at
updated_at
```

Unique identity:

```text
provider + provider_message_id
```

---

# 12. Reviews Table

Example:

```text
reviews
-------
id
type
email_id
application_id
job_id
status
requested_action
expires_at
created_at
updated_at
```

This stores the human-in-the-loop state introduced in Phase 5.

---

# 13. Decisions Table

Example:

```text
decisions
---------
id
review_id
decision
source
validated
created_at
```

A review may have one final decision.

---

# 14. Audit Events

Create an append-only audit table.

Example:

```text
audit_events
------------
id
event_type
entity_type
entity_id
metadata
created_at
```

Example:

```json
{
  "event_type": "APPLICATION_SUBMITTED",
  "entity_type": "application",
  "entity_id": "app_72fa91"
}
```

Audit events should generally not be modified after creation.

---

# 15. Database Migrations

Use Alembic.

Example:

```bash
alembic init migrations
```

Migration flow:

```text
Model Change
     ↓
Alembic Migration
     ↓
Review Migration
     ↓
Apply Migration
     ↓
PostgreSQL
```

Never manually modify production database schemas without migrations.

---

# 16. Environment Configuration

Example:

```env
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/jobhunt

DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20

WORKER_ENABLED=true
```

Credentials must remain outside Git.

---

# 17. Connection Management

The application should use a connection pool.

```text
FastAPI
   ↓
SQLAlchemy Engine
   ↓
Connection Pool
   ↓
PostgreSQL
```

Do not create a new database connection for every request.

---

# 18. Transactions

Database updates that must happen together should use transactions.

Example:

```text
Create Application
      +
Create Audit Event
      ↓
Single Transaction
```

If one operation fails:

```text
Rollback
```

This prevents inconsistent state.

---

# 19. Background Workers

Long-running tasks should not block FastAPI requests.

Examples:

```text
Job collection
Job matching
Application processing
Email processing
Email reply generation
Human-review notifications
```

Instead:

```text
API
 ↓
Queue
 ↓
Worker
 ↓
Process
```

---

# 20. Queue Architecture

Introduce a job queue.

Possible initial technology:

```text
Redis + Celery
```

or another lightweight Python-compatible queue system.

The queue abstraction should remain replaceable.

Architecture:

```text
Producer
   ↓
Queue
   ↓
Worker
```

---

# 21. Worker Types

Initial workers:

```text
JobCollectionWorker
JobMatchingWorker
ApplicationWorker
EmailWorker
HITLWorker
```

Example:

```text
Email Webhook
     ↓
Queue
     ↓
Email Worker
     ↓
Email Agent
```

---

# 22. Task Model

Every background task should have a structured identity.

Example:

```json
{
  "task_id": "task_8921",
  "task_type": "EMAIL_PROCESSING",
  "entity_id": "email_123",
  "status": "QUEUED"
}
```

Possible states:

```text
QUEUED
RUNNING
COMPLETED
FAILED
RETRYING
CANCELLED
```

---

# 23. Retry Strategy

Transient failures should be retried.

Examples:

```text
Network timeout
Temporary provider failure
LLM timeout
Database connection failure
```

Example:

```text
Attempt 1
   ↓
Failure
   ↓
Retry
   ↓
Attempt 2
   ↓
Failure
   ↓
Retry
   ↓
Attempt 3
   ↓
Failed
```

Use exponential backoff.

---

# 24. Dead-Letter Handling

Tasks that repeatedly fail should not retry forever.

Example:

```text
Task
 ↓
Retry 1
 ↓
Retry 2
 ↓
Retry 3
 ↓
Dead Letter
```

Store failed tasks for investigation.

Example:

```text
dead_letter_tasks
```

---

# 25. Idempotent Workers

Workers must be safe to execute more than once.

Example:

```text
Application Worker
      ↓
Check application status
      ↓
Already submitted?
      ↓
YES → Do not submit again
```

Similarly:

```text
Email Worker
      ↓
Check provider_message_id
      ↓
Already processed?
      ↓
YES → Stop
```

---

# 26. Concurrency Control

Multiple workers may attempt to process the same entity.

Use database-level mechanisms where appropriate.

Examples:

```text
Row locking
Unique constraints
Optimistic locking
Task ownership
Status transitions
```

Never rely only on in-memory flags.

---

# 27. Workflow State

Application workflows should persist their state.

Example:

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

If the worker crashes:

```text
Worker crash
     ↓
Application state remains persisted
     ↓
Worker can safely recover
```

---

# 28. State Transition Validation

Do not allow arbitrary status changes.

Example:

```text
DISCOVERED → MATCHED
MATCHED → ELIGIBLE
ELIGIBLE → APPLICATION_STARTED
```

But:

```text
DISCOVERED → SUBMITTED
```

should be rejected.

Create a deterministic state machine.

---

# 29. Scheduled Jobs

The system still needs scheduled execution for job hunting.

Example:

```text
Windows Task Scheduler
        ↓
Application
        ↓
Queue
        ↓
Job Collection Worker
```

Later in cloud deployment:

```text
Cloud Scheduler
        ↓
Queue
        ↓
Worker
```

The scheduler should trigger tasks, not perform the entire workflow itself.

---

# 30. Job Hunt Pipeline

Phase 6 flow:

```text
Scheduler
    ↓
Create Job Collection Task
    ↓
Queue
    ↓
Job Worker
    ↓
Collect Jobs
    ↓
Persist PostgreSQL
    ↓
Create Matching Tasks
    ↓
Queue
    ↓
Matching Worker
    ↓
Persist Matches
```

---

# 31. Email Pipeline

```text
Gmail Webhook
      ↓
Validate Event
      ↓
Create Email Task
      ↓
Queue
      ↓
Email Worker
      ↓
Email Agent
      ↓
PostgreSQL
      ↓
Action / HITL Task
```

---

# 32. Application Pipeline

```text
Eligible Application
       ↓
Application Task
       ↓
Queue
       ↓
Application Worker
       ↓
Browser Automation
       ↓
Policy Validation
       ↓
Application Result
       ↓
PostgreSQL
```

Sensitive or ambiguous cases must remain human-controlled.

---

# 33. Database as Source of Truth

From Phase 6 onward:

```text
PostgreSQL = Source of Truth
```

JSON files should primarily be used for:

```text
Fixtures
Local development
Testing
Configuration examples
```

Do not maintain two independent production sources of truth.

---

# 34. Data Migration

Existing JSON data should be migrated into PostgreSQL.

Example:

```text
jobs.json
   ↓
Migration Script
   ↓
jobs table
```

Same for:

```text
applications.json
emails.json
reviews.json
```

Migration must be idempotent.

Running it twice must not create duplicates.

---

# 35. Database Indexing

Create indexes based on actual query patterns.

Important examples:

```text
jobs(posted_at)
jobs(company)
jobs(portal, portal_job_id)

applications(status)
applications(candidate_id, portal, portal_job_id)

emails(provider, provider_message_id)
emails(application_id)
emails(received_at)

reviews(status)
reviews(expires_at)
```

Avoid creating unnecessary indexes.

---

# 36. API Changes

FastAPI endpoints can now read/write PostgreSQL.

Example:

```text
GET /jobs
GET /jobs/{job_id}

GET /applications
GET /applications/{application_id}

GET /emails
GET /reviews/pending
```

For mutations:

```text
POST /reviews/{review_id}/decision
```

All mutations must go through services and policies.

---

# 37. Health Checks

Expand:

```text
GET /health
```

to include dependency health.

Example:

```json
{
  "status": "ok",
  "database": "ok",
  "queue": "ok"
}
```

Do not expose credentials or connection details.

---

# 38. Graceful Shutdown

Workers and FastAPI should shut down gracefully.

On shutdown:

```text
Stop accepting new tasks
        ↓
Finish safe in-progress work
        ↓
Close database connections
        ↓
Close queue connections
        ↓
Exit
```

Do not abruptly terminate critical workflows where avoidable.

---

# 39. Observability

Track:

```text
queue_depth
task_duration
task_failures
retry_count
database_connections
database_query_latency
worker_health
workflow_failures
```

Example:

```text
email_processing_duration
job_collection_duration
matching_duration
application_processing_duration
```

Detailed observability infrastructure remains part of Phase 8.

---

# 40. Security

Database credentials must never be:

```text
Committed
Logged
Returned through API
Embedded in source code
```

Use:

```text
.env
Environment Variables
Secret Manager later
```

Workers must use least-privilege database credentials.

---

# 41. Testing

Add:

```text
tests/
├── test_db_connection.py
├── test_repositories_postgres.py
├── test_transactions.py
├── test_state_machine.py
├── test_workers.py
├── test_retry.py
├── test_idempotency.py
├── test_migrations.py
└── test_task_queue.py
```

Use a dedicated test database.

Do not run destructive tests against production data.

---

# 42. Integration Testing

Test complete flows.

Example:

```text
Webhook
  ↓
Queue
  ↓
Worker
  ↓
Service
  ↓
PostgreSQL
```

Example email test:

```text
Fake Email Event
      ↓
Webhook
      ↓
Queue
      ↓
Email Worker
      ↓
Mock LLM
      ↓
PostgreSQL
```

---

# 43. Local Development

Recommended local architecture:

```text
Laptop
│
├── FastAPI
├── PostgreSQL
├── Redis
├── Worker
└── Scheduler
```

Example:

```text
localhost:8000 → FastAPI
localhost:5432 → PostgreSQL
localhost:6379 → Redis
```

---

# 44. Docker

Docker may be introduced during Phase 6 for local infrastructure consistency.

Possible services:

```text
api
worker
postgres
redis
```

Example:

```text
docker compose
     │
     ├── API
     ├── Worker
     ├── PostgreSQL
     └── Redis
```

Cloud deployment remains Phase 8.

---

# 45. Configuration Separation

Separate:

```text
Application Configuration
Environment Configuration
Infrastructure Configuration
Secrets
```

Example:

```text
.env
.env.example
docker-compose.yml
```

Never place production credentials in Docker Compose committed to Git.

---

# 46. Database Backup Strategy

Even during local development, understand backup/recovery.

Example:

```text
PostgreSQL
   ↓
Backup
   ↓
Restore
```

Cloud backup and disaster recovery will be expanded in Phase 8.

---

# 47. Phase 5 → Phase 6 Contract

Phase 5 produces:

```text
reviews
decisions
notifications
workflow events
```

Phase 6 persists these in PostgreSQL and processes them asynchronously.

Example:

```text
WhatsApp Response
       ↓
Review Decision
       ↓
Queue
       ↓
Worker
       ↓
Policy
       ↓
Workflow Update
```

---

# 48. Phase 6 → Phase 7 Contract

Phase 6 provides persistent structured data that Phase 7 can use to build the candidate knowledge layer.

Examples:

```text
Candidate profile
Resume
Skills
Experience
Previous applications
Job descriptions
Recruiter conversations
Interview information
Application history
```

Phase 7 will introduce:

```text
RAG
Embeddings
Vector Database
Candidate Knowledge Base
```

---

# 49. Definition of Done

Phase 6 is complete when:

- PostgreSQL is the primary datastore
- Database migrations are implemented
- Repository abstraction supports PostgreSQL
- Existing JSON data can be migrated
- Application state is persisted
- Email state is persisted
- HITL state is persisted
- Background workers are operational
- Tasks can be queued
- Tasks support retries
- Failed tasks can be isolated
- Workers are idempotent
- Workflow transitions are validated
- Database transactions are used correctly
- Duplicate processing is prevented
- Local development infrastructure is reproducible
- Automated tests pass

---

# 50. Phase 6 Acceptance Scenario

Given:

```text
50 eligible jobs
```

The system should be able to:

```text
Eligible Jobs
      ↓
Create Tasks
      ↓
Queue
      ↓
Workers
      ↓
Process Concurrently
      ↓
Persist Results
      ↓
Retry Temporary Failures
      ↓
Record Permanent Failures
```

If the worker crashes:

```text
Worker Crash
      ↓
Persisted State
      ↓
Task Recovery / Retry
      ↓
Continue Safely
```

No job should be accidentally applied to twice because of a worker restart.

---

# 51. Architectural Principles Learned in Phase 6

### Persistent state

```text
Database > Files
```

### Asynchronous processing

```text
Request
  ↓
Queue
  ↓
Worker
```

### Reliability

```text
Failure
  ↓
Retry
  ↓
Dead Letter
```

### Idempotency

```text
Same Task
   ↓
Safe to execute again
```

### Transactional consistency

```text
Related Updates
      ↓
Transaction
      ↓
Commit / Rollback
```

### Scalable architecture

```text
Producers
    ↓
Queue
    ↓
Workers
    ↓
Database
```

---

# 52. Git Milestone

Suggested milestone:

```text
v0.6.0
```

Suggested commit:

```text
feat: introduce postgres persistence and background workers
```

---

# 53. Phase 6 Completion Statement

At the end of Phase 6, the Job Hunt & Career Operations Agent should no longer behave like a collection of scripts.

It should behave like a **reliable backend system** with:

```text
Persistent State
      +
Asynchronous Processing
      +
Reliable Workflows
      +
Retry Handling
      +
Database Transactions
      +
Human-in-the-Loop