"""Configuration settings for VideoAutomater."""

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()


class Settings(BaseModel):
    """Global configuration settings."""

    # Project directories
    project_root: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent.parent)
    output_dir: Path = Field(default_factory=lambda: Path(os.getenv("OUTPUT_DIR", "output")))

    # AI Model Settings
    gemini_api_key: str = Field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    gemini_model: str = Field(default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-1.5-flash"))

    # Video Production Specifications
    default_duration: float = Field(default=80.0)
    duration_tolerance: float = Field(default=2.0)
    width: int = Field(default=1080)
    height: int = Field(default=1920)
    fps: int = Field(default=30)
    video_codec: str = Field(default="libx264")
    audio_codec: str = Field(default="aac")
    target_lufs: float = Field(default=-14.0)
    lufs_tolerance: float = Field(default=2.0)

    # Audio & Narration
    tts_voice: str = Field(default_factory=lambda: os.getenv("TTS_VOICE", "en-US-ChristopherNeural"))
    music_volume_db: float = Field(default=-22.0)

    # Execution & Scheduling
    timezone: str = Field(default_factory=lambda: os.getenv("APP_TIMEZONE", "Asia/Karachi"))
    default_review_policy: str = Field(default_factory=lambda: os.getenv("DEFAULT_REVIEW_POLICY", "OPTIONAL_REVIEW"))


settings = Settings()
