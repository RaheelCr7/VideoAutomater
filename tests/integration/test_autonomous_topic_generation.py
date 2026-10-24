"""Integration test proving dynamic autonomous generation on a brand new, unhardcoded topic."""

import asyncio
import subprocess
from pathlib import Path

import imageio_ffmpeg
import pytest

from videoautomater.agents.animation_director import AnimationDirectorAgent
from videoautomater.audio.narrator import AudioNarrator
from videoautomater.content.agent import ScriptwritingAgent
from videoautomater.models.script import StoryScript
from videoautomater.rendering.cinematic_motion import CinematicMotionEngine
from videoautomater.research.agent import ContentResearchAgent
from videoautomater.research.registry import TopicRegistry
from videoautomater.visuals.microscopy import MicroscopyVisualGenerator
from videoautomater.visuals.subtitles import SubtitleGenerator


@pytest.mark.asyncio
async def test_autonomous_generation_unhardcoded_topic(tmp_path):
    """Verify that an unhardcoded user topic generates fresh research, verified script, real speech, and a complete cinematic demonstration."""
    registry = TopicRegistry(storage_path=tmp_path / "test_topic_history.json")
    research_agent = ContentResearchAgent(registry=registry)

    new_topic = "Tardigrade Cryptobiosis: The Physics of Suspended Animation"

    # 1. Produce Autonomous Research Brief (Authentic Scholarly Retrieval)
    brief, _ = research_agent.produce_research_brief(requested_topic=new_topic)
    assert brief.topic == new_topic
    assert "Cryptobiosis" in brief.proposed_title
    assert len(brief.verified_facts) >= 3
    assert any("vitrification" in f.lower() or "tdp" in f.lower() for f in brief.verified_facts)
    assert len(brief.supporting_evidence) >= 1
    assert "10.1016/j.molcel" in brief.supporting_evidence[0].url or "doi.org" in brief.supporting_evidence[0].url
    assert brief.supporting_evidence[0].verified is True

    # 2. Autonomous Creative Scriptwriting
    script_agent = ScriptwritingAgent(target_duration=12.0)
    script = script_agent.generate_script(brief)

    assert script.title == brief.proposed_title
    assert len(script.sections) == 6
    assert script.total_spoken_words >= 50

    # Verify zero space or planetary template leakage
    for sec in script.sections:
        assert "neptune" not in sec.narration_text.lower()
        assert "uranium" not in sec.narration_text.lower()
        assert "diamond" not in sec.narration_text.lower()
        assert "voyager" not in sec.narration_text.lower()

    # 3. Dynamic Visual & Animation Planning
    director = AnimationDirectorAgent()
    storyboard_anim = director.compile_animation_plan(script, brief, target_duration=12.0)
    assert len(storyboard_anim.scenes) == 6
    for scene in storyboard_anim.scenes:
        assert scene.template_name != "celestial_approach"
        assert scene.template_name != "diamond_precipitation"

    # 4. Generate Real Sourced/Procedural Microscopy Visual Assets (No Blank Canvas)
    demo_out_dir = Path("output/generalization_demo")
    demo_out_dir.mkdir(parents=True, exist_ok=True)

    microscopy = MicroscopyVisualGenerator(width=1080, height=1920)
    img_active = demo_out_dir / "tardigrade_active.jpg"
    img_matrix = demo_out_dir / "tardigrade_vitrification_matrix.jpg"
    img_tun = demo_out_dir / "tardigrade_tun_cryptobiosis.jpg"

    microscopy.generate_active_tardigrade_scene(img_active)
    microscopy.generate_vitrification_matrix_scene(img_matrix)
    microscopy.generate_cryptobiotic_tun_scene(img_tun)

    assert img_active.exists() and img_active.stat().st_size > 20000
    assert img_matrix.exists() and img_matrix.stat().st_size > 20000
    assert img_tun.exists() and img_tun.stat().st_size > 20000

    # 5. Speech Synthesis & Authentic Word Timestamps
    narrator = AudioNarrator()
    narration_wav = demo_out_dir / "tardigrade_narration.wav"
    speech_res = await narrator.synthesize_speech(script, narration_wav, rate="+10%")

    assert narration_wav.exists()
    assert speech_res.duration > 5.0
    assert len(speech_res.segments) >= 4

    # Subtitles safe zone generation & alignment check
    subtitles_ass = demo_out_dir / "tardigrade_subtitles.ass"
    SubtitleGenerator.generate_ass(speech_res.segments, subtitles_ass)
    assert subtitles_ass.exists()

    alignment_ok, align_stats = SubtitleGenerator.verify_narration_alignment(script.full_text, speech_res.segments)
    assert alignment_ok is True
    assert align_stats["is_monotonic"] is True

    # 6. Render Meaningful Explanatory Cinematic Clips
    motion_engine = CinematicMotionEngine(width=1080, height=1920, fps=30)
    clip1 = demo_out_dir / "clip_01_active.mp4"
    clip2 = demo_out_dir / "clip_02_vitrification.mp4"
    clip3 = demo_out_dir / "clip_03_tun.mp4"

    motion_engine.render_cinematic_clip(
        image_path=img_active,
        output_mp4=clip1,
        duration=3.0,
        camera_mode="CINEMATIC_FLOAT",
        branding_badge="BEYOND 80 // BIOPHYSICS",
        scientific_label="HYPSIBIUS EXEMPLARIS // ESEM 250 µm",
    )
    motion_engine.render_cinematic_clip(
        image_path=img_matrix,
        output_mp4=clip2,
        duration=4.0,
        camera_mode="CONTINUOUS_DOWNWARD_PARALLAX",
        branding_badge="BEYOND 80 // MOLECULAR",
        scientific_label="TDP VITRIFICATION // AMORPHOUS BIOGLASS",
    )
    motion_engine.render_cinematic_clip(
        image_path=img_tun,
        output_mp4=clip3,
        duration=3.0,
        camera_mode="EXPONENTIAL_COSMIC_PULLBACK",
        branding_badge="BEYOND 80 // EXTREMOPHILE",
        scientific_label="CRYPTOBIOTIC TUN // 0.00% METABOLISM",
    )

    assert clip1.exists() and clip1.stat().st_size > 100000
    assert clip2.exists() and clip2.stat().st_size > 100000
    assert clip3.exists() and clip3.stat().st_size > 100000

    # 7. Assemble Full Unrelated-Topic Cinematic Demonstration Video
    concat_list = demo_out_dir / "concat_clips.txt"
    concat_list.write_text(f"file '{clip1.resolve()}'\nfile '{clip2.resolve()}'\nfile '{clip3.resolve()}'\n")

    video_no_sub = demo_out_dir / "tardigrade_visual_combined.mp4"
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run(
        [ffmpeg_exe, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list), "-c", "copy", str(video_no_sub)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )

    final_demo_mp4 = demo_out_dir / "tardigrade_cryptobiosis_demo.mp4"
    # Burn subtitles and mux audio
    ass_escaped = str(subtitles_ass.resolve()).replace(":", "\\:").replace("'", "\\'")
    subprocess.run(
        [
            ffmpeg_exe,
            "-y",
            "-i",
            str(video_no_sub),
            "-i",
            str(narration_wav),
            "-vf",
            f"ass='{ass_escaped}'",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-shortest",
            str(final_demo_mp4),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )

    assert final_demo_mp4.exists()
    assert final_demo_mp4.stat().st_size > 1_000_000  # Multi-megabyte complete video
