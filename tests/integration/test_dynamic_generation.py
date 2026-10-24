"""Integration test demonstrating dynamic, non-hardcoded story and animation generation across diverse domains."""

import pytest
from videoautomater.agents.animation_director import AnimationDirectorAgent
from videoautomater.content.agent import ScriptwritingAgent
from videoautomater.models.animation import MasterAnimationPlan, VisualType
from videoautomater.models.research import ResearchBrief
from videoautomater.models.script import StoryScript
from videoautomater.research.curated_catalog import VERIFIED_CANDIDATES
from videoautomater.visuals.subtitles import SubtitleGenerator


@pytest.fixture
def neptune_brief() -> ResearchBrief:
    raw = next(c for c in VERIFIED_CANDIDATES if "cand_space_001" in c["id"])
    brief_data = raw["brief"].copy()
    brief_data["brief_id"] = "brief_neptune_test"
    brief_data["topic"] = raw["title"]
    return ResearchBrief(**brief_data)


@pytest.fixture
def oklo_brief() -> ResearchBrief:
    raw = next(c for c in VERIFIED_CANDIDATES if "cand_science_002" in c["id"])
    brief_data = raw["brief"].copy()
    brief_data["brief_id"] = "brief_oklo_test"
    brief_data["topic"] = raw["title"]
    return ResearchBrief(**brief_data)


def test_dynamic_script_generation_across_domains(neptune_brief, oklo_brief):
    """Verify ScriptwritingAgent dynamically creates domain-unique scripts without template bleeding."""
    agent = ScriptwritingAgent(target_duration=80.0)

    # 1. Generate Neptune script
    neptune_script = agent.generate_script(neptune_brief)
    assert isinstance(neptune_script, StoryScript)
    assert len(neptune_script.sections) == 6
    assert neptune_script.target_duration_seconds == 80.0
    neptune_text = neptune_script.full_text.lower()

    # Neptune domain assertions
    assert "neptune" in neptune_text
    assert "diamond" in neptune_text
    assert "uranium" not in neptune_text
    assert "fission" not in neptune_text
    assert "reactor" not in neptune_text

    # 2. Generate Oklo script
    oklo_script = agent.generate_script(oklo_brief)
    assert isinstance(oklo_script, StoryScript)
    assert len(oklo_script.sections) == 6
    assert oklo_script.target_duration_seconds == 80.0
    oklo_text = oklo_script.full_text.lower()

    # Oklo domain assertions
    assert "uranium" in oklo_text
    assert "fission" in oklo_text
    assert "reactor" in oklo_text
    assert "neptune" not in oklo_text
    assert "spacecraft" not in oklo_text
    assert "methane" not in oklo_text

    # Both scripts must have valid pacing (2.0 - 2.5 wps)
    assert 2.0 <= neptune_script.estimated_reading_speed_wps <= 2.5
    assert 2.0 <= oklo_script.estimated_reading_speed_wps <= 2.5


def test_dynamic_animation_planning_across_domains(neptune_brief, oklo_brief):
    """Verify AnimationDirectorAgent compiles domain-appropriate visual specs and objects."""
    script_agent = ScriptwritingAgent(target_duration=80.0)
    director = AnimationDirectorAgent()

    # 1. Neptune Space Animation Plan
    neptune_script = script_agent.generate_script(neptune_brief)
    neptune_plan = director.compile_animation_plan(neptune_script, neptune_brief, target_duration=80.0)
    assert isinstance(neptune_plan, MasterAnimationPlan)
    assert len(neptune_plan.scenes) == 6

    # Verify Neptune visual specs (space, celestial approach, diamond unit cell)
    s1_neptune = neptune_plan.scenes[0]
    assert s1_neptune.template_name == "celestial_approach"
    assert any("planet" in obj.object_id.lower() for obj in s1_neptune.objects)

    s3_neptune = neptune_plan.scenes[2]
    assert s3_neptune.template_name == "molecular_crystallization"
    assert any("diamond" in obj.object_id.lower() for obj in s3_neptune.objects)

    # 2. Oklo Nuclear Geology Animation Plan
    oklo_script = script_agent.generate_script(oklo_brief)
    oklo_plan = director.compile_animation_plan(oklo_script, oklo_brief, target_duration=80.0)
    assert isinstance(oklo_plan, MasterAnimationPlan)
    assert len(oklo_plan.scenes) == 6

    # Verify Oklo visual specs (geological descent, subatomic fission, hydrothermal cycle)
    s1_oklo = oklo_plan.scenes[0]
    assert s1_oklo.template_name == "geological_descent"
    assert any("uranium" in obj.object_id.lower() or "bedrock" in obj.object_id.lower() for obj in s1_oklo.objects)
    assert not any("planet_disk" in obj.object_id.lower() for obj in s1_oklo.objects)

    s4_oklo = oklo_plan.scenes[3]
    assert s4_oklo.template_name == "subatomic_fission"
    assert any("u235" in obj.object_id.lower() or "moderator" in obj.object_id.lower() for obj in s4_oklo.objects)
