## AI Job Hunt & Career Operations Agent

### Project Goal

Build an AI-powered job hunting system that can autonomously discover relevant job opportunities from multiple job portals, evaluate them against a candidate profile, apply to suitable jobs, track every application, monitor recruiter emails, and notify the user whenever human action is required.

The project will initially run **locally on a laptop**, use **file-based storage**, and be developed incrementally with Git/GitHub as an AI Architecture practice project.

### What the system will do

1. **Job Portal Discovery**
   - Start with known portals such as LinkedIn and Naukri.
   - Discover additional relevant job portals through a scripted discovery process.
   - Validate portals before adding them to the system.
   - Maintain a portal registry and portal-specific adapters.

2. **Scheduled Job Search**
   - Run as a **cron job**.
   - Search configured job portals.
   - Find jobs posted since the previous run or within a configurable number of days.
   - Normalize jobs from different portals into a common format.
   - Deduplicate the same job appearing across multiple portals.

3. **AI Job Matching**
   - Maintain candidate information in a configuration/profile file.
   - Compare job requirements with the candidate's skills, experience, location and preferences.
   - Use an LLM for semantic matching.
   - Generate a structured match result and score.
   - Apply configurable rules before deciding whether a job is eligible.

4. **AI-Powered Application**
   - Automatically process eligible applications where permitted.
   - Use browser automation such as Playwright where appropriate and allowed.
   - Fill known candidate information.
   - Generate suitable answers for application questions using the LLM.
   - Initially operate in **dry-run mode** so applications can be reviewed before submission.
   - Enable automatic submission only after the workflow has been validated.

5. **Application Tracking**
   - Store every discovered job and application.
   - Track application lifecycle/status.
   - Prevent duplicate applications.
   - Maintain timestamps and relevant metadata.
   - Initially store information in JSON files.

Example statuses:

```text
DISCOVERED
MATCHED
ELIGIBLE
APPLICATION_STARTED
APPLIED
EMAIL_RECEIVED
ACTION_REQUIRED
USER_NOTIFIED
REPLIED
INTERVIEW
OFFER
REJECTED
SKIPPED
FAILED
```

6. **Recruiter Email Monitoring**
   - Receive email events through a webhook/event mechanism.
   - Analyze incoming recruiter emails using an LLM.
   - Identify company, role, intent and required actions.
   - Match emails back to existing job applications.
   - Detect interview invitations, requests for information, scheduling requests, rejections, etc.

7. **Email Action Agent**
   - Determine whether an email requires action.
   - Automatically perform only predefined safe actions.
   - Generate draft replies when appropriate.
   - Escalate important or sensitive actions to the user instead of acting automatically.

8. **Human-in-the-Loop Notifications**
   - Send WhatsApp notifications when user intervention is required.
   - Include:
     - Company
     - Job role
     - Email subject
     - Required action
     - Deadline/interview information
     - Link to the email thread
   - Allow the user to review/approve the required action.

### High-Level Architecture

```text
                    ┌─────────────────────┐
                    │    Job Portals      │
                    │ LinkedIn / Naukri / │
                    │ Other Portals       │
                    └──────────┬──────────┘
                               │
                         Scheduled Cron
                               │
                               ▼
                       Job Collection Layer
                               │
                               ▼
                     Normalize + Deduplicate
                               │
                               ▼
                       Job Matching Agent
                               │
                         LLM / Gemini
                               │
                               ▼
                         Policy Engine
                         /           \
                      SKIP           APPLY
                                      │
                                      ▼
                             Application Agent
                                      │
                                      ▼
                              Application Status
                                      │
                                      ▼
                              JSON File Storage


Email Provider
      │
      ▼
   Webhook
      │
      ▼
  Email Agent
      │
      ▼
 Action / Intent Detection
      │
      ├───────────────┐
      ▼               ▼
 Safe Action      Human Action
      │               │
      ▼               ▼
 Reply/Action      WhatsApp
                      │
                      ▼
                    User
```

### Initial Technology Stack

- **Python**
- **FastAPI**
- **Gemini API**
- **Gemini Code Assist** for AI-assisted development
- **Playwright** for permitted browser automation
- **Cron** for scheduled job processing
- **JSON files** for initial persistence
- **Git + GitHub** for version control
- **Gmail/API + webhook mechanism** for email events
- **WhatsApp Business/API provider** for notifications

### AI Architecture Concepts Practiced

This project is intended to demonstrate practical understanding of:

- LLM integration
- Structured LLM output
- AI agents
- Tool calling
- Agent orchestration
- Event-driven architecture
- Webhooks
- Scheduled workflows
- Browser automation
- State machines
- Human-in-the-loop systems
- Policy/rule engines
- Idempotency
- Deduplication
- Error handling and retries
- Logging and observability
- Provider abstraction
- Eventually RAG and persistent memory

### Development Principle

**LLMs provide intelligence; deterministic software controls execution.**

The LLM should analyze, classify, extract, match and generate. Critical actions such as applying, replying, or sending information should be controlled by explicit application rules and human approval where appropriate.

### Future Evolution

```text
Phase 0 → Project foundation
Phase 1 → Job discovery
Phase 2 → AI matching
Phase 3 → Application automation
Phase 4 → Email webhook + Email Agent
Phase 5 → WhatsApp + Human-in-the-loop
Phase 6 → PostgreSQL + background workers
Phase 7 → RAG / candidate knowledge base
Phase 8 → Cloud deployment + observability
```

**Core idea:** build this as a real-world **AI Agent + Event-Driven Automation system**, while keeping the first version simple enough to run entirely on a local laptop.