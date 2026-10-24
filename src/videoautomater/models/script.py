"""Scriptwriting data models and structures."""


from pydantic import BaseModel, Field


class ScriptSection(BaseModel):
    """Section of an 80-second narrative arc."""
    section_id: str
    timeline_start: float = Field(ge=0.0)
    timeline_end: float = Field(gt=0.0)
    role: str = Field(description="HOOK | MYSTERY | REVELATION | ESCALATION | CLIMAX | PAYOFF")
    narration_text: str
    visual_intent: str

    @property
    def duration(self) -> float:
        return round(self.timeline_end - self.timeline_start, 2)


class StoryScript(BaseModel):
    """Validated 80-second story script."""
    script_id: str
    brief_id: str
    title: str
    selected_hook: str
    alternative_hooks: list[str] = Field(default_factory=list)
    target_duration_seconds: float = Field(default=80.0)
    total_spoken_words: int
    estimated_reading_speed_wps: float = Field(description="Target 2.1 - 2.3 words/second")
    sections: list[ScriptSection] = Field(min_length=1)
    full_text: str
