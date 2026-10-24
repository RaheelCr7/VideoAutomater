"""Orchestrator for the 10-Second Beyond 80 Visual Production Quality Test."""

import asyncio
import json
import logging
from pathlib import Path

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

from videoautomater.audio.narrator import AudioNarrator
from videoautomater.models.media import Storyboard, StoryboardScene
from videoautomater.models.research import FactualEvidence, ResearchBrief
from videoautomater.models.script import ScriptSection, StoryScript
from videoautomater.quality.checker import QualityChecker
from videoautomater.rendering.cinematic_motion import CinematicMotionEngine
from videoautomater.rendering.ffmpeg_assembler import FFmpegAssembler
from videoautomater.visuals.subtitles import SubtitleConfig, SubtitleGenerator

logger = logging.getLogger(__name__)


class TenSecondTestRunner:
    """Orchestrates production of the 10-second Beyond 80 visual-first quality test."""

    def __init__(self, output_dir: Path | None = None):
        self.output_dir = output_dir or Path("output/ten_second_test")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.motion_engine = CinematicMotionEngine()
        self.audio_narrator = AudioNarrator()
        self.assembler = FFmpegAssembler()
        self.quality_checker = QualityChecker()

    async def run_quality_test(self) -> Path:
        """Execute the 10-second quality test workflow."""
        logger.info("Starting Beyond 80 10-Second Quality Test (Visual-First Hybrid Architecture)...")

        assets_dir = self.output_dir / "assets"
        assets_dir.mkdir(parents=True, exist_ok=True)

        scene1_img = assets_dir / "scene1_opening.jpg"
        scene2_img = assets_dir / "scene2_shockwave.jpg"
        scene3_img = assets_dir / "scene3_diamond.jpg"

        # 1. Script & Research Brief
        sections = [
            ScriptSection(
                section_id="sec_01",
                timeline_start=0.0,
                timeline_end=5.0,
                role="HOOK",
                narration_text="Deep beneath Jupiter's clouds, atmospheric pressure reaches one hundred thousand atmospheres.",
                visual_intent="Cinematic macroscopic view of Jupiter with approaching probe and subtle 2.5D camera drift.",
            ),
            ScriptSection(
                section_id="sec_02",
                timeline_start=5.0,
                timeline_end=10.0,
                role="PAYOFF",
                narration_text="Crushing heat rips methane molecules apart, forging solid diamond hail.",
                visual_intent="Volumetric shockwave dissociation transforming into ray-traced diamond crystallization with caustics.",
            ),
        ]

        full_text = " ".join(s.narration_text for s in sections)
        script = StoryScript(
            script_id="beyond80_10s_script",
            brief_id="beyond80_brief_01",
            title="Beyond 80: The Quantum Forge of Jupiter",
            selected_hook=sections[0].narration_text,
            alternative_hooks=[
                "Why are diamonds falling inside Jupiter?",
                "What happens to methane under 100,000 atmospheres?",
            ],
            target_duration_seconds=10.0,
            total_spoken_words=len(full_text.split()),
            estimated_reading_speed_wps=round(len(full_text.split()) / 10.0, 2),
            sections=sections,
            full_text=full_text,
        )

        # 2. Synthesize Audio Narration & Soundscape
        narration_wav = self.output_dir / "narration.wav"
        _measured_dur, word_segments = await self.audio_narrator.synthesize_speech(script, narration_wav)

        music_wav = self.output_dir / "ambient_music.wav"
        self.audio_narrator.generate_ambient_music(duration=10.0, output_path=music_wav)

        mixed_audio = self.output_dir / "mixed_audio.aac"
        self.audio_narrator.mix_narration_and_music(
            narration_wav=narration_wav,
            music_wav=music_wav,
            output_mixed_path=mixed_audio,
            target_duration=10.0,
        )

        # 3. Render High-Quality Video Clips using Cinematic Motion Engine
        clips_dir = self.output_dir / "clips"
        clips_dir.mkdir(parents=True, exist_ok=True)

        clip1_mp4 = clips_dir / "clip_01_opening.mp4"
        self.motion_engine.render_cinematic_clip(
            image_path=scene1_img,
            output_mp4=clip1_mp4,
            duration=5.0,
            camera_mode="CINEMATIC_FLOAT",
            branding_badge="BEYOND 80 // ARCHIVE",
            scientific_label="OBSERVATION // JUPITER ATMOSPHERE",
        )

        clip2_mp4 = clips_dir / "clip_02_transformation.mp4"
        self.motion_engine.render_transformation_clip(
            image_a_path=scene2_img,
            image_b_path=scene3_img,
            output_mp4=clip2_mp4,
            duration=5.0,
            branding_badge="BEYOND 80 // QUANTUM SIMULATION",
            scientific_label="PHASE TRANSITION // CH4 -> C (DIAMOND)",
        )

        storyboard = Storyboard(
            storyboard_id="beyond80_10s_storyboard",
            script_id=script.script_id,
            total_duration=10.0,
            scenes=[
                StoryboardScene(
                    scene_id="scene_001",
                    start_time=0.0,
                    end_time=5.0,
                    duration=5.0,
                    asset_type="CINEMATIC_DOCUMENTARY",
                    asset_source="NASA_Juno_Archival_Master",
                    local_file_path=str(clip1_mp4.resolve()),
                    motion_effect="CINEMATIC_FLOAT",
                    overlay_title="OBSERVATION // JUPITER ATMOSPHERE",
                    narration_cue=sections[0].narration_text,
                ),
                StoryboardScene(
                    scene_id="scene_002",
                    start_time=5.0,
                    end_time=10.0,
                    duration=5.0,
                    asset_type="3D_SCIENTIFIC_SIMULATION",
                    asset_source="PBR_Volumetric_Raytracing",
                    local_file_path=str(clip2_mp4.resolve()),
                    motion_effect="SHOCKWAVE_DISSOCIATION_TRANSFORMATION",
                    overlay_title="PHASE TRANSITION // CH4 -> C (DIAMOND)",
                    narration_cue=sections[1].narration_text,
                ),
            ],
        )

        (self.output_dir / "storyboard.json").write_text(
            storyboard.model_dump_json(indent=2), encoding="utf-8"
        )

        # 4. Generate Compact, Word-Synchronized Subtitles (Safe Area Y=1350-1550)
        # Filter segments to 10.0s window
        test_segments = [s for s in word_segments if s.end_time <= 10.5]
        subtitles_ass = self.output_dir / "subtitles.ass"
        subtitles_srt = self.output_dir / "subtitles.srt"
        SubtitleGenerator.generate_ass(test_segments, subtitles_ass)
        SubtitleGenerator.generate_srt(test_segments, subtitles_srt)

        # 5. Master FFmpeg Assembly
        master_mp4 = self.output_dir / "beyond80_10s_test.mp4"
        self.assembler.render_master_video(
            storyboard=storyboard,
            audio_path=mixed_audio,
            subtitles_path=subtitles_ass,
            output_mp4_path=master_mp4,
        )

        # 6. Quality Gate Verification
        quality_report = self.quality_checker.inspect_episode(
            episode_id="beyond80_10s_test",
            video_path=master_mp4,
            script=script,
            subtitles_path=subtitles_ass,
        )
        (self.output_dir / "quality_report.json").write_text(
            quality_report.model_dump_json(indent=2), encoding="utf-8"
        )

        # 7. Extract Frames & Generate Contact Sheet
        self._generate_contact_sheet(master_mp4, self.output_dir / "contact_sheet.jpg")

        logger.info(f"Beyond 80 10-Second Quality Test Completed: {master_mp4}")
        return master_mp4

    def _generate_contact_sheet(self, video_path: Path, output_jpg: Path) -> Path:
        """Extract representative frames showing opening, transformation, and safe captions."""
        ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
        frames_dir = output_jpg.parent / "contact_sheet_frames"
        frames_dir.mkdir(parents=True, exist_ok=True)

        # Extract frames at 1.5s (opening), 3.5s (opening subtitles), 6.5s (shockwave), 8.5s (diamond reveal)
        sample_times = [1.5, 3.5, 6.5, 8.5]
        extracted_images: list[Image.Image] = []

        for idx, ts in enumerate(sample_times):
            frame_path = frames_dir / f"frame_{idx:02d}_{ts:.1f}s.jpg"
            cmd = [
                ffmpeg_bin,
                "-y",
                "-ss",
                str(ts),
                "-i",
                str(video_path.resolve()),
                "-vframes",
                "1",
                "-q:v",
                "2",
                str(frame_path.resolve()),
            ]
            import subprocess
            subprocess.run(cmd, check=True, capture_output=True)
            if frame_path.exists():
                extracted_images.append(Image.open(frame_path))

        if not extracted_images:
            return output_jpg

        grid_w = 1080
        grid_h = 1920
        thumb_w, thumb_h = 540, 960

        contact_sheet = Image.new("RGB", (grid_w, grid_h), (8, 12, 20))
        draw = ImageDraw.Draw(contact_sheet)
        font = ImageFont.load_default()

        labels = [
            "Scene 1: High-Orbit Planetary Approach (Concept A)",
            "Scene 1: Atmospheric Pressure Cue & Safe Subtitles",
            "Scene 2: SLAC Laser Shockwave Dissociation (Concept C)",
            "Scene 2: Crystalline Diamond Reveal & Prismatic Caustics",
        ]

        positions = [(0, 0), (540, 0), (0, 960), (540, 960)]

        for img, pos, lbl in zip(extracted_images, positions, labels):
            thumb = img.resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
            contact_sheet.paste(thumb, pos)
            # Label banner
            draw.rectangle([pos[0] + 10, pos[1] + 20, pos[0] + 520, pos[1] + 60], fill=(0, 0, 0, 200))
            draw.text((pos[0] + 20, pos[1] + 32), lbl, fill=(0, 215, 255), font=font)

        contact_sheet.save(output_jpg, "JPEG", quality=92)
        logger.info(f"Generated quality test contact sheet: {output_jpg}")
        return output_jpg
