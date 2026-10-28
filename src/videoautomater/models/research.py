"""Research data contracts and models."""

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class TopicScores(BaseModel):
    """Scoring breakdown across 6 criteria."""
    curiosity_and_hook: float = Field(ge=0.0, le=1.0, description="Curiosity and hook potential (25%)")
    surprise_and_novelty: float = Field(ge=0.0, le=1.0, description="Surprise and novelty (20%)")
    visual_storytelling: float = Field(ge=0.0, le=1.0, description="Visual storytelling potential (20%)")
    audience_relevance: float = Field(ge=0.0, le=1.0, description="Audience relevance and shareability (15%)")
    narrative_depth: float = Field(ge=0.0, le=1.0, description="Narrative depth (10%)")
    freshness_originality: float = Field(ge=0.0, le=1.0, description="Freshness and originality (10%)")
    composite_score: float = Field(default=0.0, ge=0.0, le=1.0)

    def calculate_composite(self) -> float:
        """Calculate weighted composite score based on Section 4 criteria."""
        self.composite_score = round(
            (0.25 * self.curiosity_and_hook) +
            (0.20 * self.surprise_and_novelty) +
            (0.20 * self.visual_storytelling) +
            (0.15 * self.audience_relevance) +
            (0.10 * self.narrative_depth) +
            (0.10 * self.freshness_originality),
            4
        )
        return self.composite_score


class FactualEvidence(BaseModel):
    """Verified supporting factual claim."""
    claim: str
    source_name: str
    url: str
    verified: bool = True
    is_peer_reviewed: bool = True
    publication_type: str = "PEER_REVIEWED_JOURNAL"


class CandidateTopic(BaseModel):
    """Candidate topic evaluated during daily/on-demand discovery."""
    id: str
    title: str
    category: str
    summary: str
    scores: TopicScores
    primary_source_url: str
    supporting_urls: list[str] = Field(default_factory=list)
    factual_verification_status: str = Field(default="UNVERIFIED")  # VERIFIED | UNVERIFIED | REJECTED
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class BackupTopic(BaseModel):
    """Fallback topic brief."""
    title: str
    category: str
    reason: str


class ResearchBrief(BaseModel):
    """Validated structured research brief passed to Scriptwriting Agent."""
    brief_id: str
    topic: str
    proposed_title: str
    headline: str = Field(
        default="",
        description="Hook-first publish title, <= 60 chars, the surprising claim first; no channel prefix",
    )
    alternative_hooks: list[str] = Field(min_length=3, max_length=3)
    central_question: str
    verified_facts: list[str] = Field(min_length=1)
    supporting_evidence: list[FactualEvidence] = Field(min_length=1)
    surprising_revelations: list[str] = Field(default_factory=list)
    suggested_narrative_angle: str
    visual_opportunities: list[str] = Field(default_factory=list)
    content_risks: list[str] = Field(default_factory=list)
    confidence_assessment: float = Field(ge=0.0, le=1.0, default=0.9)
    backup_topics: list[BackupTopic] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
