"""
Tests for Multi-Platform Publishing Engine and Safety Authorization Gates.
"""

import os
import tempfile
import shutil
import pytest

from videoautomater.platform.models import (
    ProductionJob,
    JobStatus,
    ReviewStatus,
    PublishingPlatform
)
from videoautomater.platform.storage import PlatformStorage
from videoautomater.platform.publishing_engine import (
    PublishingEngine,
    AuthorizationGateError,
    PublishingError
)


@pytest.fixture
def pub_fixture():
    temp_dir = tempfile.mkdtemp()
    storage = PlatformStorage(base_dir=temp_dir)
    engine = PublishingEngine(storage=storage)

    # Register destination accounts
    acc_yt = engine.register_account(PublishingPlatform.YOUTUBE_SHORTS, "Beyond80 YouTube")
    acc_ig = engine.register_account(PublishingPlatform.INSTAGRAM_REELS, "Beyond80 Instagram")

    # Create dummy master video file
    video_path = os.path.join(temp_dir, "master_test.mp4")
    with open(video_path, "wb") as f:
        f.write(b"0" * 2048)  # dummy video file

    yield storage, engine, acc_yt, acc_ig, video_path
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_publishing_blocked_when_unapproved(pub_fixture):
    storage, engine, acc_yt, acc_ig, video_path = pub_fixture

    # Job is still PENDING_HUMAN_APPROVAL
    job = ProductionJob(
        id="job_pending_001",
        topic="Relativistic Light Bending",
        status=JobStatus.COMPLETED,
        review_status=ReviewStatus.PENDING_HUMAN_APPROVAL,
        publication_authorized=False,
        master_video_path=video_path
    )
    storage.save_job(job)

    task = engine.create_publishing_task(
        job_id="job_pending_001",
        account_id=acc_yt.id,
        title="Black Hole Lensing",
        description="Gravitational light bending around Schwarzschild metric.",
        tags=["science", "physics"]
    )

    with pytest.raises(AuthorizationGateError) as exc_info:
        engine.execute_publishing_task(task.id)

    assert "SAFETY BLOCK" in str(exc_info.value)
    reloaded_task = storage.get_publishing_task(task.id)
    assert reloaded_task.status == JobStatus.FAILED


def test_publishing_blocked_when_approved_but_not_authorized(pub_fixture):
    storage, engine, acc_yt, acc_ig, video_path = pub_fixture

    # Job is APPROVED_FOR_RELEASE but publication_authorized is still False
    job = ProductionJob(
        id="job_approved_no_auth",
        topic="Relativistic Light Bending",
        status=JobStatus.COMPLETED,
        review_status=ReviewStatus.APPROVED_FOR_RELEASE,
        publication_authorized=False,  # Still not authorized for release
        master_video_path=video_path
    )
    storage.save_job(job)

    task = engine.create_publishing_task(
        job_id="job_approved_no_auth",
        account_id=acc_yt.id,
        title="Black Hole Lensing",
        description="Gravitational light bending around Schwarzschild metric.",
        tags=["science", "physics"]
    )

    with pytest.raises(AuthorizationGateError) as exc_info:
        engine.execute_publishing_task(task.id)

    assert "SAFETY BLOCK: publication_authorized flag is False" in str(exc_info.value)


def test_simulated_publishing_succeeds_when_fully_authorized(pub_fixture):
    storage, engine, acc_yt, acc_ig, video_path = pub_fixture

    # Job has full human creative and publication authorization
    job = ProductionJob(
        id="job_fully_authorized",
        topic="Relativistic Light Bending",
        status=JobStatus.COMPLETED,
        review_status=ReviewStatus.APPROVED_FOR_RELEASE,
        publication_authorized=True,
        master_video_path=video_path
    )
    storage.save_job(job)

    task = engine.create_publishing_task(
        job_id="job_fully_authorized",
        account_id=acc_yt.id,
        title="Black Hole Lensing Explained in 80 Seconds",
        description="General relativity and null geodesics.",
        tags=["blackhole", "physics"]
    )

    completed = engine.execute_publishing_task(task.id)
    assert completed.status == JobStatus.COMPLETED
    assert completed.remote_video_id is not None
    assert "sim_youtube_shorts" in completed.remote_video_id
    assert completed.published_url is not None
