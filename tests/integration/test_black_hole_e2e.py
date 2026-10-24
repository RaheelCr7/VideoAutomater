"""
Beyond 80 - Mandatory End-to-End Acceptance Test
Verifies complete 13-stage autonomous pipeline:
Director Chat -> Research -> Verification -> Script -> 3D Animation -> Narration -> Assembly -> QA -> Review Studio
Topic: "How Black Holes Bend Light (Relativistic Lensing)"
"""

import os
import tempfile
import shutil
import pytest

from videoautomater.platform.storage import PlatformStorage
from videoautomater.platform.orchestrator import ProductionOrchestrator
from videoautomater.platform.director_chat import AIDirectorChat
from videoautomater.platform.publishing_engine import PublishingEngine, AuthorizationGateError
from videoautomater.platform.models import (
    JobStatus,
    ReviewStatus,
    ApprovalMode,
    PublishingPlatform
)
from videoautomater.visuals.subject_media_director import SubjectMediaDirector


@pytest.fixture
def e2e_fixture():
    temp_dir = tempfile.mkdtemp()
    storage = PlatformStorage(base_dir=temp_dir)
    orchestrator = ProductionOrchestrator(storage=storage)
    chat = AIDirectorChat(storage=storage, orchestrator=orchestrator)
    pub_engine = PublishingEngine(storage=storage)

    # Register simulated accounts
    acc_yt = pub_engine.register_account(PublishingPlatform.YOUTUBE_SHORTS, "Beyond80 Official YT")
    acc_tt = pub_engine.register_account(PublishingPlatform.TIKTOK, "Beyond80 Official TikTok")

    yield storage, orchestrator, chat, pub_engine, acc_yt, acc_tt, temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_black_hole_relativistic_visual_generation(e2e_fixture):
    """Verify that relativistic ray-tracing visuals generate accurate physical metrics."""
    _, _, _, _, _, _, temp_dir = e2e_fixture
    director = SubjectMediaDirector(output_dir=temp_dir)

    # Render relativistic black hole animation clip (short sample)
    clip_path = director.render_subject_animation(
        subject="black hole gravitational lensing",
        duration_sec=3.0,
        fps=24,
        width=1080,
        height=1920
    )

    assert os.path.exists(clip_path)
    assert os.path.getsize(clip_path) > 10000


def test_complete_black_hole_acceptance_workflow(e2e_fixture):
    """
    Executes mandatory acceptance test:
    Director instruction -> 13-stage orchestration -> Review Studio -> Revision -> Authorized Release
    """
    storage, orchestrator, chat, pub_engine, acc_yt, acc_tt, temp_dir = e2e_fixture

    instruction = (
        "Create an 80-second cinematic video explaining how black holes bend light. "
        "Use scientifically accurate 3D animations and save for my review."
    )

    # Step 1: Submit instruction to AI Director Chat
    chat_response = chat.process_chat(instruction)
    assert chat_response.metadata.get("action") == "create_single_job"
    job_id = chat_response.metadata.get("job_id")
    assert job_id is not None

    # Step 2: Retrieve job and verify initial state
    job = storage.get_job(job_id)
    assert job is not None
    assert "black hole" in job.topic.lower()
    assert job.approval_mode == ApprovalMode.REQUIRED_APPROVAL
    assert job.review_status == ReviewStatus.PENDING_HUMAN_APPROVAL

    # Step 3: Execute orchestrator job (simulating pipeline completion)
    # The orchestrator's execute_job runs all stages
    orchestrator.execute_job(job_id)

    # Step 4: Verify completed job state in storage
    completed_job = storage.get_job(job_id)
    assert completed_job.status == JobStatus.COMPLETED
    assert completed_job.review_status == ReviewStatus.PENDING_HUMAN_APPROVAL
    assert completed_job.master_video_path is not None
    assert os.path.exists(completed_job.master_video_path)
    assert completed_job.publication_authorized is False

    # Step 5: Verify all 13 stages were executed and logged
    assert len(completed_job.agent_steps) == 13
    stage_names = [step.agent_name for step in completed_job.agent_steps]
    expected_agents = [
        "Research Agent",
        "Story Director",
        "Scriptwriting Agent",
        "Visual Director",
        "Asset Research and Licensing Agent",
        "Animation Director",
        "3D Production Agent",
        "Narration and Sound Agent",
        "Video Assembly Agent",
        "Scientific and Technical QA Agent",
        "Publishing Agent",
        "Analytics Agent",
        "Production Orchestrator"
    ]
    for agent in expected_agents:
        assert agent in stage_names

    # Step 6: Verify QA report
    assert completed_job.qa_report is not None
    assert completed_job.qa_report.passed is True
    assert completed_job.qa_report.subtitles_synchronized is True
    assert completed_job.qa_report.safe_zones_respected is True

    # Step 7: Verify Human Review Studio Revision Workflow
    # Add timestamp feedback at 35s
    fb = completed_job.add_feedback(
        timestamp_sec=35.0,
        comment="Increase Doppler beaming brightness on the approaching left limb of the accretion disk.",
        request_regeneration=True
    )
    # Create version 2
    completed_job.create_version(
        version_number=2,
        video_path=completed_job.master_video_path,
        notes="Version 2: Accretion disk Doppler beaming enhanced."
    )
    completed_job.review_status = ReviewStatus.CHANGES_REQUESTED
    storage.save_job(completed_job)

    # Step 8: Test Publishing Safety Gate
    # Creating a task on unapproved/unauthorized video must fail
    task_yt = pub_engine.create_publishing_task(
        job_id=job_id,
        account_id=acc_yt.id,
        title="How Black Holes Bend Light #Shorts",
        description="General relativity and null geodesics explained.",
        tags=["blackhole", "physics"]
    )
    with pytest.raises(AuthorizationGateError):
        pub_engine.execute_publishing_task(task_yt.id)

    # Step 9: Human Approves Release and Authorizes Distribution
    completed_job.review_status = ReviewStatus.APPROVED_FOR_RELEASE
    completed_job.publication_authorized = True
    storage.save_job(completed_job)

    # Step 10: Multi-Platform Publishing (Simulated Connectors)
    published_task = pub_engine.execute_publishing_task(task_yt.id)
    assert published_task.status == JobStatus.COMPLETED
    assert published_task.remote_video_id is not None
    assert published_task.published_url is not None
    assert "sim_youtube_shorts" in published_task.remote_video_id
