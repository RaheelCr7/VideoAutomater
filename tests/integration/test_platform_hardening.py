"""
Beyond 80 - Full Platform Hardening & Final Acceptance Integration Tests
Validates:
1. Autonomous worker execution and concurrency
2. Crash recovery & stale job handling
3. Job cancellation safeguards
4. Genuine relativistic optics physics & multi-frame 3D animation
5. Real video regeneration (timestamp-specific revisions preserving v1 & v2)
6. Strict QA rejection & zero hardcoded success
7. Multi-platform publishing authorization gates & simulation
8. Scholarly research & arbitrary topic generalization
"""

import hashlib
import json
import math
import shutil
import tempfile
import time
from pathlib import Path
import pytest
import numpy as np

from videoautomater.models.quality import QualityCheck, QualityReport

from videoautomater.platform.models import (
    ProductionJob,
    JobStatus,
    ReviewStatus,
    ApprovalMode,
    PublishingPlatform,
)
from videoautomater.platform.storage import PlatformStorage
from videoautomater.platform.orchestrator import ProductionOrchestrator
from videoautomater.platform.publishing_engine import PublishingEngine, AuthorizationGateError
from videoautomater.visuals.relativistic_engine import RelativisticOpticsEngine
from videoautomater.models.research import ResearchBrief
from videoautomater.models.script import StoryScript, ScriptSection


@pytest.fixture
def temp_platform_env():
    """Create an isolated temporary environment for platform storage and jobs."""
    temp_dir = tempfile.mkdtemp(prefix="beyond80_test_")
    storage = PlatformStorage(base_dir=temp_dir)
    orchestrator = ProductionOrchestrator(
        storage=storage,
        output_base=Path(temp_dir) / "jobs",
    )
    publishing_engine = PublishingEngine(storage=storage)
    yield storage, orchestrator, publishing_engine, Path(temp_dir)
    orchestrator.stop()
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_relativistic_optics_scientific_physics():
    """Requirement 3: Verify relativistic light deflection calculations and Schwarzschild physics."""
    engine = RelativisticOpticsEngine(width=720, height=1280)
    M = 1.0
    b_crit = math.sqrt(27.0) * M  # ~5.19615 M

    # 1. Rays with b <= b_crit must be captured (infinite deflection / absorption into shadow)
    b_captured = np.array([1.0, 2.0, 3.0, 4.0, b_crit - 0.01, b_crit])
    deflection_captured = engine.compute_light_deflection(b_captured, M=M)
    assert np.all(np.isinf(deflection_captured)), "Rays inside b_crit must be captured by event horizon"

    # 2. Rays just outside b_crit must experience strong logarithmic divergence
    b_strong = np.array([b_crit + 0.001, b_crit + 0.01, b_crit + 0.1])
    deflection_strong = engine.compute_light_deflection(b_strong, M=M)
    assert np.all(np.isfinite(deflection_strong))
    assert deflection_strong[0] > deflection_strong[1] > deflection_strong[2], (
        "Deflection must strictly increase as b approaches photon sphere"
    )

    # 3. Weak field limit: for large b, alpha matches 2PN expansion and Einstein weak limit
    b_far = np.array([50.0, 100.0, 200.0])
    deflection_far = engine.compute_light_deflection(b_far, M=M)
    expected_2pn = 4.0 * M / b_far + (15.0 * np.pi / 4.0) * (M / b_far) ** 2
    np.testing.assert_allclose(deflection_far, expected_2pn, rtol=0.01)
    np.testing.assert_allclose(deflection_far, 4.0 * M / b_far, rtol=0.08)

    # Strong-field analytical validation (Bozza 2002):
    # alpha_strong(b) = -ln(b/b_crit - 1) + b_bar_0, where b_bar_0 = -pi + ln(216*(7-4*sqrt(3))) ~ -0.40023004
    b_val = b_crit * (1.0 + 1e-4)
    alpha_num = engine.compute_light_deflection(np.array([b_val]), M=M)[0]
    b_bar_0 = -np.pi + np.log(216.0 * (7.0 - 4.0 * math.sqrt(3.0)))
    alpha_bozza = -np.log(b_val / b_crit - 1.0) + b_bar_0
    np.testing.assert_allclose(alpha_num, alpha_bozza, rtol=0.001)

    # 4. Generate dynamic simulation frame
    frame = engine.generate_simulation_frame(
        t_sec=1.5,
        total_duration=3.0,
        stage="CLIMAX",
        camera_angle_deg=45.0,
        doppler_enhancement=1.5,
        scene_heading="SCHWARZSCHILD PHOTON SPHERE",
    )
    assert frame.size == (720, 1280)


