"""Unit tests for the Viral Content Research Agent."""

import tempfile
from pathlib import Path

from videoautomater.models.research import FactualEvidence
from videoautomater.research.agent import ContentResearchAgent
from videoautomater.research.registry import TopicRegistry
from videoautomater.research.verifier import EvidenceVerifier


def test_registry_duplicate_detection():
    with tempfile.TemporaryDirectory() as tmp_dir:
        history_path = Path(tmp_dir) / "history.json"
        reg = TopicRegistry(storage_path=history_path)

        assert not reg.is_duplicate("Jupiter Diamond Rain Ocean")
        reg.record_topic("001", "Jupiter Diamond Rain Ocean", "space")

        # Exact check
        assert reg.is_duplicate("Jupiter Diamond Rain Ocean")
        # Near duplicate semantic check
        assert reg.is_duplicate("Diamond Rain on Jupiter Planet")
        # Unrelated topic
        assert not reg.is_duplicate("Ancient Greek Computer of Antikythera")


def test_evidence_verifier():
    verifier = EvidenceVerifier()
    assert verifier.is_trusted_domain("https://www.nature.com/articles/123")
    assert verifier.is_trusted_domain("https://nasa.gov/mission/juno")
    assert not verifier.is_trusted_domain("https://random-unverified-blog.xyz/rumors")

    # Valid evidence
    valid_ev = [
        FactualEvidence(
            claim="Laser shock compression turns methane into diamond crystals under pressure.",
            source_name="Nature Physics",
            url="https://nature.com",
            verified=True,
        )
    ]
    passed, errors = verifier.verify_evidence(valid_ev)
    assert passed
    assert len(errors) == 0

    # Invalid evidence (empty claim)
    invalid_ev = [
        FactualEvidence(
            claim="Too short",
            source_name="Unknown",
            url="not-a-url",
            verified=False,
        )
    ]
    passed_inv, errors_inv = verifier.verify_evidence(invalid_ev)
    assert not passed_inv
    assert len(errors_inv) > 0


def test_research_agent_produce_brief():
    with tempfile.TemporaryDirectory() as tmp_dir:
        history_path = Path(tmp_dir) / "test_history.json"
        agent = ContentResearchAgent(registry=TopicRegistry(storage_path=history_path))

        brief, candidates = agent.produce_research_brief(requested_topic="auto")

        assert brief is not None
        assert len(brief.alternative_hooks) == 3
        assert len(brief.verified_facts) >= 1
        assert len(brief.supporting_evidence) >= 1
        assert len(brief.backup_topics) >= 1
        assert brief.confidence_assessment >= 0.8
        assert len(candidates) >= 1

        # Check that topic is now in history
        assert agent.registry.is_duplicate(brief.topic)


def test_verifier_rejects_placeholder_dois_and_generic_templates():
    verifier = EvidenceVerifier()
    # Placeholder DOI
    fake_doi_ev = [
        FactualEvidence(
            claim="Tardigrades survive through extreme cryobiosis mechanisms.",
            source_name="Fake Journal",
            url="https://doi.org/10.1038/s41598-verified",
            verified=True,
        )
    ]
    passed, errors = verifier.verify_evidence(fake_doi_ev)
    assert not passed
    assert any("placeholder" in e.lower() or "fabricated" in e.lower() for e in errors)

    # Generic template phrasing
    template_ev = [
        FactualEvidence(
            claim="Empirical measurements of topic demonstrated quantifiable structural anomalies under rigorous conditions.",
            source_name="Nature",
            url="https://doi.org/10.1038/s41550-017-0219-9",
            verified=True,
        )
    ]
    passed_tpl, errors_tpl = verifier.verify_evidence(template_ev)
    assert not passed_tpl
    assert any("generic" in e.lower() or "template" in e.lower() for e in errors_tpl)


def test_research_agent_fails_on_unverifiable_gibberish_topic():
    from videoautomater.research.scholarly_retriever import ResearchVerificationError
    with tempfile.TemporaryDirectory() as tmp_dir:
        agent = ContentResearchAgent(registry=TopicRegistry(storage_path=Path(tmp_dir) / "test.json"))
        import pytest
        with pytest.raises(ResearchVerificationError):
            agent.produce_research_brief(requested_topic="xyzq123_nonexistent_pseudoscience_topic_999999")
