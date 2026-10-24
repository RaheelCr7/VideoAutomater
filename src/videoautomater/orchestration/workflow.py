"""Production Workflow Orchestrator."""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from videoautomater.audio.narrator import AudioNarrator
from videoautomater.config import settings
from videoautomater.content.agent import ScriptwritingAgent
from videoautomater.models.quality import QualityReport
from videoautomater.quality.checker import QualityChecker
from videoautomater.rendering.ffmpeg_assembler import FFmpegAssembler
from videoautomater.research.agent import ContentResearchAgent
from videoautomater.research.registry import TopicRegistry
from videoautomater.visuals.generator import VisualAssetGenerator
from videoautomater.visuals.subtitles import SubtitleGenerator

logger = logging.getLogger(__name__)


class ProductionOrchestrator:
    """Coordinates runtime agents through the end-to-end video creation pipeline."""

    def __init__(self, output_root: Path | None = None):
        self.output_root = output_root or settings.output_dir
        self.research_agent = ContentResearchAgent(
            registry=TopicRegistry(storage_path=self.output_root / "topic_history.json")
        )
        self.script_agent = ScriptwritingAgent()
        self.audio_narrator = AudioNarrator()
        self.visual_generator = VisualAssetGenerator()
        self.assembler = FFmpegAssembler()
        self.quality_checker = QualityChecker()

    def _get_next_episode_dir(self) -> Path:
        """Create and return the next sequential episode directory (e.g. output/episode_001)."""
        self.output_root.mkdir(parents=True, exist_ok=True)
        existing = [d for d in self.output_root.iterdir() if d.is_dir() and d.name.startswith("episode_")]
        next_num = len(existing) + 1
        ep_dir = self.output_root / f"episode_{next_num:03d}"
        ep_dir.mkdir(parents=True, exist_ok=True)
        return ep_dir

    async def generate_episode(
        self,
        duration: float = 80.0,
        topic: str = "auto",
        episode_dir: Path | None = None,
    ) -> tuple[Path, QualityReport]:
        """Execute full production workflow and generate all episode artifacts."""
        ep_dir = episode_dir or self._get_next_episode_dir()
        ep_dir.mkdir(parents=True, exist_ok=True)
        episode_id = ep_dir.name
        logger.info(f"Starting production for {episode_id} (Duration: {duration}s, Topic: {topic})")

        # -------------------------------------------------------------
        # 1. VIRAL CONTENT RESEARCH AGENT
        # -------------------------------------------------------------
        logger.info("Executing Phase 1: Content Research & Fact Verification...")
        brief, all_candidates = self.research_agent.produce_research_brief(requested_topic=topic)

        # Save research.json, content_brief.json, sources.json
        research_file = ep_dir / "research.json"
        research_file.write_text(
            json.dumps({"candidates": [c.model_dump(mode="json") for c in all_candidates]}, indent=2),
            encoding="utf-8",
        )

        content_brief_file = ep_dir / "content_brief.json"
        content_brief_file.write_text(brief.model_dump_json(indent=2), encoding="utf-8")

        sources_file = ep_dir / "sources.json"
        sources_file.write_text(
            json.dumps(
                {
                    "primary_topic": brief.topic,
                    "evidence": [e.model_dump(mode="json") for e in brief.supporting_evidence],
                    "verified_at": datetime.now(timezone.utc).isoformat(),
                },
                indent=2,
            ),
            encoding="utf-8",
        )

        # -------------------------------------------------------------
        # 2. CREATIVE SCRIPTWRITING AGENT
        # -------------------------------------------------------------
        logger.info("Executing Phase 2: Creative 80-Second Story Scriptwriting...")
        script = self.script_agent.generate_script(brief)

        script_file = ep_dir / "script.json"
        script_file.write_text(script.model_dump_json(indent=2), encoding="utf-8")

        # -------------------------------------------------------------
        # 3. AUDIO & NARRATION ENGINE
        # -------------------------------------------------------------
        logger.info("Executing Phase 3: Neural Voiceover Narration & Soundscape...")
        narration_wav = ep_dir / "narration.wav"
        _measured_dur, word_segments = await self.audio_narrator.synthesize_speech(script, narration_wav)

        ambient_music_wav = ep_dir / "ambient_music.wav"
        self.audio_narrator.generate_ambient_music(duration=duration, output_path=ambient_music_wav)

        mixed_audio_aac = ep_dir / "mixed_audio.aac"
        self.audio_narrator.mix_narration_and_music(
            narration_wav=narration_wav,
            music_wav=ambient_music_wav,
            output_mixed_path=mixed_audio_aac,
            target_duration=duration,
        )

        # -------------------------------------------------------------
        # 4. STORYBOARD & VISUALS ENGINE
        # -------------------------------------------------------------
        logger.info("Executing Phase 4: Storyboard Compilation & Canvas Synthesis...")
        assets_dir = ep_dir / "assets"
        storyboard = self.visual_generator.compile_storyboard(script, assets_dir, target_duration=duration)

        storyboard_file = ep_dir / "storyboard.json"
        storyboard_file.write_text(storyboard.model_dump_json(indent=2), encoding="utf-8")

        # Subtitles (SRT and ASS safe zone)
        subtitles_srt = ep_dir / "subtitles.srt"
        SubtitleGenerator.generate_srt(word_segments, subtitles_srt)

        subtitles_ass = ep_dir / "subtitles.ass"
        SubtitleGenerator.generate_ass(word_segments, subtitles_ass)

        # -------------------------------------------------------------
        # 5. FFMPEG MASTER VIDEO ASSEMBLY
        # -------------------------------------------------------------
        logger.info("Executing Phase 5: FFmpeg Master MP4 Assembly (1080x1920, 30fps)...")
        final_mp4 = ep_dir / "final.mp4"
        self.assembler.render_master_video(
            storyboard=storyboard,
            audio_path=mixed_audio_aac,
            subtitles_path=subtitles_ass,
            output_mp4_path=final_mp4,
        )

        # -------------------------------------------------------------
        # 6. EDITORIAL QUALITY VALIDATION
        # -------------------------------------------------------------
        logger.info("Executing Phase 6: Editorial Quality & Technical Verification...")
        quality_report = self.quality_checker.inspect_episode(episode_id, final_mp4)

        quality_file = ep_dir / "quality_report.json"
        quality_file.write_text(quality_report.model_dump_json(indent=2), encoding="utf-8")

        # -------------------------------------------------------------
        # 7. METADATA & FINAL PACKAGING
        # -------------------------------------------------------------
        metadata_file = ep_dir / "metadata.json"
        metadata = {
            "episode_id": episode_id,
            "title": brief.proposed_title,
            "topic": brief.topic,
            "duration": duration,
            "resolution": "1080x1920",
            "aspect_ratio": "9:16",
            "fps": settings.fps,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "passed_quality_checks": quality_report.passed_all_mandatory_checks,
            "files": {
                "research": "research.json",
                "content_brief": "content_brief.json",
                "script": "script.json",
                "storyboard": "storyboard.json",
                "sources": "sources.json",
                "narration": "narration.wav",
                "subtitles": "subtitles.srt",
                "final_video": "final.mp4",
                "metadata": "metadata.json",
                "quality_report": "quality_report.json",
            },
        }
        metadata_file.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

        logger.info(f"Production completed for {episode_id}! Master video: {final_mp4}")
        return final_mp4, quality_report
