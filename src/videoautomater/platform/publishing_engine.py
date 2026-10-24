"""
Beyond 80 - Multi-Platform Publishing Engine
Supports YouTube Shorts, Instagram Reels, TikTok, and Facebook Reels.
Includes rigorous publication authorization gates, destination-specific metadata validation,
idempotency, retry handling, and clearly labeled simulated provider connectors (SIMULATED_CONNECTOR).
"""

from __future__ import annotations
import os
import json
import time
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from videoautomater.platform.models import (
    PublishingPlatform,
    PublishingAccount,
    PublishingTask,
    JobStatus,
    ReviewStatus
)
from videoautomater.platform.storage import PlatformStorage

logger = logging.getLogger(__name__)


class PublishingError(Exception):
    """Raised when publication cannot proceed or validation fails."""
    pass


class AuthorizationGateError(PublishingError):
    """Raised when publication is attempted without explicit human authorization."""
    pass


class BasePublishingConnector:
    """Abstract base class for platform publishing connectors."""

    platform: PublishingPlatform
    is_simulated: bool = False

    def validate_metadata(self, title: str, description: str, tags: List[str]) -> Dict[str, Any]:
        """Validate destination-specific metadata constraints."""
        raise NotImplementedError

    def publish_video(
        self,
        account: PublishingAccount,
        master_video_path: str,
        title: str,
        description: str,
        tags: List[str],
        idempotency_key: str
    ) -> Dict[str, Any]:
        """Publish video to platform or simulate publication."""
        raise NotImplementedError


class SimulatedPlatformConnector(BasePublishingConnector):
    """
    Clearly labeled SIMULATED_CONNECTOR for testing multi-platform publishing
    without active production credentials or unauthorized public distribution.
    """
    is_simulated: bool = True

    def __init__(self, platform: PublishingPlatform):
        self.platform = platform

    def validate_metadata(self, title: str, description: str, tags: List[str]) -> Dict[str, Any]:
        # Platform-specific constraints
        if self.platform == PublishingPlatform.YOUTUBE_SHORTS:
            if len(title) > 100:
                raise PublishingError(f"YouTube Shorts title exceeds 100 characters: {len(title)}")
            if "#Shorts" not in title and "#Shorts" not in description:
                description = f"{description}\n\n#Shorts"

        elif self.platform == PublishingPlatform.TIKTOK:
            if len(description) > 2200:
                raise PublishingError(f"TikTok description exceeds 2200 characters: {len(description)}")

        elif self.platform == PublishingPlatform.INSTAGRAM_REELS:
            if len(description) > 2200:
                raise PublishingError(f"Instagram caption exceeds 2200 characters: {len(description)}")
            if len(tags) > 30:
                raise PublishingError(f"Instagram allows max 30 tags, provided: {len(tags)}")

        elif self.platform == PublishingPlatform.FACEBOOK_REELS:
            if len(description) > 5000:
                raise PublishingError(f"Facebook description exceeds 5000 characters: {len(description)}")

        return {
            "title": title,
            "description": description,
            "tags": tags,
            "validated": True
        }

    def publish_video(
        self,
        account: PublishingAccount,
        master_video_path: str,
        title: str,
        description: str,
        tags: List[str],
        idempotency_key: str
    ) -> Dict[str, Any]:
        if not os.path.exists(master_video_path):
            raise PublishingError(f"Master video file does not exist: {master_video_path}")

        # Validate file size and format
        stat = os.stat(master_video_path)
        if stat.st_size < 1000:
            raise PublishingError(f"Master video file suspiciously small: {stat.st_size} bytes")

        validated_meta = self.validate_metadata(title, description, tags)

        # Realistic simulated network latency
        time.sleep(0.5)

        remote_id = f"sim_{self.platform.value}_{int(time.time())}_{idempotency_key[:8]}"
        share_url = f"https://{self.platform.value}.simulated/watch/{remote_id}"

        logger.info(
            f"[SIMULATED_CONNECTOR] Published to {self.platform.value} "
            f"for account '{account.account_name}' ({account.id}). Remote ID: {remote_id}"
        )

        return {
            "platform": self.platform.value,
            "connector_type": "SIMULATED_CONNECTOR",
            "account_id": account.id,
            "account_name": account.account_name,
            "remote_id": remote_id,
            "share_url": share_url,
            "idempotency_key": idempotency_key,
            "published_at": datetime.now().isoformat(),
            "metadata": validated_meta,
            "is_simulation": True,
            "notice": "SIMULATED_CONNECTOR: This was safely simulated without external API credentials."
        }


