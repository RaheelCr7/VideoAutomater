"""
Tests for AI Director Chat intent parsing and command execution.
"""

import tempfile
import shutil
import pytest

from videoautomater.platform.storage import PlatformStorage
from videoautomater.platform.orchestrator import ProductionOrchestrator
from videoautomater.platform.director_chat import AIDirectorChat
from videoautomater.platform.models import JobStatus, ReviewStatus, ProductionJob


@pytest.fixture
def chat_fixture():
    temp_dir = tempfile.mkdtemp()
    storage = PlatformStorage(base_dir=temp_dir)
    orchestrator = ProductionOrchestrator(storage=storage)
    chat = AIDirectorChat(storage=storage, orchestrator=orchestrator)
    yield storage, orchestrator, chat
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_director_creates_single_video_job(chat_fixture):
    storage, orchestrator, chat = chat_fixture
    prompt = "Create an 80-second cinematic video explaining how black holes bend light. Use scientifically accurate 3D animations and save for my review."

    response = chat.process_chat(prompt)
    assert response.metadata.get("action") == "create_single_job"
    assert "black holes bend light" in response.content.lower()

    # Verify job created in storage
    jobs = storage.list_jobs()
    assert len(jobs) == 1
    assert "black hole" in jobs[0].topic.lower()
    assert jobs[0].target_duration_sec == 80.0
    assert jobs[0].review_status == ReviewStatus.PENDING_HUMAN_APPROVAL


def test_director_handles_batch_scheduling(chat_fixture):
    storage, orchestrator, chat = chat_fixture
    prompt = "Create three space videos tomorrow."

    response = chat.process_chat(prompt)
    assert response.metadata.get("action") == "batch_schedule"

    # Verify schedule created
    schedules = storage.list_schedules()
    assert len(schedules) == 1
    assert schedules[0].videos_per_day == 3


def test_director_handles_timestamp_regeneration(chat_fixture):
    storage, orchestrator, chat = chat_fixture
    # Create active job
    job = ProductionJob(
        id="job_active_01",
        topic="Relativistic Optics",
        status=JobStatus.COMPLETED,
        review_status=ReviewStatus.PENDING_HUMAN_APPROVAL,
        master_video_path="/path/to/test.mp4"
    )
    storage.save_job(job)

    prompt = "Regenerate the animation at 35 seconds because it looks unrealistic."
    response = chat.process_chat(prompt)

    assert response.metadata.get("action") == "regenerate_scene"
    assert response.metadata.get("timestamp_sec") == 35.0

    # Verify feedback was attached
    reloaded = storage.get_job("job_active_01")
    assert len(reloaded.feedback) >= 1
    assert reloaded.feedback[-1].timestamp_sec == 35.0


def test_director_handles_style_preference_change(chat_fixture):
    storage, orchestrator, chat = chat_fixture
    prompt = "Make the next videos more dramatic but keep scientific accuracy."

    response = chat.process_chat(prompt)
    assert response.metadata.get("action") == "update_style_preference"

    # Verify style directive saved in settings
    settings = storage.get_settings()
    assert "dramatic" in settings.global_style_directive.lower()
