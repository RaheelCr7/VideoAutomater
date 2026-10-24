"""Integration tests for narration-driven scene timing and input-hash invalidation."""

import pytest
from pathlib import Path

from videoautomater.content.agent import ScriptwritingAgent
from videoautomater.models.media import SubtitleWord
from videoautomater.models.research import FactualEvidence, ResearchBrief
from videoautomater.orchestration.pilot_runner import PilotRunner


def get_mock_brief() -> ResearchBrief:
    return ResearchBrief(
        brief_id="brief_test_neptune",
        topic="neptune_diamonds",
        proposed_title="The Secret Inside the Ice Giants",
        alternative_hooks=[
            "Deep inside icy planets like Neptune, laboratory physics suggests an astonishing possibility: carbon atoms separating to rain as solid diamonds.",
            "Why does Neptune radiate approximately two point six times more heat than it absorbs from the distant Sun?",
            "How did laser shock experiments at SLAC reveal the extreme physics of giant icy worlds?",
        ],
        central_question="Could theoretically modeled diamond precipitation contribute to Neptune's anomalous internal heat balance?",
        verified_facts=[
            "Voyager 2 measured Neptune's emitted-to-absorbed energy ratio to be ~2.61 (Pearl & Conrath 1991).",
            "SLAC LCLS laser shock experiments (Kraus et al. 2017) demonstrated diamond diffraction at 150 GPa.",
        ],
        supporting_evidence=[
            FactualEvidence(
                claim="Kraus et al. observed diamond formation under 150 GPa laser shock compression.",
                source_name="Nature Astronomy",
                url="https://doi.org/10.1038/s41550-017-0219-9",
                verified=True,
            )
        ],
        surprising_revelations=["Extreme shock compression transforms hydrocarbon plastic into nanodiamonds."],
        suggested_narrative_angle="Solve the Voyager 2 heat balance puzzle through SLAC laser shock physics.",
        visual_opportunities=["Atmospheric plunge", "Laser shockwave", "Octahedral diamond"],
        content_risks=["Distinguish laboratory results from planetary models."],
        confidence_assessment=0.99,
    )


def test_narration_driven_timing_alignment():
    """Verify that script section boundaries match measured speech sentence boundaries."""
    brief = get_mock_brief()
    agent = ScriptwritingAgent(target_duration=80.0)
    script = agent.generate_script(brief)

    assert len(script.sections) == 6

    # Simulated realistic sentence boundaries from Edge-TTS (total 77.4s speech)
    mock_sentences = [
        (0.10, 4.35, script.sections[0].narration_text),
        (4.40, 15.10, script.sections[1].narration_text),
        (15.20, 31.05, script.sections[2].narration_text),
        (31.10, 52.40, script.sections[3].narration_text),
        (52.50, 67.80, script.sections[4].narration_text),
        (67.90, 77.40, script.sections[5].narration_text),
    ]

    script.align_with_narration_timing(mock_sentences)

    assert script.sections[0].timeline_start == 0.10
    assert script.sections[0].timeline_end == 4.35
    assert script.sections[1].timeline_start == 4.40
    assert script.sections[1].timeline_end == 15.10
    assert script.sections[2].timeline_start == 15.20
    assert script.sections[2].timeline_end == 31.05
    assert script.sections[3].timeline_start == 31.10
    assert script.sections[3].timeline_end == 52.40
    assert script.sections[4].timeline_start == 52.50
    assert script.sections[4].timeline_end == 67.80
    assert script.sections[5].timeline_start == 67.90
    assert script.sections[5].timeline_end == 77.40

    # Ensure all durations are positive and monotonic
    for i in range(len(script.sections)):
        assert script.sections[i].duration > 0
        if i > 0:
            assert script.sections[i].timeline_start >= script.sections[i - 1].timeline_end - 0.05


def test_input_hash_invalidation_on_change(tmp_path):
    """Verify that any modification to script or asset invalidates the fingerprint hash."""
    brief = get_mock_brief()
    agent = ScriptwritingAgent(target_duration=80.0)
    script1 = agent.generate_script(brief)

    runner = PilotRunner(output_dir=tmp_path)

    # Create dummy assets
    assets = {}
    for k in ["01_hook", "02_voyager", "03a_hydrocarbon"]:
        p = tmp_path / f"{k}.jpg"
        p.write_bytes(b"image_bytes_v1_" + k.encode())
        assets[k] = p

    hash1 = runner.compute_production_input_hash(script1, assets)

    # Change asset content -> hash must change
    assets["01_hook"].write_bytes(b"modified_image_bytes")
    hash2 = runner.compute_production_input_hash(script1, assets)
    assert hash1 != hash2

    # Change script text -> hash must change
    script2 = agent.generate_script(brief)
    script2.full_text += " Extra changed word."
    hash3 = runner.compute_production_input_hash(script2, assets)
    assert hash2 != hash3
