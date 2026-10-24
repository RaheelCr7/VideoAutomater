"""Unit tests for the Creative Scriptwriting Agent."""

import pytest

from videoautomater.content.agent import ScriptwritingAgent
from videoautomater.models.research import BackupTopic, FactualEvidence, ResearchBrief


@pytest.fixture
def sample_brief():
    return ResearchBrief(
        brief_id="brief_test_001",
        topic="Jupiter's Diamond Rain Ocean",
        proposed_title="Why It Rains Solid Diamonds on Jupiter",
        alternative_hooks=[
            "Right now, thousands of miles beneath Jupiter's clouds, solid diamonds are falling like hail.",
            "Deep inside our solar system's largest planet, gemstones liquify into an incandescent ocean.",
            "Astronomers simulated Jupiter's core in a laboratory laser shock experiment, and discovered raining diamonds.",
        ],
        central_question="How does planetary atmospheric pressure transform gas into falling gemstone precipitation?",
        verified_facts=[
            "Atmospheric pressure near Jupiter's interior exceeds 100,000 atmospheres.",
            "Methane (CH4) undergoes thermal pyrolysis under extreme heat and pressure, separating carbon from hydrogen.",
            "Elemental carbon crystallizes into solid diamond particles that sink toward the planet's mantle.",
        ],
        supporting_evidence=[
            FactualEvidence(
                claim="Extreme pressure and laser shockwave tests confirm carbon crystallizes into diamond.",
                source_name="Nature Physics",
                url="https://nature.com",
                verified=True,
            )
        ],
        surprising_revelations=[
            "The diamond hailstones grow to the size of boulders before descending into supercritical liquid hydrogen."
        ],
        suggested_narrative_angle="Scientific awe and extreme physics.",
        backup_topics=[
            BackupTopic(title="Backup", category="science", reason="Test backup")
        ],
    )


def test_scriptwriting_sections_and_timing(sample_brief):
    agent = ScriptwritingAgent(target_duration=80.0)
    script = agent.generate_script(sample_brief)

    assert script.target_duration_seconds == 80.0
    assert len(script.sections) == 6

    # Verify timeline sequence
    assert script.sections[0].timeline_start == 0.0
    assert script.sections[0].timeline_end == 4.0
    assert script.sections[0].role == "HOOK"

    assert script.sections[1].timeline_start == 4.0
    assert script.sections[1].timeline_end == 14.0
    assert script.sections[1].role == "MYSTERY"

    assert script.sections[2].timeline_start == 14.0
    assert script.sections[2].timeline_end == 29.0
    assert script.sections[2].role == "REVELATION"

    assert script.sections[3].timeline_start == 29.0
    assert script.sections[3].timeline_end == 50.0
    assert script.sections[3].role == "ESCALATION"

    assert script.sections[4].timeline_start == 50.0
    assert script.sections[4].timeline_end == 66.0
    assert script.sections[4].role == "CLIMAX"

    assert script.sections[5].timeline_start == 66.0
    assert script.sections[5].timeline_end == 80.0
    assert script.sections[5].role == "PAYOFF"


def test_script_pacing_and_words(sample_brief):
    agent = ScriptwritingAgent(target_duration=80.0)
    script = agent.generate_script(sample_brief)

    # Word count should be around 165–185 words (2.0 to 2.4 wps)
    assert 150 <= script.total_spoken_words <= 195
    assert 1.9 <= script.estimated_reading_speed_wps <= 2.5


def test_script_hygiene_rejects_filler():
    agent = ScriptwritingAgent()
    with pytest.raises(ValueError, match="forbidden filler phrase"):
        agent.validate_script_hygiene("Welcome back guys, today we are talking about black holes.")