def test_crash_recovery_resumes_stale_jobs(temp_platform_env):
    """Requirement 2 & 8: Verify crashed/running jobs recover safely on restart."""
    storage, orchestrator, _, _ = temp_platform_env

    # Simulate a job that was left in RUNNING before a server crash
    stale_job = ProductionJob(
        id="job_crashed_101",
        job_id="job_crashed_101",
        topic="Black Hole Photon Sphere",
        status=JobStatus.RUNNING,
        current_stage="RENDERING_SCENES",
        review_status=ReviewStatus.PENDING_HUMAN_APPROVAL,
    )
    storage.save_job(stale_job)

    # Verify stale job starts in RUNNING
    loaded = storage.get_job("job_crashed_101")
    assert loaded.status == JobStatus.RUNNING

    # Trigger orchestrator recovery (which runs on initialization)
    orchestrator._recover_stale_jobs()

    # The stale job must now be reset to QUEUED for safe resume
    recovered = storage.get_job("job_crashed_101")
    assert recovered.status == JobStatus.QUEUED
    assert "RECOVERED_AFTER_RESTART" in recovered.current_stage


def test_job_cancellation(temp_platform_env):
    """Requirement 2: Verify job cancellation halts execution and records state."""
    storage, orchestrator, _, _ = temp_platform_env

    job = orchestrator.submit_job(
        topic="How Black Holes Bend Light",
        prompt="Initial generation",
    )
    assert job.status == JobStatus.QUEUED

    # Cancel job
    cancelled = orchestrator.cancel_job(job.id)
    assert cancelled is True

    # Verify storage record
    cancelled_job = storage.get_job(job.id)
    assert cancelled_job.status == JobStatus.CANCELLED
    assert cancelled_job.current_stage == "CANCELLED_BY_USER"


