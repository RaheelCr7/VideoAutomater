"""Unit tests for core data models and scoring contracts."""

from videoautomater.models.quality import QualityCheck, QualityReport
from videoautomater.models.research import BackupTopic, FactualEvidence, ResearchBrief, TopicScores
from videoautomater.models.script import ScriptSection, StoryScript


def test_topic_scores_composite_calculation():
    scores = TopicScores(
        curiosity_and_hook=1.0,
        surprise_and_novelty=0.9,
        visual_storytelling=0.8,
        audience_relevance=0.7,
        narrative_depth=0.6,
        freshness_originality=0.5,
    )
    # Expected: (0.25*1.0) + (0.20*0.9) + (0.20*0.8) + (0.15*0.7) + (0.10*0.6) + (0.10*0.5)
    # 0.25 + 0.18 + 0.16 + 0.105 + 0.06 + 0.05 = 0.805
    composite = scores.calculate_composite()
    assert composite == 0.805
    assert scores.composite_score == 0.805


def test_research_brief_validation():
    brief = ResearchBrief(
        brief_id="test_001",
        topic="Jupiter Diamond Rain",
        proposed_title="Why Diamonds Fall From Jupiter's Sky",
        alternative_hooks=[
            "Hook 1: Deep inside Jupiter...",
            "Hook 2: It is raining diamonds...",
            "Hook 3: Laboratory lasers confirmed it..."
        ],
        central_question="How does pressure create diamond precipitation?",
        verified_facts=["Methane separates into carbon and hydrogen."],
        supporting_evidence=[
            FactualEvidence(
                claim="Atmospheric pressure exceeds 100,000 atmospheres",
                source_name="Nature Astronomy",
                url="https://nature.com"
            )
        ],
        suggested_narrative_angle="Scientific awe",
        backup_topics=[
            BackupTopic(title="Topic 2", category="history", reason="Backup candidate")
        ]
    )
    assert brief.topic == "Jupiter Diamond Rain"
    assert len(brief.alternative_hooks) == 3


def test_story_script_duration_and_sections():
    sections = [
        ScriptSection(
            section_id=f"sec_{i}",
            timeline_start=i * 13.33,
            timeline_end=(i + 1) * 13.33,
            role="ROLE",
            narration_text=f"Text for section {i}",
            visual_intent=f"Visual for section {i}"
        )
        for i in range(6)
    ]
    script = StoryScript(
        script_id="script_001",
        brief_id="brief_001",
        title="Test Title",
        selected_hook="Test Hook",
        total_spoken_words=175,
        estimated_reading_speed_wps=2.18,
        sections=sections,
        full_text="Full narration text here."
    )
    assert len(script.sections) == 6
    assert script.target_duration_seconds == 80.0
    assert script.sections[0].duration > 13.0


def test_quality_report_evaluation():
    report = QualityReport(
        report_id="rep_001",
        episode_id="ep_001",
        passed_all_mandatory_checks=True,
        checks=[
            QualityCheck(
                check_name="DURATION",
                required="80.0s",
                measured="79.9s",
                status="PASS"
            )
        ]
    )
    assert report.passed_all_mandatory_checks is True
    assert len(report.checks) == 1
    assert report.checks[0].status == "PASS"
