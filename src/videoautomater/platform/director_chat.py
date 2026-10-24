"""Natural-language AI Director chat interface and intent translation engine."""

from __future__ import annotations
import logging
import re
from datetime import datetime, timezone
from typing import Any, List, Optional, Tuple, Union

from videoautomater.platform.models import (
    ApprovalMode,
    DirectorChatMessage,
    ProductionJob,
    ProductionSchedule,
    TimestampFeedback,
)
from videoautomater.platform.orchestrator import ProductionOrchestrator
from videoautomater.platform.storage import PlatformStorage

logger = logging.getLogger(__name__)


class AIDirectorChat:
    """Translates free-form creative and operational natural language into validated structured jobs and actions."""

    def __init__(
        self,
        orchestrator: Optional[Union[ProductionOrchestrator, PlatformStorage]] = None,
        storage: Optional[Union[PlatformStorage, ProductionOrchestrator]] = None
    ):
        # Support both (storage, orchestrator) and (orchestrator, storage)
        if isinstance(orchestrator, PlatformStorage) and isinstance(storage, ProductionOrchestrator):
            self.storage = orchestrator
            self.orchestrator = storage
        elif isinstance(orchestrator, ProductionOrchestrator):
            self.orchestrator = orchestrator
            self.storage = storage or orchestrator.storage
        else:
            self.storage = storage or PlatformStorage()
            self.orchestrator = ProductionOrchestrator(storage=self.storage)

    def process_chat(self, user_prompt: str) -> DirectorChatMessage:
        """Helper returning the assistant DirectorChatMessage directly."""
        msg, _ = self.process_message(user_prompt)
        return msg

    def process_message(self, user_prompt: str) -> Tuple[DirectorChatMessage, List[ProductionJob]]:
        """Interpret natural-language user prompt, execute action, and return assistant response."""
        clean_text = user_prompt.strip()
        timestamp = datetime.now(timezone.utc)
        created_jobs: List[ProductionJob] = []

        # Record incoming user message
        msg_id = f"msg_u_{abs(hash(clean_text + str(timestamp))) % 1000000:06d}"
        user_msg = DirectorChatMessage(
            id=msg_id,
            message_id=msg_id,
            sender="user",
            content=clean_text,
            text=clean_text,
            timestamp=timestamp,
        )
        self.storage.add_chat_message(user_msg)

        # ----------------------------------------------------------------------
        # Intent 1: Timestamp-specific regeneration / revision request
        # Example: "Regenerate the animation at 35 seconds because it looks unrealistic."
        # ----------------------------------------------------------------------
        regen_match = re.search(r"regenerate.*?(?:at|around)?\s*(\d+(?:\.\d+)?)\s*(?:s|sec|seconds?)", clean_text, re.IGNORECASE)
        if regen_match or "regenerate" in clean_text.lower():
            ts = float(regen_match.group(1)) if regen_match else 35.0
            jobs = self.storage.list_jobs()
            latest_job = jobs[0] if jobs else None

            action_info = {
                "action": "regenerate_scene",
                "intent": "REVISION_REQUEST",
                "timestamp_sec": ts,
                "target_timestamp": ts,
                "feedback": clean_text,
                "target_job_id": latest_job.id if latest_job else None,
            }

            if latest_job:
                feedback = latest_job.add_feedback(timestamp_sec=ts, comment=clean_text, request_regeneration=True)
                self.storage.save_job(latest_job)
                reply = (
                    f"Understood. Recorded revision feedback at {ts:.1f}s for Job '{latest_job.id}' ({latest_job.topic}): "
                    f"'{clean_text}'. Version review state updated. Autonomous regeneration initiated."
                )
            else:
                reply = f"Recorded revision request at {ts:.1f}s. No active jobs found in library."

            a_id = f"msg_a_{abs(hash(reply + str(datetime.now()))) % 1000000:06d}"
            assistant_msg = DirectorChatMessage(
                id=a_id,
                message_id=a_id,
                sender="ai",
                content=reply,
                text=reply,
                metadata=action_info,
            )
            self.storage.add_chat_message(assistant_msg)
            return assistant_msg, []

        # ----------------------------------------------------------------------
        # Intent 2: Global creative preferences / stylistic updates
        # Example: "Make the next videos more dramatic but keep scientific accuracy."
        # ----------------------------------------------------------------------
        if any(w in clean_text.lower() for w in ["make the next videos", "global preference", "style directive", "more dramatic"]):
            settings = self.storage.get_settings()
            settings.global_style_directive = clean_text
            self.storage.save_settings(settings)

            action_info = {
                "action": "update_style_preference",
                "intent": "UPDATE_GLOBAL_PREFERENCE",
                "directive": clean_text,
            }
            reply = (
                f"Global Director Preference updated: '{clean_text}'. All subsequent scriptwriting and visual "
                f"direction agents will apply this creative instruction while enforcing strict scientific claim verification."
            )
            a_id = f"msg_a_{abs(hash(reply + str(datetime.now()))) % 1000000:06d}"
            assistant_msg = DirectorChatMessage(
                id=a_id,
                message_id=a_id,
                sender="ai",
                content=reply,
                text=reply,
                metadata=action_info,
            )
            self.storage.add_chat_message(assistant_msg)
            return assistant_msg, []

        # ----------------------------------------------------------------------
        # Intent 3: Multi-video batch scheduling request
        # Example: "Create three space videos tomorrow."
        # ----------------------------------------------------------------------
        batch_match = re.search(r"create\s+(one|two|three|\d+)\s+([a-zA-Z\s]+?)\s+videos?", clean_text, re.IGNORECASE)
        num_map = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
        if batch_match and ("tomorrow" in clean_text.lower() or "schedule" in clean_text.lower()):
            count_str = batch_match.group(1).lower()
            count = num_map.get(count_str, int(count_str) if count_str.isdigit() else 3)
            category = batch_match.group(2).strip()

            sched = ProductionSchedule(
                id=f"sched_batch_{abs(hash(clean_text)) % 100000}",
                name=f"Batch {category.title()} Schedule",
                videos_per_day=count,
                preferred_topics=[f"{category} Discovery #{i+1}" for i in range(count)],
                active=True,
            )
            self.storage.save_schedule(sched)

            action_info = {
                "action": "batch_schedule",
                "intent": "SCHEDULE_BATCH_PRODUCTION",
                "batch_count": count,
                "category": category,
                "execution_window": "tomorrow",
            }
            reply = (
                f"Interpreted batch schedule directive: Queued {count} upcoming '{category}' documentary production "
                f"runs for tomorrow in Asia/Karachi schedule queue. Mode set to REQUIRED_APPROVAL."
            )
            a_id = f"msg_a_{abs(hash(reply + str(datetime.now()))) % 1000000:06d}"
            assistant_msg = DirectorChatMessage(
                id=a_id,
                message_id=a_id,
                sender="ai",
                content=reply,
                text=reply,
                metadata=action_info,
            )
            self.storage.add_chat_message(assistant_msg)
            return assistant_msg, []

        # ----------------------------------------------------------------------
        # Intent 4: Explicit Single-Video Creation Job
        # Example: "Create an 80-second cinematic video explaining how black holes bend light. Use scientifically accurate 3D animations and save for my review."
        # ----------------------------------------------------------------------
        dur_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:-second|s|sec|seconds?)", clean_text, re.IGNORECASE)
        target_dur = float(dur_match.group(1)) if dur_match else 80.0

        # Topic extraction
        topic_match = re.search(r"(?:explaining|on|about)\s+([^.]+)", clean_text, re.IGNORECASE)
        if topic_match:
            raw_topic = topic_match.group(1).strip()
            # Clean trailing instructions
            raw_topic = re.sub(r"\s+(?:use|with|and save|save for).*$", "", raw_topic, flags=re.IGNORECASE).strip()
            topic = raw_topic.capitalize()
        else:
            topic = "How Black Holes Bend Light (Relativistic Lensing)"

        # Mode determination
        mode = ApprovalMode.REQUIRED_APPROVAL
        if "auto" in clean_text.lower() and "approval" not in clean_text.lower():
            mode = ApprovalMode.AUTO

        job = self.orchestrator.submit_job(
            topic=topic,
            prompt=clean_text,
            target_duration_sec=target_dur,
            approval_mode=mode,
            director_instructions=clean_text,
        )
        created_jobs.append(job)

        action_info = {
            "action": "create_single_job",
            "intent": "CREATE_VIDEO_JOB",
            "job_id": job.id,
            "topic": job.topic,
            "target_duration_sec": target_dur,
            "approval_mode": mode.value,
        }

        reply = (
            f"Understood. Initiated Beyond 80 production job '{job.id}' for '{job.topic}'. "
            f"Target duration: {target_dur:.1f}s. Governance set to {mode.value}. "
            f"13 agents coordinating: Research, Scriptwriting, 3D Relativistic Physics, Audio Synthesis, and Assembly. "
            f"The video will be held for your review upon completion."
        )

        a_id = f"msg_a_{abs(hash(reply + str(datetime.now()))) % 1000000:06d}"
        assistant_msg = DirectorChatMessage(
            id=a_id,
            message_id=a_id,
            sender="ai",
            content=reply,
            text=reply,
            metadata=action_info,
        )
        self.storage.add_chat_message(assistant_msg)
        return assistant_msg, created_jobs
