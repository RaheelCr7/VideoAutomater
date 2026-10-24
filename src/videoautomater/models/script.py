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

    def align_with_narration_timing(self, sentence_events: list[tuple[float, float, str]]) -> None:
        """Align section start/end timeline boundaries directly to measured audio sentence timings."""
        if not sentence_events or not self.sections:
            return
        if len(sentence_events) == len(self.sections):
            for i, sec in enumerate(self.sections):
                st, et, _ = sentence_events[i]
                sec.timeline_start = round(st, 3)
                sec.timeline_end = round(et, 3)
        else:
            # Group sentence events by text matching or proportional word lengths
            curr_s = 0
            for sec in self.sections:
                sec_words = len(sec.narration_text.split())
                matched_start = sentence_events[curr_s][0] if curr_s < len(sentence_events) else 0.0
                matched_end = matched_start
                accum_words = 0
                while curr_s < len(sentence_events):
                    s_st, s_et, s_txt = sentence_events[curr_s]
                    accum_words += len(s_txt.split())
                    matched_end = s_et
                    curr_s += 1
                    if accum_words >= sec_words - 2 or curr_s == len(sentence_events):
                        break
                sec.timeline_start = round(matched_start, 3)
                sec.timeline_end = round(matched_end, 3)
