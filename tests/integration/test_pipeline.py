"""Integration tests for the complete VideoAutomater pipeline."""

import json
import tempfile
from pathlib import Path

import pytest
from PIL import Image

from videoautomater.models.media import SubtitleSegment
from videoautomater.orchestration.workflow import ProductionOrchestrator
from videoautomater.visuals.generator import VisualAssetGenerator
from videoautomater.visuals.subtitles import SubtitleGenerator


def test_visual_generator_creates_1080x1920_frame():
    with tempfile.TemporaryDirectory() as tmp_dir:
        out_file = Path(tmp_dir) / "test_frame.png"
        gen = VisualAssetGenerator(width=1080, height=1920)
        gen.render_scene_frame(
            scene_idx=1,
            title="TEST TITLE",
            category="SCIENCE",
            role="HOOK",
            theme="Cosmic",
            output_path=out_file,
        )

        assert out_file.exists()
        with Image.open(out_file) as img:
            assert img.size == (1080, 1920)


def test_subtitle_generator_srt_and_ass():
    with tempfile.TemporaryDirectory() as tmp_dir:
        srt_file = Path(tmp_dir) / "test.srt"
        ass_file = Path(tmp_dir) / "test.ass"

        segments = [
            SubtitleSegment(index=1, start_time=0.0, end_time=3.5, text="First subtitle segment."),
            SubtitleSegment(index=2, start_time=3.5, end_time=7.0, text="Second subtitle segment."),
        ]

        SubtitleGenerator.generate_srt(segments, srt_file)
        SubtitleGenerator.generate_ass(segments, ass_file)

        assert srt_file.exists()
        assert "00:00:00,000 --> 00:00:03,500" in srt_file.read_text()
        assert "First subtitle segment." in srt_file.read_text()

        assert ass_file.exists()
        assert "PlayResX: 1080" in ass_file.read_text()
        assert "PlayResY: 1920" in ass_file.read_text()
        assert "MarginV, 260" in ass_file.read_text() or "260" in ass_file.read_text()


@pytest.mark.asyncio
async def test_end_to_end_production_orchestration():
    """Verify one complete production run generates all 10 expected artifact files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        output_dir = Path(tmp_dir) / "output"
        orchestrator = ProductionOrchestrator(output_root=output_dir)

        # Run with short duration (e.g. 10s) in test to verify fast end-to-end rendering
        ep_dir = output_dir / "episode_001"
        final_mp4, _quality_report = await orchestrator.generate_episode(
            duration=10.0,
            topic="auto",
            episode_dir=ep_dir,
        )

        # 1. Verify all 10 artifact files exist
        expected_artifacts = [
            "research.json",
            "content_brief.json",
            "script.json",
            "storyboard.json",
            "sources.json",
            "narration.wav",
            "subtitles.srt",
            "final.mp4",
            "metadata.json",
            "quality_report.json",
        ]

        for artifact in expected_artifacts:
            path = ep_dir / artifact
            assert path.exists(), f"Expected artifact missing: {artifact}"
            assert path.stat().st_size > 0, f"Artifact is empty: {artifact}"

        # 2. Verify metadata structure
        meta = json.loads((ep_dir / "metadata.json").read_text())
        assert meta["resolution"] == "1080x1920"
        assert meta["aspect_ratio"] == "9:16"
        assert meta["fps"] == 30

        # 3. Verify final MP4 exists and is playable
        assert final_mp4.exists()
        assert final_mp4.stat().st_size > 50_000  # Non-trivial video file