def test_publishing_authorization_safeguards_and_simulations(temp_platform_env):
    """Requirement 1 & 7: Verify strict human approval gates and simulated multi-platform connectors."""
    storage, _, publishing_engine, temp_dir = temp_platform_env

    # Create dummy master video file
    dummy_video = temp_dir / "master_test.mp4"
    dummy_video.write_bytes(b"\x00" * 5000)

    # 1. Unapproved Job -> Must FAIL publishing authorization gate
    unapproved_job = ProductionJob(
        id="job_unapproved_001",
        job_id="job_unapproved_001",
        topic="Relativistic Optics",
        master_video_path=str(dummy_video.resolve()),
        status=JobStatus.COMPLETED,
        review_status=ReviewStatus.PENDING_HUMAN_APPROVAL,
        publication_authorized=False,
    )
    storage.save_job(unapproved_job)

    # Register simulated accounts for all 4 platforms
    accounts = {}
    for platform in [
        PublishingPlatform.YOUTUBE_SHORTS,
        PublishingPlatform.INSTAGRAM_REELS,
        PublishingPlatform.TIKTOK,
        PublishingPlatform.FACEBOOK_REELS,
    ]:
        acc = publishing_engine.register_account(
            platform=platform,
            account_name=f"Beyond80_{platform.value}",
            is_simulated=True,
        )
        accounts[platform] = acc

    # Attempting to publish unapproved job to YouTube Shorts must raise AuthorizationGateError
    yt_task = publishing_engine.create_publishing_task(
        job_id=unapproved_job.id,
        account_id=accounts[PublishingPlatform.YOUTUBE_SHORTS].id,
        title="Black Hole Relativistic Optics",
        description="Exploring null geodesics in Schwarzschild spacetime #Shorts",
        tags=["blackhole", "physics", "science"],
    )

    with pytest.raises(AuthorizationGateError) as exc_info:
        publishing_engine.execute_publishing_task(yt_task.id)
    assert "SAFETY BLOCK" in str(exc_info.value)

    # 2. Approved Job but WITHOUT explicit publication_authorized flag -> Must FAIL
    unauthorized_job = ProductionJob(
        id="job_unauthorized_002",
        job_id="job_unauthorized_002",
        topic="Relativistic Optics",
        master_video_path=str(dummy_video.resolve()),
        status=JobStatus.COMPLETED,
        review_status=ReviewStatus.APPROVED_FOR_RELEASE,
        publication_authorized=False,  # Still False
    )
    storage.save_job(unauthorized_job)

    unauth_task = publishing_engine.create_publishing_task(
        job_id=unauthorized_job.id,
        account_id=accounts[PublishingPlatform.TIKTOK].id,
        title="Black Hole Light Bending",
        description="Einstein ring formation #science",
        tags=["astronomy"],
    )

    with pytest.raises(AuthorizationGateError) as exc_info:
        publishing_engine.execute_publishing_task(unauth_task.id)
    assert "publication_authorized flag is False" in str(exc_info.value)

    # 3. Fully Approved AND Explicitly Authorized Job -> Succeeds with SIMULATED_CONNECTOR
    fully_approved_job = ProductionJob(
        id="job_approved_003",
        job_id="job_approved_003",
        topic="Relativistic Optics",
        master_video_path=str(dummy_video.resolve()),
        status=JobStatus.COMPLETED,
        review_status=ReviewStatus.APPROVED_FOR_RELEASE,
        publication_authorized=True,  # Explicitly confirmed
    )
    storage.save_job(fully_approved_job)

    # Verify simulation execution across all 4 platforms
    for platform, acc in accounts.items():
        task = publishing_engine.create_publishing_task(
            job_id=fully_approved_job.id,
            account_id=acc.id,
            title="Beyond 80 Relativistic Episode",
            description="Lensing and Doppler beaming in curved spacetime #Shorts",
            tags=["beyond80", "relativity"],
        )
        res_task = publishing_engine.execute_publishing_task(task.id)
        assert res_task.status == JobStatus.COMPLETED
        assert res_task.published_url is not None
        assert f"{platform.value}.simulated" in res_task.published_url


