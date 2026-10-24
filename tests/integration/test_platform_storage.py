"""
Integration tests for PlatformStorage, Models, and Persistence.
"""

import os
import shutil
import tempfile
import pytest
from datetime import datetime

from videoautomater.platform.models import (
    ProductionJob,
    JobStatus,
    ApprovalMode,
    ReviewStatus,
    AgentConfig,
    ProductionSchedule,
    PublishingAccount,
    PublishingPlatform,
    SystemSettings
)
from videoautomater.platform.storage import PlatformStorage


@pytest.fixture
def temp_storage():
    temp_dir = tempfile.mkdtemp()
    storage = PlatformStorage(base_dir=temp_dir)
    yield storage
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_job_persistence_and_versioning(temp_storage):
    job = ProductionJob(
        id="job_test_001",
        topic="Relativistic Optics",
        target_duration_sec=80.0,
        status=JobStatus.RUNNING,
        approval_mode=ApprovalMode.REQUIRED_APPROVAL,
        review_status=ReviewStatus.PENDING_HUMAN_APPROVAL
    )
    temp_storage.save_job(job)

    # Reload from storage
    loaded = temp_storage.get_job("job_test_001")
    assert loaded is not None
    assert loaded.topic == "Relativistic Optics"
    assert loaded.status == JobStatus.RUNNING
    assert loaded.review_status == ReviewStatus.PENDING_HUMAN_APPROVAL
    assert loaded.publication_authorized is False

    # Add version
    loaded.create_version(1, "/path/to/v1.mp4", "Initial render")
    temp_storage.save_job(loaded)

    reloaded = temp_storage.get_job("job_test_001")
    assert len(reloaded.versions) == 1
    assert reloaded.versions[0].version_number == 1

    # Add feedback
    reloaded.add_feedback(timestamp_sec=35.2, comment="Accretion disk should be more asymmetric", scene_index=2)
    temp_storage.save_job(reloaded)

    reloaded2 = temp_storage.get_job("job_test_001")
    assert len(reloaded2.feedback) == 1
    assert reloaded2.feedback[0].timestamp_sec == 35.2


def test_agent_configuration_persistence(temp_storage):
    agents = temp_storage.list_agents()
    assert len(agents) == 13

    # Update visual director
    vis_agent = temp_storage.get_agent("visual_director")
    assert vis_agent is not None
    vis_agent.temperature = 0.45
    temp_storage.save_agent(vis_agent)

    reloaded = temp_storage.get_agent("visual_director")
    assert reloaded.temperature == 0.45


def test_settings_persistence(temp_storage):
    settings = temp_storage.get_settings()
    assert settings.default_timezone == "Asia/Karachi"
    assert settings.default_approval_mode == ApprovalMode.REQUIRED_APPROVAL

    settings.daily_production_quota = 10
    temp_storage.save_settings(settings)

    reloaded = temp_storage.get_settings()
    assert reloaded.daily_production_quota == 10
