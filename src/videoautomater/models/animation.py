"""Animation Director data contracts and structured motion specifications."""

from enum import Enum
from pydantic import BaseModel, Field


class VisualType(str, Enum):
    """Categorization of explanatory and cinematic visuals."""
    CINEMATIC_ESTABLISHING = "CINEMATIC_ESTABLISHING"
    EXPLANATORY_PROCESS = "EXPLANATORY_PROCESS"
    STRUCTURAL_TRANSFORMATION = "STRUCTURAL_TRANSFORMATION"
    SCIENTIFIC_CROSS_SECTION = "SCIENTIFIC_CROSS_SECTION"
    DYNAMIC_SCALE_COMPARISON = "DYNAMIC_SCALE_COMPARISON"
    DOCUMENTARY_MOTION = "DOCUMENTARY_MOTION"


class CameraMotion(BaseModel):
    """Camera movement and framing kinematics."""
    movement_type: str = Field(description="PAN | DOLLY_ZOOM | ORBIT | TRACKING | STATIC", default="DOLLY_ZOOM")
    start_zoom: float = Field(default=1.0)
    end_zoom: float = Field(default=1.15)
    focal_x: float = Field(default=540.0)
    focal_y: float = Field(default=960.0)
    pan_dx: float = Field(default=0.0)
    pan_dy: float = Field(default=0.0)


class AnimationObject(BaseModel):
    """A visual entity participating in the explanatory motion."""
    object_id: str
    name: str
    role: str = Field(description="PRIMARY_SUBJECT | SECONDARY_INDICATOR | BACKGROUND_CONTEXT")
    initial_scale: float = Field(default=1.0)
    target_scale: float = Field(default=1.0)
    initial_alpha: float = Field(default=1.0)
    target_alpha: float = Field(default=1.0)
    position: tuple[float, float] = Field(default=(540.0, 700.0), description="(x, y) coordinates on 1080x1920 canvas")
    color: str = "#00D7FF"


class AnimationEvent(BaseModel):
    """Time-indexed visual action synchronized with narration words."""
    event_id: str
    start_time: float
    end_time: float
    trigger_words: str
    action: str = Field(description="APPROACH | COMPRESS | DISSOCIATE | CRYSTALIZE | PRECIPITATE | HIGHLIGHT")
    target_object_id: str
    description: str
    parameters: dict[str, float | str] = Field(default_factory=dict)


class OnScreenLabel(BaseModel):
    """Scientific or measurement label placed outside subtitle safe zone."""
    label_id: str
    text: str
    position: tuple[float, float] = Field(description="(x, y) coordinates, safe area Y <= 1300 or >= 1600")
    start_time: float
    end_time: float
    font_size: int = 36
    color: str = "#E0E6ED"


class SceneAnimationSpec(BaseModel):
    """Validated machine-readable animation specification for a single scene."""
    scene_id: str
    section_role: str
    narration_text: str
    start_time: float
    end_time: float
    visual_type: VisualType
    visual_objective: str
    scientific_concept: str
    camera: CameraMotion = Field(default_factory=CameraMotion)
    objects: list[AnimationObject] = Field(default_factory=list)
    events: list[AnimationEvent] = Field(default_factory=list)
    labels: list[OnScreenLabel] = Field(default_factory=list)
    subtitle_safe_zone_y: tuple[int, int] = Field(default=(1350, 1550))
    template_name: str

    @property
    def duration(self) -> float:
        return max(0.0, round(self.end_time - self.start_time, 3))


class MasterAnimationPlan(BaseModel):
    """Complete episodic animation production plan compiled by AnimationDirectorAgent."""
    plan_id: str
    topic: str
    total_duration: float
    scenes: list[SceneAnimationSpec] = Field(min_length=1)
