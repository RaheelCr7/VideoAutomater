"""Media and rendering data models."""


from pydantic import BaseModel, Field


class SubtitleWord(BaseModel):
    """Word-level timing information."""
    word: str
    start_time: float
    end_time: float
    confidence: float = 1.0


class SubtitleSegment(BaseModel):
    """Sentence or phrase level timed subtitle."""
    index: int
    start_time: float
    end_time: float
    text: str
    words: list[SubtitleWord] = Field(default_factory=list)


class StoryboardScene(BaseModel):
    """Individual scene within the 80-second storyboard."""
    scene_id: str
    start_time: float
    end_time: float
    duration: float
    asset_type: str = Field(default="SYNTHETIC_CANVAS")  # SYNTHETIC_CANVAS | LICENSED_IMAGE | MOTION_GRAPHIC
    asset_source: str = Field(default="programmatic_render")
    local_file_path: str
    motion_effect: str = Field(default="KEN_BURNS_ZOOM_IN")  # KEN_BURNS_ZOOM_IN | PAN_LEFT | PAN_RIGHT | PULSE
    transition_in: str = Field(default="FADE")
    transition_duration: float = Field(default=0.3)
    overlay_title: str
    overlay_subtitle: str | None = None
    narration_cue: str


class Storyboard(BaseModel):
    """Complete storyboard assembling all visual scenes."""
    storyboard_id: str
    script_id: str
    total_duration: float = 80.0
    scenes: list[StoryboardScene] = Field(default_factory=list)
