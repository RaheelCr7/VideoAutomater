"""
Beyond 80 - Agent Control Center FastAPI Application
Provides RESTful APIs for Dashboard, AI Director Chat, Persistent Job Orchestration,
Video Review Studio, Multi-Platform Publishing, Scheduling, and Analytics.
"""

from __future__ import annotations
import os
import sys
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query, Body, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from videoautomater.platform.models import (
    JobStatus,
    ApprovalMode,
    ReviewStatus,
    PublishingPlatform,
    SystemSettings
)
from videoautomater.platform.storage import PlatformStorage
from videoautomater.platform.orchestrator import ProductionOrchestrator
from videoautomater.platform.director_chat import AIDirectorChat
from videoautomater.platform.publishing_engine import (
    PublishingEngine,
    PublishingError,
    AuthorizationGateError
)
from videoautomater.platform.scheduler import ProductionScheduler
from videoautomater.platform.publish_metadata import build_publish_metadata

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("agent_control_center")

app = FastAPI(
    title="Beyond 80 — Agent Control Center",
    description="Autonomous AI Agent Orchestration and Multi-Platform Publishing Platform",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize storage and engines
storage = PlatformStorage()
orchestrator = ProductionOrchestrator(storage=storage)
chat_engine = AIDirectorChat(storage=storage, orchestrator=orchestrator)
publishing_engine = PublishingEngine(storage=storage)
scheduler = ProductionScheduler(storage=storage, orchestrator=orchestrator)

# Start background workers
orchestrator.start()
scheduler.start()


# Request/Response DTO models
class ChatRequest(BaseModel):
    message: str


class CreateJobRequest(BaseModel):
    topic: Optional[str] = None
    target_duration_sec: float = 80.0
    approval_mode: ApprovalMode = ApprovalMode.REQUIRED_APPROVAL
    director_instructions: Optional[str] = None


class FeedbackRequest(BaseModel):
    timestamp_sec: float
    scene_index: Optional[int] = None
    comment: str
    request_regeneration: bool = False


class ReviewStatusRequest(BaseModel):
    status: ReviewStatus
    reviewer_notes: Optional[str] = None


class AuthorizePublicationRequest(BaseModel):
    authorized: bool


class AccountRegisterRequest(BaseModel):
    platform: PublishingPlatform
    account_name: str
    credentials: Optional[Dict[str, Any]] = None
    is_simulated: bool = True


class PublishTaskRequest(BaseModel):
    job_id: str
    account_id: str
    title: str = ""          # empty: build hook-first metadata from the job's research brief
    description: str = ""
    tags: List[str] = []
    auto_authorize: bool = True
    force_now: bool = False  # skip the posting-cadence pacing for this one release


class ScheduleCreateRequest(BaseModel):
    name: str
    videos_per_day: int = 1
    preferred_topics: Optional[List[str]] = None
    approval_mode: ApprovalMode = ApprovalMode.REQUIRED_APPROVAL
    active: bool = True


# System Health and Stats
@app.get("/api/health")
def get_health():
    jobs = storage.list_jobs()
    running_jobs = [j for j in jobs if j.status == JobStatus.RUNNING]
    return {
        "status": "healthy",
        "service": "Beyond 80 Agent Control Center",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "orchestrator_running": orchestrator.running,
        "scheduler_running": scheduler.running,
        "active_workers": len(running_jobs),
        "total_jobs": len(jobs)
    }


@app.get("/api/dashboard")
def get_dashboard_metrics():
    jobs = storage.list_jobs()
    agents = storage.list_agents()
    schedules = storage.list_schedules()
    pub_tasks = storage.list_publishing_tasks()

    completed = sum(1 for j in jobs if j.status == JobStatus.COMPLETED)
    in_review = sum(1 for j in jobs if j.review_status == ReviewStatus.PENDING_HUMAN_APPROVAL)
    running = sum(1 for j in jobs if j.status == JobStatus.RUNNING)
    failed = sum(1 for j in jobs if j.status == JobStatus.FAILED)
    queued = sum(1 for j in jobs if j.status == JobStatus.QUEUED)

    return {
        "total_jobs": len(jobs),
        "completed_videos": completed,
        "in_review": in_review,
        "active_running": running,
        "queued": queued,
        "failed": failed,
        "total_agents": len(agents),
        "active_schedules": sum(1 for s in schedules if s.active),
        "published_videos": sum(1 for p in pub_tasks if p.status == JobStatus.COMPLETED),
        "recent_jobs": [j.model_dump() for j in jobs[:6]]
    }


# AI Director Chat
@app.post("/api/director/chat")
def handle_director_chat(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Empty message")
    response_msg = chat_engine.process_chat(req.message)
    return response_msg.model_dump()


@app.get("/api/director/history")
def get_director_history(limit: int = 50):
    return [msg.model_dump() for msg in storage.get_chat_history(limit=limit)]


# Production Jobs
@app.get("/api/jobs")
def list_jobs(status: Optional[str] = None):
    jobs = storage.list_jobs()
    if status:
        jobs = [j for j in jobs if j.status.value.lower() == status.lower()]
    return [j.model_dump() for j in jobs]


@app.post("/api/jobs")
def create_job(req: CreateJobRequest):
    job = orchestrator.submit_job(
        topic=req.topic,
        target_duration_sec=req.target_duration_sec,
        approval_mode=req.approval_mode,
        director_instructions=req.director_instructions
    )
    return job.model_dump()


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str):
    job = storage.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job.model_dump()


@app.post("/api/jobs/{job_id}/cancel")
def cancel_job(job_id: str):
    success = orchestrator.cancel_job(job_id)
    if not success:
        raise HTTPException(status_code=400, detail="Could not cancel job")
    return {"status": "cancelled", "job_id": job_id}


# Agent Configuration
@app.get("/api/agents")
def list_agents():
    return [a.model_dump() for a in storage.list_agents()]


@app.put("/api/agents/{agent_id}")
def update_agent(agent_id: str, updates: Dict[str, Any] = Body(...)):
    agent = storage.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    for key, val in updates.items():
        if hasattr(agent, key):
            setattr(agent, key, val)
    agent.last_updated = datetime.now()
    storage.save_agent(agent)
    return agent.model_dump()


# Video Library & Review Studio
@app.get("/api/library")
def get_video_library():
    jobs = storage.list_jobs()
    # Filter completed or ready-for-review videos
    library_items = [
        j.model_dump() for j in jobs
        if j.master_video_path and os.path.exists(j.master_video_path)
    ]
    return library_items


@app.post("/api/review/{job_id}/feedback")
def submit_review_feedback(job_id: str, feedback: FeedbackRequest):
    job = storage.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    fb_record = job.add_feedback(
        timestamp_sec=feedback.timestamp_sec,
        comment=feedback.comment,
        scene_index=feedback.scene_index,
        request_regeneration=feedback.request_regeneration
    )

    if feedback.request_regeneration:
        # Create a new version for revision
        new_version_num = len(job.versions) + 1
        job.create_version(
            version_number=new_version_num,
            video_path=job.master_video_path or "",
            notes=f"Revision requested at {feedback.timestamp_sec:.1f}s: {feedback.comment}"
        )
        job.review_status = ReviewStatus.CHANGES_REQUESTED
        # Trigger orchestrator revision workflow
        orchestrator.submit_revision_job(job, feedback.timestamp_sec, feedback.comment)

    storage.save_job(job)
    return {"status": "feedback_saved", "feedback": fb_record.model_dump()}


@app.post("/api/review/{job_id}/status")
def update_review_status(job_id: str, req: ReviewStatusRequest):
    job = storage.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job.review_status = req.status
    if req.reviewer_notes:
        job.reviewer_notes = req.reviewer_notes

    # If rejected or changes requested, strictly reset authorization
    if req.status in [ReviewStatus.REJECTED, ReviewStatus.CHANGES_REQUESTED]:
        job.publication_authorized = False

    storage.save_job(job)
    return {"status": "updated", "review_status": job.review_status.value}


@app.post("/api/review/{job_id}/authorize-publication")
def authorize_publication(job_id: str, req: AuthorizePublicationRequest):
    job = storage.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if req.authorized and job.review_status != ReviewStatus.APPROVED_FOR_RELEASE:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot authorize release: Video review status is '{job.review_status.value}'. Must be APPROVED_FOR_RELEASE."
        )

    job.publication_authorized = req.authorized
    storage.save_job(job)
    return {
        "status": "updated",
        "job_id": job.id,
        "publication_authorized": job.publication_authorized
    }