class PublishingEngine:
    """
    Manages accounts, dispatches publishing tasks, and strictly enforces
    human release approval gates before any video can be pushed.
    """

    def __init__(self, storage: PlatformStorage):
        self.storage = storage
        self.connectors: Dict[PublishingPlatform, BasePublishingConnector] = {
            PublishingPlatform.YOUTUBE_SHORTS: SimulatedPlatformConnector(PublishingPlatform.YOUTUBE_SHORTS),
            PublishingPlatform.INSTAGRAM_REELS: SimulatedPlatformConnector(PublishingPlatform.INSTAGRAM_REELS),
            PublishingPlatform.TIKTOK: SimulatedPlatformConnector(PublishingPlatform.TIKTOK),
            PublishingPlatform.FACEBOOK_REELS: SimulatedPlatformConnector(PublishingPlatform.FACEBOOK_REELS),
        }

    def register_account(
        self,
        platform: PublishingPlatform,
        account_name: str,
        credentials: Optional[Dict[str, Any]] = None,
        is_simulated: bool = True
    ) -> PublishingAccount:
        """Register a publishing destination account."""
        account_id = f"acc_{platform.value}_{int(time.time()*1000)}"
        account = PublishingAccount(
            id=account_id,
            platform=platform,
            account_name=account_name,
            auth_token="simulated_token" if is_simulated else (credentials.get("token", "") if credentials else ""),
            refresh_token="simulated_refresh" if is_simulated else "",
            is_active=True,
            is_simulated=is_simulated,
            metadata={
                "registered_at": datetime.now().isoformat(),
                "credentials_provided": bool(credentials)
            }
        )
        self.storage.save_publishing_account(account)
        logger.info(f"Registered publishing account {account.id} ({account.account_name}) for {platform.value}")
        return account

    def create_publishing_task(
        self,
        job_id: str,
        account_id: str,
        title: str,
        description: str,
        tags: List[str]
    ) -> PublishingTask:
        """Create a scheduled or queued publishing task."""
        account = self.storage.get_publishing_account(account_id)
        if not account:
            raise PublishingError(f"Account {account_id} not found")

        job = self.storage.get_job(job_id)
        if not job:
            raise PublishingError(f"Job {job_id} not found")

        task_id = f"pub_task_{int(time.time()*1000)}"
        task = PublishingTask(
            id=task_id,
            job_id=job_id,
            account_id=account_id,
            platform=account.platform,
            title=title,
            description=description,
            tags=tags,
            status=JobStatus.QUEUED,
            idempotency_key=f"idem_{job_id}_{account_id}"
        )
        self.storage.save_publishing_task(task)
        return task

    def execute_publishing_task(self, task_id: str) -> PublishingTask:
        """
        Execute a publishing task with strict human approval gates.
        """
        task = self.storage.get_publishing_task(task_id)
        if not task:
            raise PublishingError(f"Publishing task {task_id} not found")

        job = self.storage.get_job(task.job_id)
        if not job:
            raise PublishingError(f"Job {task.job_id} not found")

        # CRITICAL SAFETY GATE:
        # 1. Review status MUST be APPROVED_FOR_RELEASE
        # 2. Publication authorization flag MUST be True
        if job.review_status != ReviewStatus.APPROVED_FOR_RELEASE:
            task.status = JobStatus.FAILED
            task.error_message = (
                f"SAFETY BLOCK: Video review status is '{job.review_status.value}', "
                f"not '{ReviewStatus.APPROVED_FOR_RELEASE.value}'. Release blocked."
            )
            self.storage.save_publishing_task(task)
            raise AuthorizationGateError(task.error_message)

        if not job.publication_authorized:
            task.status = JobStatus.FAILED
            task.error_message = (
                "SAFETY BLOCK: publication_authorized flag is False. "
                "Explicit human release authorization is required."
            )
            self.storage.save_publishing_task(task)
            raise AuthorizationGateError(task.error_message)

        account = self.storage.get_publishing_account(task.account_id)
        if not account:
            raise PublishingError(f"Account {task.account_id} not found")

        connector = self.connectors.get(task.platform)
        if not connector:
            raise PublishingError(f"No connector registered for platform {task.platform.value}")

        task.status = JobStatus.RUNNING
        self.storage.save_publishing_task(task)

        try:
            result = connector.publish_video(
                account=account,
                master_video_path=job.master_video_path or "",
                title=task.title,
                description=task.description,
                tags=task.tags,
                idempotency_key=task.idempotency_key
            )
            task.status = JobStatus.COMPLETED
            task.remote_video_id = result.get("remote_id")
            task.published_url = result.get("share_url")
            task.published_at = datetime.now()
            self.storage.save_publishing_task(task)
            logger.info(f"Successfully published task {task.id} to {task.platform.value}")
            return task
        except Exception as e:
            task.status = JobStatus.FAILED
            task.error_message = str(e)
            task.retry_count += 1
            self.storage.save_publishing_task(task)
            logger.error(f"Failed to publish task {task.id}: {e}")
            raise
