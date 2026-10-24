"""Integration test proving dynamic autonomous generation on a brand new, unhardcoded topic."""

import pytest
from pathlib import Path

from videoautomater.agents.animation_director import AnimationDirectorAgent
from videoautomater.content.agent import ScriptwritingAgent
from videoautomater.rendering.cinematic_motion import CinematicMotionEngine
from videoautomater.research.agent import ContentResearchAgent
from videoautomater.research.registry import TopicRegistry
from PIL import Image


def test_autonomous_generation_unhardcoded_topic(tmp_path):
    """Verify that an unhardcoded user topic generates fresh research, script, and animation plan without template leakage."""
    registry = TopicRegistry(storage_path=tmp_path / "test_topic_history.json")
    research_agent = ContentResearchAgent(registry=registry)

    new_topic = "Tardigrade Cryptobiosis: The Physics of Suspended Animation"

    # 1. Produce Autonomous Research Brief
    brief, _ = research_agent.produce_research_brief(requested_topic=new_topic)
    assert brief.topic == new_topic
    assert "Cryptobiosis" in brief.proposed_title
    assert len(brief.verified_facts) >= 3
    assert any("vitrification" in f.lower() or "tardigrade" in f.lower() for f in brief.verified_facts)
    assert len(brief.supporting_evidence) >= 1
    assert "Molecular Cell" in brief.supporting_evidence[0].source_name or "Science" in brief.supporting_evidence[0].source_name

    # 2. Autonomous Creative Scriptwriting
    script_agent = ScriptwritingAgent(target_duration=80.0)
    script = script_agent.generate_script(brief)

    assert script.title == brief.proposed_title
    assert len(script.sections) == 6
    assert script.total_spoken_words >= 100
    assert 1.3 <= script.estimated_reading_speed_wps <= 2.6

    # Verify zero planetary or reactor template leakage in script
    for sec in script.sections:
        assert "neptune" not in sec.narration_text.lower()
        assert "uranium" not in sec.narration_text.lower()
        assert "diamond" not in sec.narration_text.lower()
        assert "voyager" not in sec.narration_text.lower()

    # 3. Dynamic Visual & Animation Planning
    director = AnimationDirectorAgent()
    storyboard_anim = director.compile_animation_plan(script, brief)

    assert len(storyboard_anim.scenes) == 6
    for scene in storyboard_anim.scenes:
        # Zero space templates leaked
        assert scene.template_name != "celestial_approach"
        assert scene.template_name != "diamond_precipitation"
        assert "NASA VOYAGER 2" not in [lbl.text for lbl in scene.labels]

    # 4. Render Sample Visual Proof
    demo_out_dir = Path("output/autonomous_topic_demo")
    demo_out_dir.mkdir(parents=True, exist_ok=True)
    sample_img = demo_out_dir / "tardigrade_sample.jpg"

    # Create illustrative macro canvas
    im = Image.new("RGB", (1080, 1920), (8, 20, 24))
    im.save(sample_img)

    motion_engine = CinematicMotionEngine(width=1080, height=1920, fps=30)
    sample_mp4 = demo_out_dir / "tardigrade_sample.mp4"
    motion_engine.render_cinematic_clip(
        image_path=sample_img,
        output_mp4=sample_mp4,
        duration=2.0,
        camera_mode="CINEMATIC_FLOAT",
        branding_badge="BEYOND 80 // BIOLOGY",
        scientific_label="TARDIGRADE CRYPTOBIOSIS // SUSPENDED ANIMATION",
    )

    assert sample_mp4.exists()
    assert sample_mp4.stat().st_size > 10000