# Autonomous Scheduler
@app.get("/api/schedules")
def list_schedules():
    return [s.model_dump() for s in storage.list_schedules()]


@app.post("/api/schedules")
def create_schedule(req: ScheduleCreateRequest):
    schedule = scheduler.create_schedule(
        name=req.name,
        videos_per_day=req.videos_per_day,
        preferred_topics=req.preferred_topics,
        approval_mode=req.approval_mode,
        active=req.active
    )
    return schedule.model_dump()


# Multi-Account Publishing
@app.get("/api/publishing/accounts")
def list_publishing_accounts():
    return [a.model_dump() for a in storage.list_publishing_accounts()]


@app.post("/api/publishing/accounts")
def register_publishing_account(req: AccountRegisterRequest):
    account = publishing_engine.register_account(
        platform=req.platform,
        account_name=req.account_name,
        credentials=req.credentials,
        is_simulated=req.is_simulated
    )
    return account.model_dump()


@app.delete("/api/publishing/accounts/{account_id}")
def delete_publishing_account(account_id: str):
    success = storage.delete_publishing_account(account_id)
    if not success:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"status": "deleted", "account_id": account_id}


@app.get("/api/publishing/tasks")
def list_publishing_tasks():
    return [t.model_dump() for t in storage.list_publishing_tasks()]


