"""Quality check and report models."""

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class QualityCheck(BaseModel):
    """Result of an individual technical or editorial quality verification."""
    check_name: str
    required: str
    measured: str
    status: str = Field(description="PASS | FAIL | WARNING")
    details: str = ""


class ContentRating(BaseModel):
    """Editorial content evaluation scores (1-10) derived from empirical heuristics."""
    hook_strength: float = Field(ge=1.0, le=10.0, default=7.0)
    pacing_score: float = Field(ge=1.0, le=10.0, default=7.0)
    narrative_payoff: float = Field(ge=1.0, le=10.0, default=7.0)
    methodology: str = "empirical_heuristic"
    evidence: dict[str, str] = Field(default_factory=dict)


class QualityReport(BaseModel):
    """Comprehensive episode quality sign-off report with explicit approval separation."""
    report_id: str
    episode_id: str
    technical_qa_passed: bool = Field(default=False, description="All automated technical audio/video gates pass")
    scientific_qa_passed: bool = Field(default=False, description="Peer-reviewed claim verification passes")
    rights_cleared: bool = Field(default=False, description="Asset provenance and licensing terms verified")
    passed_all_mandatory_checks: bool = Field(default=False, description="Backward-compatible technical gate alias")
    publication_approval_status: str = Field(
        default="PENDING_HUMAN_APPROVAL",
        description="PENDING_HUMAN_APPROVAL | APPROVED_FOR_PUBLICATION | REJECTED",
    )
    publication_authorized: bool = Field(default=False, description="Explicit human release authorization flag")
    checks: list[QualityCheck] = Field(default_factory=list)
    content_rating: ContentRating = Field(default_factory=ContentRating)
    reviewed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
