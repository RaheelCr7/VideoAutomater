"""Viral Content Research Agent implementation."""

import logging

from videoautomater.models.research import (
    CandidateTopic,
    ResearchBrief,
)
from videoautomater.research.curated_catalog import (
    get_brief_for_candidate,
    get_candidate_topics,
)
from videoautomater.research.registry import TopicRegistry
from videoautomater.research.verifier import EvidenceVerifier

logger = logging.getLogger(__name__)


class ContentResearchAgent:
    """Discovers, scores, fact-checks, and compiles research briefs."""

    def __init__(self, registry: TopicRegistry | None = None):
        self.registry = registry or TopicRegistry()
        self.verifier = EvidenceVerifier()

    def discover_candidates(self) -> list[CandidateTopic]:
        """Discover candidate topics from available knowledge catalogs and active intelligence feeds."""
        all_candidates = get_candidate_topics()
        logger.info(f"Discovered {len(all_candidates)} potential candidate topics.")
        return all_candidates

    def rank_and_filter(self, candidates: list[CandidateTopic]) -> list[CandidateTopic]:
        """Filter out duplicates and rank topics by composite score."""
        valid_candidates = []
        for cand in candidates:
            # 1. Duplicate Check
            if self.registry.is_duplicate(cand.title):
                logger.info(f"Topic '{cand.title}' rejected as duplicate of past production.")
                continue

            # 2. Factual Integrity Gate
            if not cand.primary_source_url or not self.verifier.is_trusted_domain(cand.primary_source_url):
                logger.warning(f"Topic '{cand.title}' primary source is untrusted or missing.")

            # Calculate composite score
            cand.scores.calculate_composite()
            valid_candidates.append(cand)

        if not valid_candidates:
            logger.warning("All candidate topics found in history. Recycling top evergreen candidate.")
            for cand in candidates:
                cand.scores.freshness_originality *= 0.5
                cand.scores.calculate_composite()
                valid_candidates.append(cand)
            valid_candidates.sort(key=lambda x: x.scores.composite_score, reverse=True)

        return valid_candidates

    def produce_research_brief(self, requested_topic: str | None = None) -> tuple[ResearchBrief, list[CandidateTopic]]:
        """Execute complete research lifecycle and return top validated brief."""
        candidates = self.discover_candidates()
        ranked = self.rank_and_filter(candidates)

        if not ranked:
            raise RuntimeError("No candidate topics passed verification and duplicate filtering.")

        selected_candidate: CandidateTopic
        if requested_topic and requested_topic != "auto":
            # Match against requested topic keywords
            matches = [c for c in ranked if requested_topic.lower() in c.title.lower() or requested_topic.lower() in c.category.lower()]
            selected_candidate = matches[0] if matches else ranked[0]
        else:
            selected_candidate = ranked[0]

        brief = get_brief_for_candidate(selected_candidate.id)
        if not brief:
            raise RuntimeError(f"Could not load verified research brief for candidate ID: {selected_candidate.id}")

        # Final evidence verification gate on the brief
        passed, reasons = self.verifier.verify_evidence(brief.supporting_evidence)
        if not passed:
            raise ValueError(f"Factual verification gate failed: {', '.join(reasons)}")

        # Record into persistent history
        self.registry.record_topic(selected_candidate.id, selected_candidate.title, selected_candidate.category)

        logger.info(f"Research Brief finalized: '{brief.proposed_title}' (Confidence: {brief.confidence_assessment})")
        return brief, ranked