@app.get("/api/publishing/metadata-preview")
def preview_publish_metadata(job_id: str = Query(...), platform: str = "youtube_shorts"):
    """The hook-first title, description, tags and pinned comment a release would use. No upload."""
    job = storage.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    try:
        target = PublishingPlatform(platform)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Unknown platform '{platform}'")
    return build_publish_metadata(job, platform=target).to_dict()


@app.post("/api/publishing/publish")
def publish_to_platform(req: PublishTaskRequest):
    try:
        job = storage.get_job(req.job_id)
        if not job:
            raise HTTPException(status_code=404, detail=f"Job {req.job_id} not found")

        if req.auto_authorize:
            job.review_status = ReviewStatus.APPROVED_FOR_RELEASE
            job.publication_authorized = True
            storage.save_job(job)

        account = storage.get_publishing_account(req.account_id)
        if not account:
            raise HTTPException(status_code=404, detail=f"Account {req.account_id} not found")

        if req.title.strip():
            title, description, tags, task_meta = req.title, req.description, req.tags, {}
        else:
            meta = build_publish_metadata(job, platform=account.platform)
            title, description, tags, task_meta = meta.title, meta.description, meta.tags, meta.task_metadata()

        task = publishing_engine.create_publishing_task(
            job_id=req.job_id,
            account_id=req.account_id,
            title=title,
            description=description,
            tags=tags,
            metadata=task_meta
        )
        completed_task = publishing_engine.execute_publishing_task(task.id, force_now=req.force_now)
        return completed_task.model_dump()
    except AuthorizationGateError as age:
        raise HTTPException(status_code=403, detail=str(age))
    except PublishingError as pe:
        raise HTTPException(status_code=400, detail=str(pe))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/publishing/authorize-and-publish")
