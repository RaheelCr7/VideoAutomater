"""Tests for CinematicMotionEngine in Visual-First Documentary Production."""

import tempfile
from pathlib import Path

import pytest
from PIL import Image

from videoautomater.rendering.cinematic_motion import CinematicMotionEngine


@pytest.fixture
def sample_test_images():
    with tempfile.TemporaryDirectory() as td:
        img_a = Path(td) / "test_a.jpg"
        img_b = Path(td) / "test_b.jpg"

        Image.new("RGB", (768, 1376), (15, 25, 45)).save(img_a, "JPEG")
        Image.new("RGB", (768, 1376), (45, 25, 15)).save(img_b, "JPEG")
        yield img_a, img_b


def test_cinematic_clip_rendering(sample_test_images):
    """Verify CinematicMotionEngine renders a 1080x1920 MP4 clip with cinematic float."""
    img_a, _ = sample_test_images
    engine = CinematicMotionEngine(width=1080, height=1920, fps=30)

    with tempfile.TemporaryDirectory() as td:
        out_mp4 = Path(td) / "out_clip.mp4"
        clip = engine.render_cinematic_clip(
            image_path=img_a,
            output_mp4=out_mp4,
            duration=1.0,
            branding_badge="BEYOND 80 // TEST",
            scientific_label="TEST LABEL",
        )
        assert clip.exists()
        assert clip.stat().st_size > 1000


def test_transformation_clip_rendering(sample_test_images):
    """Verify CinematicMotionEngine renders a multi-state transformation clip."""
    img_a, img_b = sample_test_images
    engine = CinematicMotionEngine(width=1080, height=1920, fps=30)

    with tempfile.TemporaryDirectory() as td:
        out_mp4 = Path(td) / "out_trans.mp4"
        clip = engine.render_transformation_clip(
            image_a_path=img_a,
            image_b_path=img_b,
            output_mp4=out_mp4,
            duration=1.0,
            branding_badge="BEYOND 80 // QUANTUM",
            scientific_label="PHASE TRANSITION",
        )
        assert clip.exists()
        assert clip.stat().st_size > 1000
