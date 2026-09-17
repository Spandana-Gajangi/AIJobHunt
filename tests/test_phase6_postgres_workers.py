from app.models.workflow import AuditEvent, RunState, WorkflowState
from app.services.queue import ApplicationWorker, InMemoryQueue, JobCollectionWorker


def test_workflow_state_tracks_state_progression() -> None:
    state = WorkflowState(job_id="job-42", status="QUEUED", current_step="DISCOVERY")

    state.advance("MATCHING")
    state.mark_started()
    state.mark_completed()

    assert state.current_step == "MATCHING"
    assert state.status == "COMPLETED"
    assert len(state.history) >= 3


def test_in_memory_queue_deduplicates_pending_jobs() -> None:
    queue = InMemoryQueue()

    assert queue.enqueue({"job_id": "job-1", "kind": "job_collection"}) is True
    assert queue.enqueue({"job_id": "job-1", "kind": "job_collection"}) is False

    job = queue.dequeue()
    assert job["job_id"] == "job-1"
    assert queue.pending_count() == 0


def test_application_worker_records_audit_event() -> None:
    worker = ApplicationWorker()
    state = RunState(name="application", status="QUEUED")

    event = worker.process({"job_id": "job-99"}, state)

    assert event.kind == "application"
    assert event.status == "SUCCESS"
    assert isinstance(event, AuditEvent)
    assert state.status == "COMPLETED"
    assert state.current_step == "APPLICATION"


def test_job_collection_worker_uses_queue_contract() -> None:
    queue = InMemoryQueue()
    queue.enqueue({"job_id": "portal-7", "kind": "job_collection"})
    worker = JobCollectionWorker(queue)

    result = worker.run_once()

    assert result == "portal-7"
    assert queue.pending_count() == 0
