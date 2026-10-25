"""
Production runner script for BEYOND 80 Creative Quality Rebuild.
Executes the full 80-second documentary production with the 8 differentiated shots,
generates the 8-shot contact sheet, physics validation report, and produces master_v2.mp4 revision.
"""

import sys
import logging
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from videoautomater.platform.storage import PlatformStorage
from videoautomater.platform.orchestrator import ProductionOrchestrator
from videoautomater.platform.models import JobStatus, ReviewStatus

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("creative_rebuild_runner")

def main():
    logger.info("=== Starting Beyond 80 Creative Quality Rebuild Production ===")
    storage = PlatformStorage()
    orchestrator = ProductionOrchestrator(storage=storage)

    topic = "How Black Holes Bend Light (Relativistic Lensing)"
    job = orchestrator.submit_job(
        topic=topic,
        target_duration_sec=80.0,
        director_instructions="Option 4 Hybrid Approach: 8 differentiated scientific sequences, genuine 3D animations, zero HUD clutter, compact safe-zone subtitles."
    )
    logger.info(f"Created Job {job.id} for topic '{job.topic}'")

    # Execute full production pipeline
    logger.info("Executing 13-agent autonomous production pipeline...")
    job = orchestrator.execute_job(job.id)

    if job.status != JobStatus.COMPLETED:
        logger.error(f"Job {job.id} failed with status {job.status}: {job.error_message}")
        sys.exit(1)

    logger.info(f"Job {job.id} v1 completed successfully! Master MP4: {job.master_video_path}")
    logger.info(f"Review status: {job.review_status}")

    # Execute revision on scene 3 to demonstrate versioned workflow and produce master_v2.mp4
    logger.info("Executing revision on Scene 03 to create master_v2.mp4 with updated physics visual...")
    rev_job = orchestrator.execute_revision(
        job_id=job.id,
        timestamp_sec=22.0,
        feedback_comment="Option 4 Hybrid: Enhanced 3D geodesic photon trajectory tracing"
    )

    logger.info(f"Job {rev_job.id} v{rev_job.current_version} completed! Master v2: {rev_job.master_video_path}")
    logger.info(f"Review status: {rev_job.review_status} (Pending Human Approval)")

    # Print summary of generated artifacts
    out_dir = Path(rev_job.output_dir)
    print("\n" + "="*70)
    print("BEYOND 80 CREATIVE QUALITY REBUILD — ARTIFACTS PRODUCED")
    print("="*70)
    print(f"Job ID: {rev_job.id}")
    print(f"Master Video v1: {out_dir / 'master_video.mp4'}")
    print(f"Master Video v2: {out_dir / 'master_v2.mp4'}")
    print(f"Contact Sheet:   {out_dir / 'contact_sheet.jpg'}")
    print(f"Quality Report:  {out_dir / 'quality_report.json'}")
    print(f"Physics Report:  {out_dir / 'physics_validation_report.json'}")
    print(f"Clips Directory: {out_dir / 'clips'}")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
