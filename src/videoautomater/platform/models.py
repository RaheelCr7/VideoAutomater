"""Platform domain models for Agent Control Center, Orchestration, Review, and Publishing."""

from __future__ import annotations
from datetime import datetime, timezone
from enum import Enum
from typing import Any, List, Dict, Optional
from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    PENDING = "PENDING"
    QUEUED = "QUEUED"
    RESEARCHING = "RESEARCHING"
    WRITING = "WRITING"
    DIRECTING_VISUALS = "DIRECTING_VISUALS"
    ANIMATING = "ANIMATING"
    SYNTHESIZING_AUDIO = "SYNTHESIZING_AUDIO"
    ASSEMBLING = "ASSEMBLING"
    QA_AUDITING = "QA_AUDITING"
    READY_FOR_REVIEW = "READY_FOR_REVIEW"
    RUNNING = "RUNNING"
    APPROVED = "APPROVED"
    PUBLISHING = "PUBLISHING"
    PUBLISHED = "PUBLISHED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ApprovalMode(str, Enum):
    REQUIRED_APPROVAL = "REQUIRED_APPROVAL"  # Default: human review strictly required before publish
    OPTIONAL_REVIEW = "OPTIONAL_REVIEW"
    AUTO = "AUTO"


class ReviewStatus(str, Enum):
    PENDING_HUMAN_APPROVAL = "PENDING_HUMAN_APPROVAL"
    APPROVED_FOR_RELEASE = "APPROVED_FOR_RELEASE"
    CHANGES_REQUESTED = "CHANGES_REQUESTED"
    REVISION_REQUESTED = "CHANGES_REQUESTED"
    REJECTED = "REJECTED"


class TimestampFeedback(BaseModel):
    timestamp_sec: float = 0.0
    scene_index: Optional[int] = None
    comment: str = ""
    request_regeneration: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Backward compatibility properties
    @property
    def timestamp_seconds(self) -> float:
        return self.timestamp_sec

    @property
    def feedback_text(self) -> str:
        return self.comment


class VersionReviewRecord(BaseModel):
    version_number: int = 1
    video_path: str = ""
    notes: str = ""
    status: ReviewStatus = ReviewStatus.PENDING_HUMAN_APPROVAL
    feedback_items: List[TimestampFeedback] = Field(default_factory=list)
    reviewed_at: Optional[datetime] = None
    reviewer_notes: str = ""
    is_master_approved: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentStepLog(BaseModel):
    agent_name: str
    status: str = "completed"
    summary: str = ""
    duration_sec: float = 0.0
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class QAReport(BaseModel):
    passed: bool = True
    subtitles_synchronized: bool = True
    safe_zones_respected: bool = True
    rights_cleared: bool = True
    vocabulary_coverage: float = 1.0
    provenance_verified: bool = True
    claims_verified: List[str] = Field(default_factory=list)
    details: Dict[str, Any] = Field(default_factory=dict)


class ProductionJob(BaseModel):
    id: str = Field(alias="id", default="")
    job_id: str = ""
    topic: str = ""
    prompt: str = ""
    target_duration_sec: float = 80.0
    actual_duration_sec: float = 80.0
    status: JobStatus = JobStatus.PENDING
    approval_mode: ApprovalMode = ApprovalMode.REQUIRED_APPROVAL
    review_status: ReviewStatus = ReviewStatus.PENDING_HUMAN_APPROVAL
    current_stage: str = "QUEUED"
    stages_completed: List[str] = Field(default_factory=list)
    agent_steps: List[AgentStepLog] = Field(default_factory=list)
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Output artifact references
    output_dir: str = ""
    master_video_path: Optional[str] = None
    thumbnail_path: Optional[str] = None
    script_data: Optional[Dict[str, Any]] = None
    script_summary: str = ""
    narrated_word_count: int = 0
    measured_duration: float = 0.0

    # Versioning & Review
    current_version: int = 1
    versions: List[VersionReviewRecord] = Field(default_factory=list)
    feedback: List[TimestampFeedback] = Field(default_factory=list)
    publication_authorized: bool = False
    reviewer_notes: Optional[str] = None

    # Traceable metadata
    qa_report: Optional[QAReport] = None
    provenance_summary: Dict[str, Any] = Field(default_factory=dict)
    director_instructions: Optional[str] = None

    def model_post_init(self, __context: Any) -> None:
        if not self.id and self.job_id:
            self.id = self.job_id
        elif not self.job_id and self.id:
            self.job_id = self.id

    def add_feedback(
        self,
        timestamp_sec: float,
        comment: str,
        scene_index: Optional[int] = None,
        request_regeneration: bool = False
    ) -> TimestampFeedback:
        fb = TimestampFeedback(
            timestamp_sec=timestamp_sec,
            scene_index=scene_index,
            comment=comment,
            request_regeneration=request_regeneration
        )
        self.feedback.append(fb)
        return fb

    def create_version(self, version_number: int, video_path: str, notes: str = "") -> VersionReviewRecord:
        v = VersionReviewRecord(
            version_number=version_number,
            video_path=video_path,
            notes=notes,
            status=ReviewStatus.PENDING_HUMAN_APPROVAL
        )
        self.versions.append(v)
        self.current_version = version_number
        return v