def authorize_and_publish(
    job_id: str = Query(...),
    platform: Optional[str] = None,
    force_now: bool = Query(False, description="Skip the posting-cadence pacing for this release")
):
    job = storage.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    # Authorize release
    job.review_status = ReviewStatus.APPROVED_FOR_RELEASE
    job.publication_authorized = True
    storage.save_job(job)

    # Dispatch to accounts
    accounts = storage.list_publishing_accounts()
    if not accounts:
        # Auto-register default accounts if none connected
        for p in [PublishingPlatform.YOUTUBE_SHORTS, PublishingPlatform.TIKTOK, PublishingPlatform.INSTAGRAM_REELS, PublishingPlatform.FACEBOOK_REELS]:
            publishing_engine.register_account(p, f"Beyond 80 {p.value.replace('_', ' ').title()}", is_simulated=True)
        accounts = storage.list_publishing_accounts()

    if platform:
        target_accounts = [a for a in accounts if a.platform.value == platform or a.platform == platform]
    else:
        target_accounts = accounts

    results = []
    for acc in target_accounts:
        try:
            meta = build_publish_metadata(job, platform=acc.platform)
            task = publishing_engine.create_publishing_task(
                job_id=job.id,
                account_id=acc.id,
                title=meta.title,
                description=meta.description,
                tags=meta.tags,
                metadata=meta.task_metadata()
            )
            completed_task = publishing_engine.execute_publishing_task(task.id, force_now=force_now)
            results.append(completed_task.model_dump())
        except Exception as e:
            logger.error(f"Failed to publish to {acc.platform}: {e}")
            results.append({"platform": acc.platform.value, "error": str(e)})

    return {
        "status": "published",
        "job_id": job.id,
        "results": results
    }


# Analytics Reporting
@app.get("/api/analytics")
def get_analytics():
    jobs = storage.list_jobs()
    pub_tasks = storage.list_publishing_tasks()

    total_runs = len(jobs)
    passed_qa = sum(1 for j in jobs if j.qa_report and j.qa_report.passed)
    qa_pass_rate = (passed_qa / max(1, total_runs)) * 100

    approved_count = sum(1 for j in jobs if j.review_status == ReviewStatus.APPROVED_FOR_RELEASE)
    approval_rate = (approved_count / max(1, total_runs)) * 100

    # Production duration analytics
    durations = [j.actual_duration_sec for j in jobs if j.actual_duration_sec and j.actual_duration_sec > 0]
    avg_duration = sum(durations) / max(1, len(durations)) if durations else 80.0

    return {
        "total_productions": total_runs,
        "qa_pass_rate_pct": round(qa_pass_rate, 1),
        "approval_rate_pct": round(approval_rate, 1),
        "average_video_duration_sec": round(avg_duration, 1),
        "platforms_connected": len(storage.list_publishing_accounts()),
        "total_publications": len(pub_tasks),
        "simulated_views": sum(15000 + i * 4200 for i in range(len(pub_tasks))),
        "topic_distribution": {
            "Astrophysics & Space": sum(1 for j in jobs if "space" in (j.topic or "").lower() or "black hole" in (j.topic or "").lower() or "neptune" in (j.topic or "").lower()),
            "Biophysics & Extremophiles": sum(1 for j in jobs if "tardigrade" in (j.topic or "").lower() or "bio" in (j.topic or "").lower()),
            "Other Fundamental Science": sum(1 for j in jobs if "space" not in (j.topic or "").lower() and "tardigrade" not in (j.topic or "").lower())
        }
    }


# Settings
@app.get("/api/settings")
def get_settings():
    return storage.get_settings().model_dump()


@app.put("/api/settings")
def update_settings(updates: Dict[str, Any] = Body(...)):
    settings = storage.get_settings()
    for key, val in updates.items():
        if hasattr(settings, key):
            setattr(settings, key, val)
    storage.save_settings(settings)
    if "default_timezone" in updates:
        scheduler.set_timezone(updates["default_timezone"])
    return settings.model_dump()


# Local Video Streaming for Review Studio
@app.api_route("/media/{file_path:path}", methods=["GET", "HEAD"])
def stream_media(file_path: str):
    # Security: resolve absolute path and prevent directory traversal outside workspace
    full_path = os.path.abspath(file_path)
    workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))

    if not full_path.startswith(workspace_root) and not full_path.startswith("/Users/raheel/Desktop/Video Proj/VideoAutomater"):
        raise HTTPException(status_code=403, detail="Access denied")

    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="Media file not found")

    content_type = "video/mp4"
    if full_path.endswith(".png") or full_path.endswith(".jpg"):
        content_type = "image/png"
    elif full_path.endswith(".wav"):
        content_type = "audio/wav"

    return FileResponse(full_path, media_type=content_type)


# Mount Static Files
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
def serve_index():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Agent Control Center Frontend is being initialized."}
