"""
Tests for Autonomous Production Scheduler.
"""

import tempfile
import shutil
import time
from datetime import datetime, timedelta
import zoneinfo
import pytest

from videoautomater.platform.storage import PlatformStorage
from videoautomater.platform.orchestrator import ProductionOrchestrator
from videoautomater.platform.scheduler import ProductionScheduler
from videoautomater.platform.models import ApprovalMode, JobStatus


@pytest.fixture
def scheduler_fixture():
    temp_dir = tempfile.mkdtemp()
    storage = PlatformStorage(base_dir=temp_dir)
    orchestrator = ProductionOrchestrator(storage=storage)
    scheduler = ProductionScheduler(storage=storage, orchestrator=orchestrator, timezone="Asia/Karachi")
    yield storage, orchestrator, scheduler
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_scheduler_creation_and_timezone(scheduler_fixture):
    storage, orchestrator, scheduler = scheduler_fixture

    sched = scheduler.create_schedule(
        name="Daily Space Exploration",
        videos_per_day=2,
        preferred_topics=["Black Holes", "Neutron Stars"],
        approval_mode=ApprovalMode.REQUIRED_APPROVAL
    )

    assert sched.id is not None
    assert sched.videos_per_day == 2
    assert len(sched.preferred_topics) == 2

    # Check persistence
    loaded = storage.get_schedule(sched.id)
    assert loaded is not None
    assert loaded.name == "Daily Space Exploration"


def test_scheduler_triggers_due_job(scheduler_fixture):
    storage, orchestrator, scheduler = scheduler_fixture

    # Create schedule due in the past
    sched = scheduler.create_schedule(
        name="Immediate Test Trigger",
        videos_per_day=1,
        preferred_topics=["Black Holes and Light Bending"]
    )
    sched.next_run = datetime.now(scheduler.tz) - timedelta(minutes=1)
    storage.save_schedule(sched)

    # Run check
    scheduler._check_and_trigger_schedules()

    # Verify job was submitted to orchestrator
    jobs = storage.list_jobs()
    assert len(jobs) == 1
    assert "Black Holes and Light Bending" in jobs[0].topic

    # Verify next run was advanced
    reloaded_sched = storage.get_schedule(sched.id)
    assert reloaded_sched.total_runs == 1
    assert reloaded_sched.next_run > datetime.now(scheduler.tz)
