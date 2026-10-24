"""
Beyond 80 - Autonomous Production Scheduler
Supports durable recurring schedules (cron / interval / daily quotas),
persists state across restarts, handles queue concurrency, retry policies,
and executes autonomous topic discovery or queued user topics.
Timezone default: Asia/Karachi (configurable).
"""

from __future__ import annotations
import os
import time
import logging
import threading
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import zoneinfo

from videoautomater.platform.models import (
    ProductionSchedule,
    ProductionJob,
    JobStatus,
    ApprovalMode
)
from videoautomater.platform.storage import PlatformStorage
from videoautomater.platform.orchestrator import ProductionOrchestrator

logger = logging.getLogger(__name__)


class ProductionScheduler:
    """
    Durable production scheduler that operates as a background worker thread.
    Survives restarts by persisting schedule configurations and execution logs.
    """

    def __init__(
        self,
        storage: PlatformStorage,
        orchestrator: ProductionOrchestrator,
        timezone: str = "Asia/Karachi"
    ):
        self.storage = storage
        self.orchestrator = orchestrator
        self.default_tz_name = timezone
        try:
            self.tz = zoneinfo.ZoneInfo(timezone)
        except Exception:
            self.tz = zoneinfo.ZoneInfo("UTC")

        self.running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

    def set_timezone(self, tz_name: str) -> None:
        try:
            self.tz = zoneinfo.ZoneInfo(tz_name)
            self.default_tz_name = tz_name
            settings = self.storage.get_settings()
            settings.default_timezone = tz_name
            self.storage.save_settings(settings)
            logger.info(f"Scheduler timezone updated to {tz_name}")
        except Exception as e:
            logger.error(f"Invalid timezone {tz_name}: {e}")
            raise ValueError(f"Unknown timezone: {tz_name}")

    def create_schedule(
        self,
        name: str,
        videos_per_day: int = 1,
        preferred_topics: Optional[List[str]] = None,
        approval_mode: ApprovalMode = ApprovalMode.REQUIRED_APPROVAL,
        active: bool = True
    ) -> ProductionSchedule:
        """Create a durable production schedule."""
        schedule_id = f"sched_{int(time.time()*1000)}"
        schedule = ProductionSchedule(
            id=schedule_id,
            name=name,
            active=active,
            frequency_days=1,
            videos_per_day=videos_per_day,
            preferred_topics=preferred_topics or [],
            approval_mode=approval_mode,
            next_run=datetime.now(self.tz)
        )
        self.storage.save_schedule(schedule)
        logger.info(f"Created production schedule '{name}' ({schedule_id})")
        return schedule

    def start(self) -> None:
        """Start the background scheduler thread."""
        with self._lock:
            if self.running:
                return
            self.running = True
            self._thread = threading.Thread(target=self._scheduler_loop, daemon=True)
            self._thread.start()
            logger.info("Autonomous Production Scheduler started.")

    def stop(self) -> None:
        """Stop the background scheduler."""
        with self._lock:
            self.running = False
        if self._thread:
            self._thread.join(timeout=2.0)
            logger.info("Autonomous Production Scheduler stopped.")

    def _scheduler_loop(self) -> None:
        """Main periodic check loop."""
        while self.running:
            try:
                self._check_and_trigger_schedules()
            except Exception as e:
                logger.error(f"Error in scheduler check loop: {e}", exc_info=True)
            time.sleep(5)  # Check every 5 seconds

    def _check_and_trigger_schedules(self) -> None:
        """Evaluate schedules and trigger jobs whose time has arrived."""
        now = datetime.now(self.tz)
        schedules = self.storage.list_schedules()

        for schedule in schedules:
            if not schedule.active:
                continue

            if schedule.next_run and now >= schedule.next_run:
                # Trigger production
                logger.info(f"Schedule '{schedule.name}' triggered at {now.isoformat()}")

                topic = None
                if schedule.preferred_topics:
                    # Pick topic
                    idx = schedule.total_runs % len(schedule.preferred_topics)
                    topic = schedule.preferred_topics[idx]

                job = self.orchestrator.submit_job(
                    topic=topic,
                    approval_mode=schedule.approval_mode,
                    director_instructions=f"Autonomous scheduled production run for '{schedule.name}'"
                )

                schedule.total_runs += 1
                schedule.last_run = now

                # Calculate next run (divide 24h by videos_per_day)
                hours_interval = 24.0 / max(1, schedule.videos_per_day)
                schedule.next_run = now + timedelta(hours=hours_interval)
                self.storage.save_schedule(schedule)

                logger.info(f"Scheduled job {job.id} triggered. Next run: {schedule.next_run.isoformat()}")
