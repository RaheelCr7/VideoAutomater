"""Tests for AnimationDirectorAgent, AnimationEngine, and Cinematic Explanatory Pipeline."""

import tempfile
from pathlib import Path

import pytest

from videoautomater.agents.animation_director import AnimationDirectorAgent
from videoautomater.models.animation import (
    AnimationEvent,
    AnimationObject,
    CameraMotion,
    MasterAnimationPlan,
    SceneAnimationSpec,
    VisualType,
)
from videoautomater.models.research import FactualEvidence, ResearchBrief
from videoautomater.models.script import ScriptSection, StoryScript
from videoautomater.visuals.animation_engine import AnimationEngine


@pytest.fixture
def sample_research_brief():
    return ResearchBrief(
        brief_id="test_brief_01",
        topic="Jupiter's Diamond Rain",
        proposed_title="Jupiter's Diamond Rain",
        alternative_hooks=[
            "Why are diamonds falling inside Jupiter?",
            "What happens to methane under 100,000 atmospheres?",
            "How does planetary pressure forge diamonds in mid-air?",
        ],
        central_question="How does planetary pressure transform methane gas into falling solid diamonds?",
        verified_facts=[
            "At 100,000 atmospheres, methane pyrolyzes into carbon.",
        ],
        supporting_evidence=[
            FactualEvidence(
                claim="Extreme pressures inside gas giants dissociate methane into diamond.",
                source_name="Nature Astronomy",
                url="https://nature.com/example",
                verified=True,
            )
        ],
        suggested_narrative_angle="Step-by-step physical transformation from methane gas to crystalline diamond hail.",
    )


@pytest.fixture
def sample_script():
    sections = [
        ScriptSection(
            section_id="sec_01",
            timeline_start=0.0,
            timeline_end=4.0,
            role="HOOK",
            narration_text="Beneath Jupiter's outer cloud decks, an impossible planetary phenomenon begins.",
            visual_intent="Establishing wide shot.",
        ),
        ScriptSection(
            section_id="sec_02",
            timeline_start=4.0,
            timeline_end=9.0,
            role="ESCALATION",
            narration_text="At one hundred thousand atmospheres, crushing pressure and heat compress methane.",
            visual_intent="Pressure gauge and gas compression.",
        ),
        ScriptSection(
            section_id="sec_03",
            timeline_start=9.0,
            timeline_end=14.0,
            role="REVELATION",
            narration_text="Laser shockwaves rip molecular bonds apart, crystallizing free carbon into pure diamond.",
            visual_intent="Molecular dissociation into diamond lattice.",
        ),
        ScriptSection(
            section_id="sec_04",
            timeline_start=14.0,
            timeline_end=19.0,
            role="PAYOFF",
            narration_text="Precipitating downward, solid diamond hail sinks through liquid metallic hydrogen.",
            visual_intent="Precipitating diamond crystals.",
        ),
    ]
    return StoryScript(
        script_id="test_script_01",
        brief_id="test_brief_01",
        title="Jupiter's Diamond Rain",
        selected_hook=sections[0].narration_text,
        alternative_hooks=["Why are diamonds falling?"],
        target_duration_seconds=19.0,
        total_spoken_words=len(" ".join(s.narration_text for s in sections).split()),
        estimated_reading_speed_wps=2.2,
        sections=sections,
        full_text=" ".join(s.narration_text for s in sections),
    )


def test_animation_director_spec_generation(sample_script, sample_research_brief):
    """Verify AnimationDirectorAgent creates valid, machine-readable SceneAnimationSpecs."""
    director = AnimationDirectorAgent()
    plan = director.compile_animation_plan(sample_script, sample_research_brief, target_duration=19.0)

    assert isinstance(plan, MasterAnimationPlan)
    assert len(plan.scenes) == 4
    assert plan.total_duration == 19.0

    # Scene 1: Celestial approach
    s1 = plan.scenes[0]
    assert s1.visual_type == VisualType.CINEMATIC_ESTABLISHING
    assert s1.template_name == "celestial_approach"
    assert len(s1.events) >= 1
    assert s1.camera.movement_type in ("DOLLY_ZOOM", "ORBIT", "PAN", "TRACKING")

    # Scene 2: Pressure gauge
    s2 = plan.scenes[1]
    assert s2.visual_type == VisualType.EXPLANATORY_PROCESS
    assert s2.template_name == "pressure_depth_gauge"
    assert any("pressure" in lbl.text.lower() or "depth" in lbl.text.lower() for lbl in s2.labels)

    # Scene 3: Molecular transformation
    s3 = plan.scenes[2]
    assert s3.visual_type == VisualType.STRUCTURAL_TRANSFORMATION
    assert s3.template_name == "molecular_crystallization"
    assert any(e.action == "DISSOCIATE" for e in s3.events)
    assert any(e.action == "CRYSTALIZE" for e in s3.events)

    # Scene 4: Diamond precipitation
    s4 = plan.scenes[3]
    assert s4.visual_type == VisualType.SCIENTIFIC_CROSS_SECTION
    assert s4.template_name == "diamond_precipitation"
    assert any(e.action == "PRECIPITATE" for e in s4.events)


def test_animation_engine_clip_rendering(sample_script, sample_research_brief):
    """Verify AnimationEngine renders a valid 1080x1920 30FPS MP4 video clip."""
    director = AnimationDirectorAgent()
    plan = director.compile_animation_plan(sample_script, sample_research_brief, target_duration=19.0)
    spec = plan.scenes[0]

    engine = AnimationEngine(width=1080, height=1920, fps=30)
    with tempfile.TemporaryDirectory() as td:
        clip_path = Path(td) / "test_clip.mp4"
        out = engine.render_scene_clip(spec, clip_path)

        assert out.exists()
        assert out.stat().st_size > 10000  # Non-trivial video file size


def test_subtitle_safe_zone_label_placement(sample_script, sample_research_brief):
    """Verify all on-screen labels are placed strictly outside the subtitle safe zone [1350, 1550]."""
    director = AnimationDirectorAgent()
    plan = director.compile_animation_plan(sample_script, sample_research_brief, target_duration=19.0)

    for scene in plan.scenes:
        for lbl in scene.labels:
            _x, y = lbl.position
            assert not (1320 <= y <= 1580), (
                f"Label '{lbl.text}' at Y={y} violates subtitle safe zone [1320, 1580] in scene {scene.scene_id}"
            )
