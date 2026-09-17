# Phase 5 — Human-in-the-Loop & WhatsApp Agent

## 1. Objective

Phase 5 introduces the **Human-in-the-Loop (HITL) layer** for the Job Hunt & Career Operations Agent.

The system can now detect situations where AI should not act autonomously and ask the user for a decision through WhatsApp.

The goal is not to make the system fully autonomous.

The goal is:

> **AI handles routine decisions. Humans handle sensitive, ambiguous, or high-impact decisions.**

Phase 5 connects:

```text
Job Agent
Email Agent
Application Agent
       ↓
Human Review Engine
       ↓
WhatsApp
       ↓
User Decision
       ↓
Workflow Resumes
```

---

# 2. Phase 5 Goal

Phase 5 should allow the system to:

- Detect when human input is required
- Create a structured review request
- Send the request through WhatsApp
- Provide enough context for the user to make a decision
- Accept the user's response
- Validate the response
- Resume the appropriate workflow
- Track the decision
- Maintain an audit trail
- Prevent duplicate actions

Example:

```text
Recruiter asks:
"What are your salary expectations?"

        ↓

Email Agent
        ↓

Policy Engine
        ↓

Human Review Required
        ↓
WhatsApp

"Example Corp is asking for salary expectations
for AI Architect role.

How would you like to respond?"

[Reply manually]
[Use saved preference]
[Ignore]
```

The user decides.

---

# 3. Why Human-in-the-Loop Is Required

Certain actions should not be fully automated.

Examples:

```text
Salary expectations
Salary negotiation
Offer acceptance
Offer rejection
Joining date
Relocation
Work authorization
Visa information
Legal declarations
Sensitive personal information
Ambiguous interview scheduling
Unknown candidate information
Conflicting recruiter requests
```

The AI should not guess the user's preference.

Instead:

```text
Unknown
   ↓
Ask Human
   ↓
Receive Decision
   ↓
Continue Workflow
```

---

# 4. Architecture

```text
                         ┌───────────────────┐
                         │   Job Agent       │
                         └─────────┬─────────┘
                                   │
                         ┌─────────▼─────────┐
                         │   Email Agent     │
                         └─────────┬─────────┘
                                   │
                              Action Needed
                                   │
                         ┌─────────▼─────────┐
                         │ HITL Review Engine │
                         └─────────┬─────────┘
                                   │
                            Review Request
                                   │
                         ┌─────────▼─────────┐
                         │     WhatsApp      │
                         └─────────┬─────────┘
                                   │
                              User Response
                                   │
                         ┌─────────▼─────────┐
                         │ Response Handler  │
                         └─────────┬─────────┘
                                   │
                         ┌─────────▼─────────┐
                         │ Policy Validation │
                         └─────────┬─────────┘
                                   │
                         ┌─────────▼─────────┐
                         │ Resume Workflow   │
                         └───────────────────┘
```

---

# 5. Core Design Principle

The most important rule in Phase 5:

> **WhatsApp is an interface for human decisions, not an authorization bypass.**

A WhatsApp message such as:

```text
"Yes"
```

must not automatically mean:

```text
Do anything the AI previously wanted.
```

The response must be tied to:

```text
review_id
requested_action
application_id
current workflow state
allowed decisions
```

---

# 6. Human Review Model

Create a structured review object.

Example:

```json
{
  "review_id": "review_9281",
  "type": "SALARY_INFORMATION_REQUEST",
  "email_id": "email_8a72f1",
  "application_id": "app_72fa91",
  "job_id": "job_a82f91",
  "company": "Example Corp",
  "role": "AI Architect",
  "reason": "Recruiter requested salary expectations",
  "requested_action": "USER_RESPONSE",
  "status": "PENDING",
  "created_at": "2026-09-18T10:30:00"
}
```

Possible states:

```text
PENDING
NOTIFIED
USER_RESPONDED
APPROVED
REJECTED
EXPIRED
CANCELLED
COMPLETED
FAILED
```

---

# 7. Review Request Types

Initial supported review types:

```text
SALARY_REQUEST
INTERVIEW_CONFIRMATION
INTERVIEW_RESCHEDULE
OFFER_REVIEW
JOINING_DATE
RELOCATION
WORK_AUTHORIZATION
UNKNOWN_CANDIDATE_INFORMATION
AMBIGUOUS_EMAIL
APPLICATION_EXCEPTION
MANUAL_REPLY_REQUIRED
```

More types can be added later.

---

# 8. Human Review Engine

Create:

```text
app/hitl/
```

Suggested components:

```text
app/hitl/
├── __init__.py
├── models.py
├── review_service.py
├── review_policy.py
├── response_handler.py
└── repository.py
```

Responsibilities:

```text
Create review
      ↓
Store review
      ↓
Notify user
      ↓
Wait for response
      ↓
Validate response
      ↓
Resume workflow
      ↓
Record outcome
```

---

# 9. WhatsApp Provider Abstraction

Do not couple the application directly to one WhatsApp provider.

Create:

```python
class WhatsAppProvider:
    def send_message(self, message):
        pass

    def receive_message(self, event):
        pass
```

Potential implementation:

```text
WhatsAppProvider
       │
       └── WhatsAppBusinessProvider
```

The provider implementation can later be changed without changing HITL business logic.

---

# 10. WhatsApp Integration

Use an official WhatsApp Business/API integration or another permitted provider.

The architecture should support:

```text
Outbound:

Application
     ↓
WhatsApp Provider
     ↓
WhatsApp
     ↓
User
```

Inbound:

```text
User
 ↓
WhatsApp
 ↓
Provider Webhook
 ↓
FastAPI
 ↓
Response Handler
```

Do not use unofficial automation that attempts to imitate a WhatsApp client or bypass platform controls.

---

# 11. WhatsApp Webhook

Add an endpoint such as:

```text
POST /webhooks/whatsapp
```

Flow:

```text
WhatsApp message
       ↓
Webhook
       ↓
Validate provider event
       ↓
Extract sender/message
       ↓
Find pending review
       ↓
Validate response
       ↓
Resume workflow
```

Webhook processing must be idempotent.

---

# 12. Review-to-Message Mapping

Every WhatsApp notification must contain a reference to the review.

Example:

```text
Review ID: review_9281
Company: Example Corp
Role: AI Architect

Recruiter asked for your salary expectations.

Please choose:

1. Reply manually
2. Use saved preference
3. Ignore
```

Internally:

```text
WhatsApp response
      ↓
review_id = review_9281
      ↓
Review record
      ↓
requested_action = USER_RESPONSE
```

Never infer the review only from message text.

---

# 13. Supported Response Types

The response handler should support structured responses.

Example:

```text
1
```

means:

```text
REPLY_MANUALLY
```

or:

```text
2
```

means:

```text
USE_SAVED_PREFERENCE
```

Natural-language responses can also be supported:

```text
"Yes, confirm it"
"Don't respond"
"Ask them for another time"
```

However, natural-language responses must be interpreted and validated before execution.

---

# 14. Ambiguous User Responses

If the response is unclear:

```text
User:
"Maybe"
```

The system should NOT guess.

Instead:

```text
I'm not sure which action you want.

Please choose:
1. Confirm
2. Decline
3. Reschedule
```

This is another example of:

```text
Uncertainty → Human clarification
```

---

# 15. Example — Interview Confirmation

Recruiter:

```text
We would like to schedule your interview
for Tuesday at 3 PM.
Please confirm.
```

Email Agent:

```text
INTERVIEW_CONFIRMATION_REQUIRED
```

HITL Engine:

```text
Review created:
review_1001
```

WhatsApp:

```text
Example Corp
AI Architect

Interview:
Tuesday, 3:00 PM

Recruiter is asking you to confirm.

Reply:
1 - Confirm
2 - Ask for another time
3 - Decline
```

User:

```text
1
```

System:

```text
review_1001
      ↓
APPROVED
      ↓
Generate confirmation draft
      ↓
Policy validation
      ↓
Send if permitted
      ↓
Update review
```

---

# 16. Example — Salary Request

Recruiter:

```text
Could you please share your expected compensation?
```

Email Agent:

```text
SALARY_REQUEST
```

HITL:

```text
USER_REVIEW_REQUIRED
```

WhatsApp:

```text
Example Corp is asking for your expected compensation
for the AI Architect role.

This requires your decision.

Options:

1. Reply manually
2. Use saved preference
3. Ignore
```

The system must not invent a salary expectation.

---

# 17. Example — Offer Email

Recruiter:

```text
We are pleased to offer you the position...
```

Email Agent:

```text
OFFER_REVIEW
```

WhatsApp:

```text
You received an offer from Example Corp
for AI Architect.

Offer requires your review.

Open email:
<email thread link>

Options:
1. Review manually
2. Request more information
3. Decline
```

The system must not automatically accept or reject the offer.

---

# 18. Review Policy

The HITL policy determines when a human decision is required.

Example:

```python
class ReviewPolicy:

    def requires_review(self, intent):
        if intent in {
            "SALARY_REQUEST",
            "OFFER_ACCEPTANCE",
            "WORK_AUTHORIZATION",
            "LEGAL_DECLARATION"
        }:
            return True

        return False
```

This policy must remain deterministic.

The LLM should not override it.

---

# 19. Human Decision vs AI Decision

Use this separation:

```text
AI
│
├── Understand email
├── Extract intent
├── Identify relevant application
├── Explain situation
└── Suggest possible actions
          │
          ▼
      HUMAN DECISION
          │
          ▼
Deterministic Policy
          │
          ▼
     External Action
```

The AI can recommend.

The user authorizes.

The policy engine validates.

The service executes.

---

# 20. Decision Object

Create a structured decision.

Example:

```json
{
  "review_id": "review_1001",
  "decision": "CONFIRM",
  "source": "WHATSAPP",
  "received_at": "2026-09-18T11:05:00",
  "validated": true
}
```

For a manual response:

```json
{
  "review_id": "review_1002",
  "decision": "MANUAL_REPLY",
  "response_text": "I would prefer a range of ...",
  "source": "WHATSAPP",
  "validated": true
}
```

Sensitive values should not be unnecessarily logged.

---

# 21. Expiration

Review requests should have an expiration time.

Example:

```text
created_at = 10:00
expires_at = 24 hours later
```

If expired:

```text
PENDING
   ↓
EXPIRED
```

Do not automatically execute the old request.

For time-sensitive interview invitations, the expiration can be shorter.

---

# 22. Stale Decision Protection

A decision must only apply to the workflow state for which it was created.

Example:

```text
Review created
   ↓
User receives WhatsApp
   ↓
Application state changes independently
   ↓
User responds
```

Before executing the decision:

```text
Check current application state
Check review state
Check requested action
Check review version
```

If the workflow has changed:

```text
STALE_REVIEW
     ↓
USER_REVIEW_REQUIRED
```

---

# 23. Idempotency

WhatsApp webhooks can be retried.

The same user response must not trigger the action twice.

Use:

```text
provider_message_id
```

as the external event identity.

Also enforce:

```text
review_id + decision
```

processing constraints.

Example:

```text
User sends "1"
     ↓
Decision processed
     ↓
Review = COMPLETED
```

If the same event arrives again:

```text
Already processed
     ↓
Ignore
```

---

# 24. Audit Trail

Every human decision must be recorded.

Example:

```json
{
  "event": "HUMAN_DECISION",
  "review_id": "review_1001",
  "decision": "CONFIRM",
  "source": "WHATSAPP",
  "timestamp": "2026-09-18T11:05:00"
}
```

Audit events:

```text
REVIEW_CREATED
REVIEW_NOTIFIED
REVIEW_RESPONSE_RECEIVED
REVIEW_VALIDATED
HUMAN_DECISION
WORKFLOW_RESUMED
REVIEW_COMPLETED
REVIEW_EXPIRED
REVIEW_FAILED
```

---

# 25. Security

The WhatsApp channel must be treated as an external input.

Do not trust a message merely because it looks like:

```text
"Yes"
```

Validate:

```text
Sender
Provider event
Review ID
Pending review
Allowed decision
Current workflow state
```

The system must ensure that one user cannot manipulate another user's workflow.

---

# 26. Sender Verification

The inbound WhatsApp event should be validated against the configured user identity.

Example:

```text
WhatsApp sender
       ↓
Known authorized user?
       ↓
YES → Continue
NO  → Reject
```

Do not expose application information to unauthorized senders.

---

# 27. Sensitive Information

WhatsApp messages may contain sensitive information.

Avoid placing unnecessary sensitive details in notifications.

Instead of:

```text
Full personal information...
```

prefer:

```text
Example Corp
AI Architect

Recruiter requested additional information.

Open email:
<thread link>
```

Only show information required for the decision.

---

# 28. Link to Email Thread

For email-related reviews, provide a direct link to the email thread when available.

Example:

```text
Open recruiter email:
<email_thread_url>
```

The user can inspect the original message before deciding.

---

# 29. HITL Repository

Initially continue using JSON.

Example:

```text
data/
├── emails.json
├── applications.json
├── jobs.json
├── reviews.json
└── decisions.json
```

Example `reviews.json`:

```json
[
  {
    "review_id": "review_1001",
    "type": "INTERVIEW_CONFIRMATION",
    "email_id": "email_8a72f1",
    "application_id": "app_72fa91",
    "status": "PENDING",
    "created_at": "2026-09-18T10:30:00"
  }
]
```

---

# 30. Suggested Project Structure

Extend the project:

```text
app/
├── hitl/
│   ├── __init__.py
│   ├── models.py
│   ├── review_service.py
│   ├── review_policy.py
│   ├── response_handler.py
│   └── repository.py
│
├── whatsapp/
│   ├── __init__.py
│   ├── base.py
│   ├── provider.py
│   ├── message_builder.py
│   └── webhook.py
│
├── email/
│   └── ...
│
├── agents/
│   └── ...
│
└── api/
    ├── email_webhook.py
    └── whatsapp_webhook.py
```

---

# 31. Message Builder

WhatsApp messages should be generated using structured templates rather than allowing the LLM to freely construct the entire notification.

Example:

```python
def build_review_message(review):
    return (
        f"{review.company}\n"
        f"{review.role}\n\n"
        f"{review.reason}\n\n"
        f"Reply with one of the available options."
    )
```

The LLM may help summarize the email, but the final notification format should be controlled by application code.

---

# 32. LLM Usage in Phase 5

The LLM can help with:

```text
Summarizing recruiter messages
Explaining the situation
Interpreting natural-language user responses
Generating reply drafts
Extracting structured information
```

The LLM should NOT:

```text
Authorize an action
Bypass policy
Determine user consent
Access WhatsApp credentials
Choose sensitive user preferences
```

---

# 33. Natural Language Decision Processing

Example:

```text
User:
"Yeah, Tuesday at 3 works for me"
```

LLM:

```json
{
  "intent": "CONFIRM_INTERVIEW",
  "confidence": 0.97
}
```

Policy:

```text
Is CONFIRM_INTERVIEW allowed for this review?
YES
```

Workflow:

```text
Generate confirmation
      ↓
Validate
      ↓
Send
```

If confidence is low:

```text
User:
"Maybe Tuesday"
```

Then:

```text
CONFIDENCE LOW
      ↓
Ask clarification
```

---

# 34. User Preferences

Future versions may support saved preferences.

Example:

```json
{
  "interview_confirmation": "ask_user",
  "salary_response": "ask_user",
  "recruiter_followup": "draft_first"
}
```

However, Phase 5 should not assume preferences that the user has not explicitly configured.

---

# 35. Action Authorization Levels

Define explicit authorization levels.

```text
LEVEL_0
Observe only

LEVEL_1
Classify and summarize

LEVEL_2
Create drafts

LEVEL_3
Perform low-risk approved actions

LEVEL_4
Sensitive actions requiring explicit human approval
```

Initial Phase 5 should operate primarily at:

```text
LEVEL_1
LEVEL_2
LEVEL_4
```

---

# 36. Example End-to-End Flow

```text
Recruiter
   │
   ▼
Gmail
   │
   ▼
Email Webhook
   │
   ▼
Email Agent
   │
   ▼
"Interview invitation"
   │
   ▼
Application Association
   │
   ▼
Policy Engine
   │
   ▼
Human Review Required
   │
   ▼
Review Service
   │
   ▼
WhatsApp
   │
   ▼
User
   │
   ▼
"Confirm"
   │
   ▼
WhatsApp Webhook
   │
   ▼
Response Handler
   │
   ▼
Review Validation
   │
   ▼
Policy Engine
   │
   ▼
Email Service
   │
   ▼
Recruiter
```