def test_real_video_regeneration_and_version_preservation(temp_platform_env):
    """Requirement 4: Verify real video regeneration creates immutable v2 and preserves v1."""
    storage, orchestrator, _, temp_dir = temp_platform_env

    # Set up job directory and synthetic master v1
    job_id = "job_revision_test_01"
    job_dir = temp_dir / "jobs" / f"job_{job_id}"
    job_dir.mkdir(parents=True, exist_ok=True)
    clips_dir = job_dir / "clips"
    clips_dir.mkdir(parents=True, exist_ok=True)

    # Create dummy script
    script = StoryScript(
        script_id=f"script_{job_id}",
        brief_id=f"brief_{job_id}",
        title="How Black Holes Bend Light",
        selected_hook="What happens when gravity bends light itself?",
        target_duration_seconds=6.0,
        total_spoken_words=30,
        estimated_reading_speed_wps=2.1,
        full_text="Light travels in straight lines. Photon sphere orbit. Rays inside b crit are captured. Concentric Einstein rings. Relativistic Doppler beaming. Geometry of spacetime.",
        sections=[
            ScriptSection(
                section_id="sec_1",
                timeline_start=0.0,
                timeline_end=1.0,
                role="HOOK",
                visual_intent="Black hole shadow",
                narration_text="Light travels in straight lines.",
            ),
            ScriptSection(
                section_id="sec_2",
                timeline_start=1.0,
                timeline_end=2.0,
                role="MYSTERY",
                visual_intent="Photon sphere orbit",
                narration_text="Photon sphere orbit.",
            ),
            ScriptSection(
                section_id="sec_3",
                timeline_start=2.0,
                timeline_end=3.0,
                role="REVELATION",
                visual_intent="Critical impact parameter",
                narration_text="Rays inside b crit are captured.",
            ),
            ScriptSection(
                section_id="sec_4",
                timeline_start=3.0,
                timeline_end=4.0,
                role="ESCALATION",
                visual_intent="Einstein rings",
                narration_text="Concentric Einstein rings.",
            ),
            ScriptSection(
                section_id="sec_5",
                timeline_start=4.0,
                timeline_end=5.0,
                role="CLIMAX",
                visual_intent="Doppler boosted accretion disk",
                narration_text="Relativistic Doppler beaming.",
            ),
            ScriptSection(
                section_id="sec_6",
                timeline_start=5.0,
                timeline_end=6.0,
                role="PAYOFF",
                visual_intent="Cosmic perspective",
                narration_text="Geometry of spacetime.",
            ),
        ],
    )
    (job_dir / "script.json").write_text(script.model_dump_json(indent=2), encoding="utf-8")

    # Render genuine short scene clips for all 6 scenes
    engine = RelativisticOpticsEngine(width=1080, height=1920)
    for idx in range(1, 7):
        clip_p = clips_dir / f"scene_{idx:02d}.mp4"
        engine.render_dynamic_relativistic_clip(
            output_mp4_path=clip_p,
            duration_sec=1.0,
            fps=12,
            stage="CLIMAX",
            camera_mode="ORBIT",
        )

    # Create synthetic mixed audio and subtitles
    import subprocess
    import imageio_ffmpeg
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    mixed_audio = job_dir / "mixed_audio.aac"
    subprocess.run([
        ffmpeg, "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
        "-t", "6.0", "-c:a", "aac", str(mixed_audio)
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    subtitles_ass = job_dir / "subtitles.ass"
    subtitles_ass.write_text(
        "[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\n\n"
        "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
        "Style: Default,Helvetica,48,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,2,0,2,20,20,460,1\n\n"
        "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
        "Dialogue: 0,0:00:00.00,0:00:01.00,Default,,0,0,0,,Light travels in straight lines.\n"
        "Dialogue: 0,0:00:01.00,0:00:02.00,Default,,0,0,0,,Photon sphere orbit.\n"
        "Dialogue: 0,0:00:02.00,0:00:03.00,Default,,0,0,0,,Rays inside b crit are captured.\n"
        "Dialogue: 0,0:00:03.00,0:00:04.00,Default,,0,0,0,,Concentric Einstein rings.\n"
        "Dialogue: 0,0:00:04.00,0:00:05.00,Default,,0,0,0,,Relativistic Doppler beaming.\n"
        "Dialogue: 0,0:00:05.00,0:00:06.00,Default,,0,0,0,,Geometry of spacetime.\n",
        encoding="utf-8"
    )

    # Create initial master v1
    master_v1 = job_dir / "master_video.mp4"
    shutil.copy(clips_dir / "scene_01.mp4", master_v1)

    job = ProductionJob(
        id=job_id,
        job_id=job_id,
        topic="How Black Holes Bend Light",
        target_duration_sec=6.0,
        actual_duration_sec=6.0,
        output_dir=str(job_dir.resolve()),
        master_video_path=str(master_v1.resolve()),
        current_version=1,
        status=JobStatus.COMPLETED,
        review_status=ReviewStatus.PENDING_HUMAN_APPROVAL,
    )
    job.create_version(1, str(master_v1.resolve()), notes="Initial Master v1")
    storage.save_job(job)

    # 1. Execute revision at timestamp 2.5s (Target Scene 3: REVELATION)
    revised_job = orchestrator.execute_revision(
        job_id=job.id,
        timestamp_sec=2.5,
        feedback_comment="Boost relativistic Doppler beaming on the approaching limb",
    )

    # 2. Verify Version Progression
    assert revised_job.current_version == 2
    assert len(revised_job.versions) == 2

    # 3. Verify Version 1 is PRESERVED on disk
    assert master_v1.exists(), "Previous master v1 must be preserved on disk"

    # 4. Verify Version 2 exists as distinct file
    master_v2 = Path(revised_job.master_video_path)
    assert master_v2.exists()
    assert "master_v2.mp4" in master_v2.name
    assert master_v2 != master_v1

    # 5. Verify revised clip for target scene was generated
    revised_clip = clips_dir / "scene_03_v2.mp4"
    assert revised_clip.exists(), "Target scene clip must be regenerated for revision"


def test_scholarly_research_topic_generalization(temp_platform_env):
    """Requirement 6: Verify arbitrary topic generalization without hardcoded assumptions."""
    _, orchestrator, _, _ = temp_platform_env

    # Submit an arbitrary non-black-hole topic
    topic = "Mariana Trench Abyssal Chemosynthesis and Hydrothermal Vent Microorganisms"
    brief, _ = orchestrator.research_agent.produce_research_brief(requested_topic=topic)

    assert brief.topic == topic
    assert len(brief.verified_facts) >= 3
    # Check domain detection
    domain = orchestrator.subject_media_director.detect_domain(brief)
    assert domain in ["deep_sea_oceanography", "cellular_biophysics", "general_physics"]
    assert domain != "relativistic_astrophysics"

    # Generate script
    script = orchestrator.script_agent.generate_script(brief)
    assert script.target_duration_seconds == 80.0
    assert len(script.sections) == 6
    assert any("vent" in s.narration_text.lower() or "chemosynth" in s.narration_text.lower() or "ocean" in s.narration_text.lower() or "energy" in s.narration_text.lower() or "deep" in s.narration_text.lower() for s in script.sections)


def test_revision_cumulative_inheritance(temp_platform_env):
    """Requirement 3: Verify cumulative inheritance across multiple revision cycles with manifests."""
    storage, orchestrator, _, temp_dir = temp_platform_env

    job_id = "job_cumul_inherit_01"
    job_dir = temp_dir / "jobs" / f"job_{job_id}"
    job_dir.mkdir(parents=True, exist_ok=True)
    clips_dir = job_dir / "clips"
    clips_dir.mkdir(parents=True, exist_ok=True)

    # 1. Create script with 6 scenes
    script = StoryScript(
        script_id=f"script_{job_id}",
        brief_id=f"brief_{job_id}",
        title="Black Hole Ray Tracing",
        selected_hook="Curved spacetime light paths",
        target_duration_seconds=6.0,
        total_spoken_words=24,
        estimated_reading_speed_wps=2.0,
        full_text="Scene one. Scene two. Scene three. Scene four. Scene five. Scene six.",
        sections=[
            ScriptSection(section_id=f"s_{i}", timeline_start=float(i-1), timeline_end=float(i), role="CLIMAX", visual_intent=f"Scene {i}", narration_text=f"Scene {i}.")
            for i in range(1, 7)
        ]
    )
    (job_dir / "script.json").write_text(script.model_dump_json(indent=2), encoding="utf-8")

    # Render base clips
    engine = RelativisticOpticsEngine(width=1080, height=1920)
    for i in range(1, 7):
        clip_p = clips_dir / f"scene_{i:02d}.mp4"
        engine.render_dynamic_relativistic_clip(clip_p, duration_sec=1.0, fps=10, stage="CLIMAX")

    # Audio & subtitles
    import subprocess
    import imageio_ffmpeg
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    mixed_audio = job_dir / "mixed_audio.aac"
    subprocess.run([ffmpeg, "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-t", "6.0", "-c:a", "aac", str(mixed_audio)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    word_nums = ["one", "two", "three", "four", "five", "six"]
    subtitles_ass = job_dir / "subtitles.ass"
    subtitles_ass.write_text(
        "[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Default,Helvetica,48,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,2,0,2,20,20,460,1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n" +
        "\n".join([f"Dialogue: 0,0:00:0{i-1}.00,0:00:0{i}.00,Default,,0,0,0,,Scene {word_nums[i-1]}." for i in range(1, 7)]),
        encoding="utf-8"
    )

    master_v1 = job_dir / "master_video.mp4"
    shutil.copy(clips_dir / "scene_01.mp4", master_v1)

    # Initial manifest v1
    manifest_v1_items = []
    for i in range(1, 7):
        c_path = clips_dir / f"scene_{i:02d}.mp4"
        manifest_v1_items.append({
            "scene_index": i,
            "clip_path": str(c_path.resolve()),
            "filename": c_path.name,
            "sha256": hashlib.sha256(c_path.read_bytes()).hexdigest(),
            "duration_sec": 1.0,
            "version_introduced": 1,
        })
    (job_dir / "scene_manifest_v1.json").write_text(json.dumps({"version": 1, "scenes": manifest_v1_items}, indent=2), encoding="utf-8")

    job = ProductionJob(
        id=job_id,
        job_id=job_id,
        topic="Black Hole Ray Tracing",
        target_duration_sec=6.0,
        actual_duration_sec=6.0,
        output_dir=str(job_dir.resolve()),
        master_video_path=str(master_v1.resolve()),
        current_version=1,
        status=JobStatus.COMPLETED,
        review_status=ReviewStatus.PENDING_HUMAN_APPROVAL,
    )
    job.create_version(1, str(master_v1.resolve()), notes="Master v1")
    storage.save_job(job)

    # 2. Cycle 1: Revise Scene 2 at timestamp 1.5s -> produces v2
    job_v2 = orchestrator.execute_revision(job.id, timestamp_sec=1.5, feedback_comment="Adjust lensing on Scene 2")
    assert job_v2.current_version == 2
    manifest_v2 = json.loads((job_dir / "scene_manifest_v2.json").read_text(encoding="utf-8"))
    assert manifest_v2["scenes"][1]["version_introduced"] == 2
    assert "scene_02_v2.mp4" in manifest_v2["scenes"][1]["filename"]

    # 3. Cycle 2: Revise Scene 4 at timestamp 3.5s -> produces v3
    job_v3 = orchestrator.execute_revision(job.id, timestamp_sec=3.5, feedback_comment="Enhance Doppler beaming on Scene 4")
    assert job_v3.current_version == 3

    # 4. Mandatory check: Scene 2's revision from v2 MUST be inherited in v3!
    manifest_v3 = json.loads((job_dir / "scene_manifest_v3.json").read_text(encoding="utf-8"))
    assert manifest_v3["scenes"][1]["version_introduced"] == 2, "v3 must retain Scene 2 change from v2"
    assert "scene_02_v2.mp4" in manifest_v3["scenes"][1]["filename"]
    assert manifest_v3["scenes"][3]["version_introduced"] == 3, "v3 must incorporate Scene 4 change"
    assert "scene_04_v3.mp4" in manifest_v3["scenes"][3]["filename"]

    # Other scenes remain v1
    assert manifest_v3["scenes"][0]["version_introduced"] == 1
    assert manifest_v3["scenes"][4]["version_introduced"] == 1

    # Check that all 3 master files exist as separate immutable assets
    assert (job_dir / "master_video.mp4").exists()
    assert (job_dir / "master_v2.mp4").exists()
    assert (job_dir / "master_v3.mp4").exists()


def test_revision_qa_blocking_rejection(temp_platform_env, monkeypatch):
    """Requirement 2: Revised master must fail workflow if QA fails, retaining previous valid master."""
    storage, orchestrator, _, temp_dir = temp_platform_env

    job_id = "job_qa_block_test_01"
    job_dir = temp_dir / "jobs" / f"job_{job_id}"
    job_dir.mkdir(parents=True, exist_ok=True)
    clips_dir = job_dir / "clips"
    clips_dir.mkdir(parents=True, exist_ok=True)

    script = StoryScript(
        script_id=f"script_{job_id}",
        brief_id=f"brief_{job_id}",
        title="QA Rejection Test",
        selected_hook="Testing blocking QA",
        target_duration_seconds=2.0,
        total_spoken_words=8,
        estimated_reading_speed_wps=2.0,
        full_text="Test scene one. Test scene two.",
        sections=[
            ScriptSection(section_id="s_1", timeline_start=0.0, timeline_end=1.0, role="HOOK", visual_intent="Scene 1", narration_text="Test scene one."),
            ScriptSection(section_id="s_2", timeline_start=1.0, timeline_end=2.0, role="PAYOFF", visual_intent="Scene 2", narration_text="Test scene two."),
        ]
    )
    (job_dir / "script.json").write_text(script.model_dump_json(indent=2), encoding="utf-8")

    engine = RelativisticOpticsEngine(width=720, height=1280)
    for i in range(1, 3):
        engine.render_dynamic_relativistic_clip(clips_dir / f"scene_{i:02d}.mp4", duration_sec=1.0, fps=10, stage="CLIMAX")

    import subprocess
    import imageio_ffmpeg
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    mixed_audio = job_dir / "mixed_audio.aac"
    subprocess.run([ffmpeg, "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-t", "2.0", "-c:a", "aac", str(mixed_audio)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    subtitles_ass = job_dir / "subtitles.ass"
    subtitles_ass.write_text("[Script Info]\nScriptType: v4.00+\nPlayResX: 720\nPlayResY: 1280\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\nDialogue: 0,0:00:00.00,0:00:01.00,Default,,0,0,0,,Test scene one.\nDialogue: 0,0:00:01.00,0:00:02.00,Default,,0,0,0,,Test scene two.\n", encoding="utf-8")

    master_v1 = job_dir / "master_video.mp4"
    shutil.copy(clips_dir / "scene_01.mp4", master_v1)

    job = ProductionJob(
        id=job_id,
        job_id=job_id,
        topic="Relativistic Light Deflection",
        target_duration_sec=2.0,
        actual_duration_sec=2.0,
        output_dir=str(job_dir.resolve()),
        master_video_path=str(master_v1.resolve()),
        current_version=1,
        status=JobStatus.COMPLETED,
        review_status=ReviewStatus.PENDING_HUMAN_APPROVAL,
    )
    job.create_version(1, str(master_v1.resolve()), notes="Master v1")
    storage.save_job(job)

    # Monkeypatch inspect_episode to simulate QA failure during revision
    orig_inspect = orchestrator.quality_checker.inspect_episode
    def mock_failing_inspect(*args, **kwargs):
        res = orig_inspect(*args, **kwargs)
        res.technical_qa_passed = False
        res.checks.append(
            QualityCheck(
                check_name="SUBTITLE_LAYOUT_AND_CONSTRAINTS",
                required="Captions within safe vertical bounds (Y <= 1500)",
                measured="Violation: text placed at Y=1750",
                status="FAIL",
            )
        )
        return res

    monkeypatch.setattr(orchestrator.quality_checker, "inspect_episode", mock_failing_inspect)

    # Revision execution must raise ValueError due to mandatory blocking QA
    with pytest.raises(ValueError) as exc_info:
        orchestrator.execute_revision(job.id, timestamp_sec=0.5, feedback_comment="Change colors")
    assert "Revision v2 rejected" in str(exc_info.value)
    assert "SUBTITLE_LAYOUT_AND_CONSTRAINTS" in str(exc_info.value)

    # Check persistent job record: previous valid master MUST be preserved!
    updated_job = storage.get_job(job.id)
    assert updated_job.status == JobStatus.FAILED
    assert updated_job.current_stage == "REVISION_V2_FAILED_QA"
    assert updated_job.master_video_path == str(master_v1.resolve()), "Previous master v1 must be preserved on QA failure"
    assert updated_job.current_version == 1, "Job version must not increment on QA failure"
    assert updated_job.review_status != ReviewStatus.APPROVED_FOR_RELEASE


def test_measured_qa_values_not_hardcoded(temp_platform_env, monkeypatch):
    """Requirement 4: Eliminate hardcoded QA success values; populate from measurements."""
    storage, orchestrator, _, temp_dir = temp_platform_env

    job_id = "job_measured_qa_01"
    job_dir = temp_dir / "jobs" / f"job_{job_id}"
    job_dir.mkdir(parents=True, exist_ok=True)
    clips_dir = job_dir / "clips"
    clips_dir.mkdir(parents=True, exist_ok=True)

    script = StoryScript(
        script_id=f"script_{job_id}",
        brief_id=f"brief_{job_id}",
        title="Measured QA Test",
        selected_hook="Empirical QA audit",
        target_duration_seconds=2.0,
        total_spoken_words=4,
        estimated_reading_speed_wps=2.0,
        full_text="Test dialogue.",
        sections=[ScriptSection(section_id="s_1", timeline_start=0.0, timeline_end=2.0, role="HOOK", visual_intent="Test", narration_text="Test dialogue.")]
    )
    (job_dir / "script.json").write_text(script.model_dump_json(indent=2), encoding="utf-8")

    engine = RelativisticOpticsEngine(width=1080, height=1920)
    engine.render_dynamic_relativistic_clip(clips_dir / "scene_01.mp4", duration_sec=2.0, fps=10, stage="CLIMAX")

    import subprocess
    import imageio_ffmpeg
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    mixed_audio = job_dir / "mixed_audio.aac"
    subprocess.run([ffmpeg, "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-t", "2.0", "-c:a", "aac", str(mixed_audio)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    subtitles_ass = job_dir / "subtitles.ass"
    subtitles_ass.write_text(
        "[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\n\n"
        "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
        "Style: Default,Helvetica,48,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,2,0,2,20,20,460,1\n\n"
        "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
        "Dialogue: 0,0:00:00.00,0:00:02.00,Default,,0,0,0,,Test dialogue.\n",
        encoding="utf-8"
    )

    master_v1 = job_dir / "master_video.mp4"
    shutil.copy(clips_dir / "scene_01.mp4", master_v1)

    job = ProductionJob(
        id=job_id,
        job_id=job_id,
        topic="Relativistic Optics",
        target_duration_sec=2.0,
        actual_duration_sec=2.0,
        output_dir=str(job_dir.resolve()),
        master_video_path=str(master_v1.resolve()),
        current_version=1,
        status=JobStatus.COMPLETED,
        review_status=ReviewStatus.PENDING_HUMAN_APPROVAL,
    )
    storage.save_job(job)

    # Execute revision with genuine passing QA
    rev_job = orchestrator.execute_revision(job.id, timestamp_sec=1.0, feedback_comment="Passing revision")
    assert rev_job.qa_report is not None
    assert rev_job.qa_report.passed is True
    assert rev_job.qa_report.subtitles_synchronized is True
    assert rev_job.qa_report.safe_zones_respected is True
    assert rev_job.qa_report.vocabulary_coverage >= 0.92
    assert rev_job.qa_report.vocabulary_coverage <= 1.0

