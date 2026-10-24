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
    """Editorial content evaluation scores (1-10)."""
    hook_strength: float = Field(ge=1.0, le=10.0, default=8.5)
    pacing_score: float = Field(ge=1.0, le=10.0, default=8.5)
    narrative_payoff: float = Field(ge=1.0, le=10.0, default=8.5)


class QualityReport(BaseModel):
    """Comprehensive episode quality sign-off report."""
    report_id: str
    episode_id: str
    passed_all_mandatory_checks: bool
    checks: list[QualityCheck] = Field(default_factory=list)
    content_rating: ContentRating = Field(default_factory=ContentRating)
    reviewed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