---

# 37. Failure Handling

Possible errors:

```text
WHATSAPP_PROVIDER_ERROR
WHATSAPP_WEBHOOK_ERROR
INVALID_SENDER
REVIEW_NOT_FOUND
REVIEW_EXPIRED
INVALID_DECISION
AMBIGUOUS_DECISION
STALE_REVIEW
EMAIL_SEND_FAILED
LLM_ERROR
POLICY_REJECTED
UNKNOWN_ERROR
```

Every failure should produce a recoverable state.

---

# 38. Safe Retry Rules

Safe retries:

```text
WhatsApp network timeout
Temporary provider failure
LLM timeout
Webhook processing failure
```

Do not blindly retry:

```text
Email send with unknown result
Completed review
Sensitive action
Expired review
Stale review
```

---

# 39. Testing Strategy

Add:

```text
tests/
├── test_hitl_models.py
├── test_review_service.py
├── test_review_policy.py
├── test_response_handler.py
├── test_whatsapp_message_builder.py
├── test_whatsapp_webhook.py
├── test_review_idempotency.py
└── fixtures/
    ├── interview_review.json
    ├── salary_review.json
    ├── offer_review.json
    └── ambiguous_review.json
```

Mock:

```text
WhatsApp provider
Gmail provider
LLM
External APIs
```

No real messages should be sent during unit tests.

---

# 40. Test Scenarios

### Scenario 1 — Interview confirmation

```text
Review created
        ↓
WhatsApp notification
        ↓
User: "1"
        ↓
CONFIRM
        ↓
Workflow resumes
```

Expected:

```text
Review = COMPLETED
```

---

### Scenario 2 — Ambiguous response

```text
User:
"Okay"
```

Expected:

```text
AMBIGUOUS
     ↓
Ask user to choose an option
```

No action should be taken.

---

### Scenario 3 — Expired review

```text
Review = EXPIRED
User responds
```

Expected:

```text
Do not execute
Ask user to review current state
```

---

### Scenario 4 — Duplicate webhook

```text
Same WhatsApp event received twice
```

Expected:

```text
First → Process
Second → Ignore
```

---

### Scenario 5 — Unauthorized sender

```text
Unknown WhatsApp sender
```

Expected:

```text
Reject
No application information exposed
```

---

# 41. Observability

Track:

```text
reviews_created
reviews_pending
reviews_completed
reviews_expired
whatsapp_notifications_sent
whatsapp_responses_received
invalid_responses
unauthorized_responses
workflow_resumptions
hitl_failures
```

Later these metrics can be exposed through the observability platform introduced in Phase 8.

---

# 42. Configuration

Add:

```env
WHATSAPP_ENABLED=false

WHATSAPP_PROVIDER=business_api

WHATSAPP_WEBHOOK_ENABLED=false

HITL_REVIEW_EXPIRY_HOURS=24

AUTO_EMAIL_REPLY=false

REQUIRE_HUMAN_APPROVAL_FOR_SENSITIVE_ACTIONS=true
```

All secrets remain in `.env`.

Never commit:

```text
WhatsApp access tokens
Provider credentials
Webhook secrets
OAuth tokens
```

---

# 43. Development Mode

Before connecting a real WhatsApp account, support a local notification mode.

Example:

```text
HITL_NOTIFICATION_MODE=console
```

Then:

```text
Review created

-----------------------------
HUMAN REVIEW REQUIRED
-----------------------------

Company: Example Corp
Role: AI Architect

Recruiter requested salary expectations.

Options:
1. Reply manually
2. Use saved preference
3. Ignore

Review ID: review_1001
-----------------------------
```

The developer can then simulate:

```bash
python -m app.hitl.run --review-id review_1001 --decision 1
```

This allows Phase 5 to be developed without WhatsApp credentials.

---

# 44. CLI

Example commands:

```bash
python -m app.hitl.run --review-id review_1001
```

Simulate a user response:

```bash
python -m app.hitl.run \
    --review-id review_1001 \
    --decision CONFIRM
```

List pending reviews:

```bash
python -m app.hitl.run --pending
```

Expire old reviews:

```bash
python -m app.hitl.run --expire
```

---

# 45. Phase 4 → Phase 5 Contract

Phase 4 produces:

```text
review_required
company
role
email_id
application_id
job_id
reason
requested_action
email_thread_url
```

Phase 5 consumes these fields.

Example:

```json
{
  "email_id": "email_8a72f1",
  "application_id": "app_72fa91",
  "company": "Example Corp",
  "role": "AI Architect",
  "requested_action": "CONFIRM_AVAILABILITY",
  "requires_human_review": true
}
```

---

# 46. Phase 5 → Phase 6 Contract

Phase 5 should expose structured review and decision data so that the JSON repository can later be migrated to PostgreSQL.

Example:

```text
Review
Decision
Notification
Workflow Event
Audit Event
```

The business logic must not depend on JSON-specific implementation details.

---

# 47. Future Evolution

Phase 5 establishes the foundation for a broader personal career operations system.

Future channels could include:

```text
WhatsApp
Web UI
Mobile App
Telegram
Email
Voice Assistant
```

The architecture should therefore separate:

```text
Human Review Logic
        ↓
Notification Channel
```

rather than embedding review logic directly inside WhatsApp code.

---

# 48. Architectural Pattern

Phase 5 demonstrates:

### Human-in-the-loop architecture

```text
AI
 ↓
Uncertainty / Sensitive Action
 ↓
Human
 ↓
Authorization
 ↓
Action
```

### Event-driven communication

```text
Webhook
 ↓
Event
 ↓
Workflow
```

### Policy-based authorization

```text
AI Decision
 ↓
Policy
 ↓
Allowed / Blocked
```

### Channel abstraction

```text
HITL Engine
    ↓
Notification Interface
    ↓
WhatsApp / Web / Mobile / etc.
```

### Idempotent event processing

```text
Same event
    ↓
Process once
```

---

# 49. Definition of Done

Phase 5 is complete when the system can:

- Create a human-review request
- Persist the review
- Identify the related application/job/email
- Generate a structured notification
- Send a notification through a provider abstraction
- Receive a user response
- Validate the sender
- Validate the review
- Interpret structured responses
- Handle ambiguous responses
- Handle expired reviews
- Handle stale reviews
- Prevent duplicate processing
- Resume the appropriate workflow
- Record the human decision
- Maintain an audit trail
- Pass automated tests
- Run completely in local simulation mode without WhatsApp

---

# 50. Phase 5 Acceptance Scenario

Given:

```text
Application:
Example Corp
AI Architect

application_id:
app_72fa91
```

Recruiter sends:

```text
Hi Spandana,

We would like to schedule your technical interview
for Tuesday at 3 PM.

Please confirm your availability.
```

Phase 4 produces:

```text
INTERVIEW_CONFIRMATION_REQUIRED
```

Phase 5 creates:

```text
review_1001
```

WhatsApp:

```text
Example Corp
AI Architect

Technical interview:
Tuesday, 3 PM

Recruiter is asking you to confirm.

1 - Confirm
2 - Ask for another time
3 - Decline
```

User:

```text
1
```

System:

```text
WhatsApp Webhook
      ↓
Validate sender
      ↓
Find review_1001
      ↓
Validate review state
      ↓
Decision = CONFIRM
      ↓
Policy validation
      ↓
Generate confirmation
      ↓
Validate response
      ↓
Send permitted reply
      ↓
Update application timeline
      ↓
Mark review COMPLETED
      ↓
Audit event
```

---

# 51. Phase 5 Completion Statement

At the end of Phase 5, the system should be able to answer:

> **"When the AI needs me, can it tell me exactly what happened, give me the relevant context, capture my decision safely, and continue the correct workflow without guessing?"**

Phase 5 establishes the **human control layer** of the Job Hunt & Career Operations Agent.

The next phase, **Phase 6**, will replace the initial JSON-based persistence and lightweight execution model with **PostgreSQL, background workers, queues, retries, and scalable workflow processing**.