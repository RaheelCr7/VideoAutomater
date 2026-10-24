"""Durable persistent storage layer for platform state, jobs, review records, and settings."""

from __future__ import annotations
import json
import logging
from pathlib import Path
from typing import Any, List, Optional, Union

from videoautomater.platform.models import (
    AgentConfig,
    AgentStatus,
    ApprovalMode,
    DirectorChatMessage,
    JobStatus,
    ProductionJob,
    ProductionSchedule,
    PublishingAccount,
    PublishingPlatform,
    PublishingTask,
    ReviewStatus,
    TimestampFeedback,
    VersionReviewRecord,
    SystemSettings
)

logger = logging.getLogger(__name__)


class PlatformStorage:
    """Manages persistent JSON state files for durable execution across server restarts."""

    def __init__(self, data_dir: Optional[Union[Path, str]] = None, base_dir: Optional[Union[Path, str]] = None):
        target = base_dir or data_dir or "output/platform_db"
        self.data_dir = Path(target)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.jobs_file = self.data_dir / "jobs.json"
        self.schedules_file = self.data_dir / "schedules.json"
        self.accounts_file = self.data_dir / "accounts.json"
        self.tasks_file = self.data_dir / "tasks.json"
        self.chat_file = self.data_dir / "chat.json"
        self.agents_file = self.data_dir / "agents.json"
        self.settings_file = self.data_dir / "settings.json"

        self._init_defaults()

    def _read_json(self, path: Path, default: Any) -> Any:
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except Exception as e:
                logger.error(f"Error reading {path}: {e}")
        return default

    def _write_json(self, path: Path, data: Any):
        try:
            path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
        except Exception as e:
            logger.error(f"Error writing {path}: {e}")

    def _init_defaults(self):
        # 13 default platform agents
        if not self.agents_file.exists():
            agents = [
                AgentConfig(
                    id="research_agent",
                    name="Scholarly Research Agent",
                    role_description="Crossref API scholar querying peer-reviewed journals for empirically verified claims.",
                    system_prompt="Execute claim-level validation. Reject non-peer-reviewed extrapolations.",
                ),
                AgentConfig(
                    id="story_director",
                    name="Story Director Agent",
                    role_description="Structures hook, build, climax, and resolution into tight vertical pacing.",
                    system_prompt="Create suspenseful, scientific hooks within the first 3 seconds.",
                ),
                AgentConfig(
                    id="scriptwriting_agent",
                    name="Scriptwriting Agent",
                    role_description="Calculates word budgets (~2.5 words/sec), ensuring exact 80s target durations.",
                    system_prompt="Draft concise, punchy educational narration. Adhere to safe word limits.",
                ),
                AgentConfig(
                    id="visual_director",
                    name="Visual Director Agent",
                    role_description="Selects domain color palettes, lighting schemes, and cinematic framing standards.",
                    system_prompt="Establish premium vertical cinema aesthetics with high micro-contrast.",
                ),
                AgentConfig(
                    id="asset_licensing_agent",
                    name="Asset Research & Licensing Agent",
                    role_description="Audits asset provenance, verifies rights, and ensures synthetic imagery is explicitly disclosed.",
                    system_prompt="Never misrepresent AI or procedural reconstructions as genuine NASA photography.",
                ),
                AgentConfig(
                    id="animation_director",
                    name="Animation Director Agent",
                    role_description="Compiles dynamic animation plans, camera easing curves, and visual event triggers.",
                    system_prompt="Ensure kinetic camera motions are smooth and meaningful.",
                ),
                AgentConfig(
                    id="three_d_production_agent",
                    name="3D Production Agent",
                    role_description="Renders relativistic light bending, crystal transformations, and procedural models.",
                    system_prompt="Simulate accurate physical phenomena (Snell caustics, null geodesics).",
                ),
                AgentConfig(
                    id="narration_sound_agent",
                    name="Narration & Sound Agent",
                    role_description="Synthesizes neural voiceover with real word timestamps and mixes ambient soundscape.",
                    system_prompt="Capture exact millisecond TTS word boundaries. Never substitute tone tracks.",
                ),
                AgentConfig(
                    id="video_assembly_agent",
                    name="Video Assembly Agent",
                    role_description="Directly renders and burns safe-zone subtitles into the final broadcast master MP4.",
                    system_prompt="Single-master direct assembly. Keep lower UI zones clean (Y=1460).",
                ),
                AgentConfig(
                    id="qa_agent",
                    name="Scientific & Technical QA Agent",
                    role_description="Executes 11 automated quality inspection gates on duration, audio, and captions.",
                    system_prompt="Fail fast if vocabulary coverage < 95% or audio cut off prematurely.",
                ),
                AgentConfig(
                    id="publishing_agent",
                    name="Multi-Account Publishing Agent",
                    role_description="Manages destination queues for YouTube, Instagram, TikTok, and Facebook.",
                    system_prompt="Strictly block publishing unless master version is APPROVED_FOR_RELEASE.",
                ),
                AgentConfig(
                    id="analytics_agent",
                    name="Analytics & Feedback Agent",
                    role_description="Aggregates production and distribution metrics to inform future topic rankings.",
                    system_prompt="Report accurate real metrics. Avoid synthetic inflation.",
                ),
                AgentConfig(
                    id="production_orchestrator",
                    name="Production Orchestrator",
                    role_description="Coordinates asynchronous job execution, worker concurrency, and recovery.",
                    system_prompt="Ensure durable persistent pipeline execution across all agent stages.",
                ),
            ]
            self._write_json(self.agents_file, [a.model_dump() for a in agents])

        if not self.settings_file.exists():
            default_settings = SystemSettings()
            self._write_json(self.settings_file, default_settings.model_dump())

    # --- Job Operations ---
    def list_jobs(self) -> List[ProductionJob]:
        raw = self._read_json(self.jobs_file, [])
        return [ProductionJob(**j) for j in raw]

    def get_job(self, job_id: str) -> Optional[ProductionJob]:
        for j in self.list_jobs():
            if j.id == job_id or j.job_id == job_id:
                return j
        return None

    def save_job(self, job: ProductionJob):
        jobs = self.list_jobs()
        idx = next((i for i, x in enumerate(jobs) if x.id == job.id or (job.job_id and x.job_id == job.job_id)), None)
        if idx is not None:
            jobs[idx] = job
        else:
            jobs.insert(0, job)
        self._write_json(self.jobs_file, [j.model_dump() for j in jobs])

    # --- Review Operations ---
    def add_job_feedback(self, job_id: str, feedback: TimestampFeedback) -> Optional[ProductionJob]:
        job = self.get_job(job_id)
        if not job:
            return None
        job.feedback.append(feedback)
        self.save_job(job)
        return job

    def update_review_status(
        self,
        job_id: str,
        status: ReviewStatus,
        reviewer_notes: str = "",
        is_master_approved: bool = False,
    ) -> Optional[ProductionJob]:
        job = self.get_job(job_id)
        if not job:
            return None
        job.review_status = status
        job.reviewer_notes = reviewer_notes
        if status in [ReviewStatus.REJECTED, ReviewStatus.CHANGES_REQUESTED]:
            job.publication_authorized = False
        self.save_job(job)
        return job

    # --- Agent Configuration Operations ---
    def list_agents(self) -> List[AgentConfig]:
        raw = self._read_json(self.agents_file, [])
        return [AgentConfig(**a) for a in raw]

    def get_agent(self, agent_id: str) -> Optional[AgentConfig]:
        for a in self.list_agents():
            if a.id == agent_id or a.agent_id == agent_id:
                return a
        return None

    def save_agent(self, agent: AgentConfig):
        agents = self.list_agents()
        idx = next((i for i, x in enumerate(agents) if x.id == agent.id or x.agent_id == agent.agent_id), None)
        if idx is not None:
            agents[idx] = agent
        else:
            agents.append(agent)
        self._write_json(self.agents_file, [a.model_dump() for a in agents])

    def update_agent_status(
        self,
        agent_id: str,
        status: AgentStatus,
        action: str = "",
        current_job_id: Optional[str] = None
    ) -> Optional[AgentConfig]:
        agent = self.get_agent(agent_id)
        if not agent:
            return None
        agent.status = status
        agent.last_action = action or agent.last_action
        agent.current_job_id = current_job_id
        self.save_agent(agent)
        return agent

    # --- Schedule Operations ---
    def list_schedules(self) -> List[ProductionSchedule]:
        raw = self._read_json(self.schedules_file, [])
        return [ProductionSchedule(**s) for s in raw]

    def get_schedule(self, schedule_id: str) -> Optional[ProductionSchedule]:
        for s in self.list_schedules():
            if s.id == schedule_id or s.schedule_id == schedule_id:
                return s
        return None

    def save_schedule(self, schedule: ProductionSchedule):
        scheds = self.list_schedules()
        idx = next((i for i, x in enumerate(scheds) if x.id == schedule.id or (schedule.schedule_id and x.schedule_id == schedule.schedule_id)), None)
        if idx is not None:
            scheds[idx] = schedule
        else:
            scheds.append(schedule)
        self._write_json(self.schedules_file, [s.model_dump() for s in scheds])

    # --- Publishing Operations ---
    def list_publishing_accounts(self) -> List[PublishingAccount]:
        raw = self._read_json(self.accounts_file, [])
        return [PublishingAccount(**a) for a in raw]

    def get_publishing_account(self, account_id: str) -> Optional[PublishingAccount]:
        for a in self.list_publishing_accounts():
            if a.id == account_id or a.account_id == account_id:
                return a
        return None

    def save_publishing_account(self, account: PublishingAccount):
        accs = self.list_publishing_accounts()
        idx = next((i for i, x in enumerate(accs) if x.id == account.id or (account.account_id and x.account_id == account.account_id)), None)
        if idx is not None:
            accs[idx] = account
        else:
            accs.append(account)
        self._write_json(self.accounts_file, [a.model_dump() for a in accs])

    def list_publishing_tasks(self) -> List[PublishingTask]:
        raw = self._read_json(self.tasks_file, [])
        return [PublishingTask(**t) for t in raw]

    def get_publishing_task(self, task_id: str) -> Optional[PublishingTask]:
        for t in self.list_publishing_tasks():
            if t.id == task_id or t.task_id == task_id:
                return t
        return None

    def save_publishing_task(self, task: PublishingTask):
        tasks = self.list_publishing_tasks()
        idx = next((i for i, x in enumerate(tasks) if x.id == task.id or (task.task_id and x.task_id == task.task_id)), None)
        if idx is not None:
            tasks[idx] = task
        else:
            tasks.append(task)
        self._write_json(self.tasks_file, [t.model_dump() for t in tasks])

    # --- Chat Operations ---
    def list_chat_messages(self) -> List[DirectorChatMessage]:
        raw = self._read_json(self.chat_file, [])
        return [DirectorChatMessage(**m) for m in raw]

    def get_chat_history(self, limit: int = 50) -> List[DirectorChatMessage]:
        msgs = self.list_chat_messages()
        return msgs[-limit:]

    def add_chat_message(self, message: DirectorChatMessage):
        msgs = self.list_chat_messages()
        msgs.append(message)
        self._write_json(self.chat_file, [m.model_dump() for m in msgs])

    # --- Settings Operations ---
    def get_settings(self) -> SystemSettings:
        raw = self._read_json(self.settings_file, {})
        if isinstance(raw, dict):
            return SystemSettings(**raw)
        return SystemSettings()

    def save_settings(self, settings: Union[SystemSettings, dict]):
        if isinstance(settings, SystemSettings):
            data = settings.model_dump()
        else:
            data = settings
        self._write_json(self.settings_file, data)

    def update_settings(self, new_settings: dict[str, Any]):
        curr = self.get_settings().model_dump()
        curr.update(new_settings)
        self.save_settings(curr)