class AgentStatus(str, Enum):
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"


class AgentConfig(BaseModel):
    id: str = ""
    agent_id: str = ""
    name: str = ""
    role_description: str = ""
    system_prompt: str = ""
    system_instructions: str = ""
    model: str = "rule_based_deterministic"
    temperature: float = 0.2
    is_active: bool = True
    status: AgentStatus = AgentStatus.IDLE
    current_job_id: Optional[str] = None
    last_action: str = "Initialized"
    last_heartbeat: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    operational_rules: List[str] = Field(default_factory=list)

    def model_post_init(self, __context: Any) -> None:
        if not self.id and self.agent_id:
            self.id = self.agent_id
        elif not self.agent_id and self.id:
            self.agent_id = self.id
        if not self.system_prompt and self.system_instructions:
            self.system_prompt = self.system_instructions
        elif not self.system_instructions and self.system_prompt:
            self.system_instructions = self.system_prompt


class PublishingPlatform(str, Enum):
    YOUTUBE_SHORTS = "youtube_shorts"
    INSTAGRAM_REELS = "instagram_reels"
    TIKTOK = "tiktok"
    FACEBOOK_REELS = "facebook_reels"


class PublishingAccount(BaseModel):
    id: str = ""
    account_id: str = ""
    platform: PublishingPlatform
    account_name: str = ""
    account_handle: str = ""
    auth_token: str = ""
    refresh_token: str = ""
    is_active: bool = True
    is_connected: bool = True
    is_simulated: bool = True  # Labeled simulated connector when real OAuth is unconfigured
    notes: str = "SIMULATED_CONNECTOR ready for real OAuth integration"
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def model_post_init(self, __context: Any) -> None:
        if not self.id and self.account_id:
            self.id = self.account_id
        elif not self.account_id and self.id:
            self.account_id = self.id
        if not self.account_name and self.account_handle:
            self.account_name = self.account_handle
        elif not self.account_handle and self.account_name:
            self.account_handle = self.account_name


class PublishingTask(BaseModel):
    id: str = ""
    task_id: str = ""
    job_id: str = ""
    account_id: str = ""
    platform: PublishingPlatform
    title: str = ""
    description: str = ""
    tags: List[str] = Field(default_factory=list)
    status: JobStatus = JobStatus.QUEUED
    scheduled_for: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    published_at: Optional[datetime] = None
    published_url: Optional[str] = None
    remote_video_id: Optional[str] = None
    idempotency_key: str = ""
    error_message: Optional[str] = None
    retry_count: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def model_post_init(self, __context: Any) -> None:
        if not self.id and self.task_id:
            self.id = self.task_id
        elif not self.task_id and self.id:
            self.task_id = self.id


class ProductionSchedule(BaseModel):
    id: str = ""
    schedule_id: str = ""
    name: str = ""
    active: bool = True
    enabled: bool = True
    frequency_days: int = 1
    videos_per_day: int = 1
    cron_expression: str = "0 10 * * *"
    timezone: str = "Asia/Karachi"
    preferred_topics: List[str] = Field(default_factory=list)
    specified_topics: List[str] = Field(default_factory=list)
    approval_mode: ApprovalMode = ApprovalMode.REQUIRED_APPROVAL
    total_runs: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None

    def model_post_init(self, __context: Any) -> None:
        if not self.id and self.schedule_id:
            self.id = self.schedule_id
        elif not self.schedule_id and self.id:
            self.schedule_id = self.id
        if not self.preferred_topics and self.specified_topics:
            self.preferred_topics = self.specified_topics
        elif not self.specified_topics and self.preferred_topics:
            self.specified_topics = self.preferred_topics


class DirectorChatMessage(BaseModel):
    id: str = ""
    message_id: str = ""
    sender: str = "user"  # user | ai | system
    content: str = ""
    text: str = ""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def model_post_init(self, __context: Any) -> None:
        if not self.id and self.message_id:
            self.id = self.message_id
        elif not self.message_id and self.id:
            self.message_id = self.id
        if not self.content and self.text:
            self.content = self.text
        elif not self.text and self.content:
            self.text = self.content


class SystemSettings(BaseModel):
    default_approval_mode: ApprovalMode = ApprovalMode.REQUIRED_APPROVAL
    default_timezone: str = "Asia/Karachi"
    target_video_duration_sec: float = 80.0
    daily_production_quota: int = 5
    global_style_directive: str = "cinematic, scientifically accurate, dramatic pacing"
