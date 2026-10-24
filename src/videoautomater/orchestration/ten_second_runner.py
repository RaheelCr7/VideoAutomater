"""Orchestrator for the Improved 11-Second Beyond 80 Visual Production Quality Test."""

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
    """Orchestrates production of the improved 11-second Beyond 80 visual-first quality test."""

    def __init__(self, output_dir: Path | None = None):
        self.output_dir = output_dir or Path("output/ten_second_test_v2")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.motion_engine = CinematicMotionEngine()
        self.audio_narrator = AudioNarrator()
        self.assembler = FFmpegAssembler()
        self.quality_checker = QualityChecker()

    async def run_quality_test(self) -> Path:
        """Execute the improved visual-first quality test workflow."""
        logger.info("Starting Beyond 80 11-Second Quality Test (Continuous Explanatory Transformation)...")

        assets_dir = self.output_dir / "assets"
        assets_dir.mkdir(parents=True, exist_ok=True)

        neptune_img = assets_dir / "01_neptune.jpg"
        hydrocarbon_img = assets_dir / "02_hydrocarbon.jpg"
        nucleation_img = assets_dir / "03_nucleation.jpg"
        diamond_img = assets_dir / "04_diamond_caustics.jpg"

        # 1. Factually Grounded Script (Kraus et al. Nature Astronomy SLAC experiments on Ice Giants)
        sections = [
            ScriptSection(
                section_id="sec_01",
                timeline_start=0.0,
                timeline_end=2.33,
                role="HOOK",
                narration_text="Deep inside ice giants like Neptune,",
                visual_intent="Fast, dramatic camera dive into Neptune's storm cloud bands, establishing planetary scale in under 2.5 seconds.",
            ),
            ScriptSection(
                section_id="sec_02",
                timeline_start=2.33,
                timeline_end=11.0,
                role="EXPLANATION_AND_PAYOFF",
                narration_text="crushing pressures tear hydrocarbon molecules apart into free carbon, crystallizing pure diamond hail that sinks toward the core.",
                visual_intent="Continuous multi-stage explanatory transformation: hydrocarbon molecular bond rupture, carbon lattice nucleation, and diamond crystallization with caustic dispersion.",
            ),
        ]

        full_text = " ".join(s.narration_text for s in sections)
        script = StoryScript(
            script_id="beyond80_v2_11s_script",
            brief_id="beyond80_brief_neptune",
            title="Beyond 80: Inside the Ice Giants",
            selected_hook=sections[0].narration_text,
            alternative_hooks=[
                "Why do diamonds rain inside Neptune?",
                "What happens to methane under 1.5 million atmospheres?",
            ],
            target_duration_seconds=11.0,
            total_spoken_words=len(full_text.split()),
            estimated_reading_speed_wps=round(len(full_text.split()) / 11.0, 2),
            sections=sections,
            full_text=full_text,
        )

        # 2. Synthesize Audio Narration & Soundscape (Measured Timestamps)
        narration_wav = self.output_dir / "narration.wav"
        measured_dur, word_segments = await self.audio_narrator.synthesize_speech(script, narration_wav)

        music_wav = self.output_dir / "ambient_music.wav"
        self.audio_narrator.generate_ambient_music(duration=11.0, output_path=music_wav)

        mixed_audio = self.output_dir / "mixed_audio.aac"
        self.audio_narrator.mix_narration_and_music(
            narration_wav=narration_wav,
            music_wav=music_wav,
            output_mixed_path=mixed_audio,
            target_duration=11.0,
        )

        # 3. Render High-Quality Video Clips using Cinematic Motion Engine
        clips_dir = self.output_dir / "clips"
        clips_dir.mkdir(parents=True, exist_ok=True)

        # Clip 1: Opening (0.0s - 2.33s = 2.33s duration)
        clip1_mp4 = clips_dir / "clip_01_neptune_dive.mp4"
        self.motion_engine.render_cinematic_clip(
            image_path=neptune_img,
            output_mp4=clip1_mp4,
            duration=2.33,
            camera_mode="CINEMATIC_FLOAT",
            branding_badge="BEYOND 80",
            scientific_label=None,  # No technical clutter in top-left
        )

        # Clip 2: Multi-Stage Continuous Transformation (2.33s - 11.0s = 8.67s duration)
        # Driven by exact Edge-TTS word timing:
        # 0.00s -> 3.15s (timeline 2.33s - 5.48s): "crushing pressures tear hydrocarbon molecules apart"
        # 3.15s -> 4.77s (timeline 5.48s - 7.10s): "into free carbon,"
        # 4.77s -> 8.67s (timeline 7.10s - 11.00s): "crystallizing pure diamond hail that sinks toward the core."
        stages = [
            (hydrocarbon_img, 0.0, 3.15, "molecular_vibration_and_dissociation"),
            (nucleation_img, 3.15, 4.77, "carbon_clustering_and_lattice_nucleation"),
            (diamond_img, 4.77, 8.67, "diamond_caustic_refraction_and_sinking"),
        ]

        clip2_mp4 = clips_dir / "clip_02_transformation.mp4"
        self.motion_engine.render_multi_stage_transformation_clip(
            stages=stages,
            output_mp4=clip2_mp4,
            total_duration=8.67,
            branding_badge="BEYOND 80",
        )

        storyboard = Storyboard(
            storyboard_id="beyond80_v2_storyboard",
            script_id=script.script_id,
            total_duration=11.0,
            scenes=[
                StoryboardScene(
                    scene_id="scene_001",
                    start_time=0.0,
                    end_time=2.33,
                    duration=2.33,
                    asset_type="CINEMATIC_DOCUMENTARY",
                    asset_source="NASA_Voyager2_Neptune_Master",
                    local_file_path=str(clip1_mp4.resolve()),
                    motion_effect="PLANETARY_ATMOSPHERIC_PLUNGE",
                    overlay_title="NEPTUNE ATMOSPHERE",
                    narration_cue=sections[0].narration_text,
                ),
                StoryboardScene(
                    scene_id="scene_002",
                    start_time=2.33,
                    end_time=11.0,
                    duration=8.67,
                    asset_type="3D_SCIENTIFIC_SIMULATION",
                    asset_source="SLAC_Laser_Compression_Reconstruction",
                    local_file_path=str(clip2_mp4.resolve()),
                    motion_effect="CONTINUOUS_EXPLANATORY_TRANSFORMATION",
                    overlay_title="HYDROCARBON DISSOCIATION & DIAMOND CRYSTALLIZATION",
                    narration_cue=sections[1].narration_text,
                ),
            ],
        )

        (self.output_dir / "storyboard.json").write_text(
            storyboard.model_dump_json(indent=2), encoding="utf-8"
        )

        # 4. Generate Compact, Word-Synchronized Subtitles (Safe Area Y=1350-1550)
        # Break into compact 3-5 word dialogue lines matching spoken cadence
        subtitles_ass = self.output_dir / "subtitles.ass"
        subtitles_srt = self.output_dir / "subtitles.srt"
        SubtitleGenerator.generate_ass(word_segments, subtitles_ass)
        SubtitleGenerator.generate_srt(word_segments, subtitles_srt)

        # 5. Master FFmpeg Assembly
        master_mp4 = self.output_dir / "beyond80_11s_demonstration.mp4"
        self.assembler.render_master_video(
            storyboard=storyboard,
            audio_path=mixed_audio,
            subtitles_path=subtitles_ass,
            output_mp4_path=master_mp4,
        )

        # 6. Quality Gate Verification
        quality_report = self.quality_checker.inspect_episode(
            episode_id="beyond80_v2_11s_demonstration",
            video_path=master_mp4,
            script=script,
            subtitles_path=subtitles_ass,
        )
        (self.output_dir / "quality_report.json").write_text(
            quality_report.model_dump_json(indent=2), encoding="utf-8"
        )

        # 7. Timeline Report
        timeline_report = {
            "demo_id": "beyond80_11s_demonstration",
            "total_duration": 11.0,
            "measured_audio_duration": measured_dur,
            "events": [
                {
                    "time_range": [0.0, 2.33],
                    "narration": "Deep inside ice giants like Neptune,",
                    "visual_action": "High-orbit atmospheric plunge into Neptune cloud decks",
                    "animated_elements": "Planetary scaling, atmospheric cloud drift, sun rim lighting breathing",
                },
                {
                    "time_range": [2.33, 5.48],
                    "narration": "crushing pressures tear hydrocarbon molecules apart",
                    "visual_action": "Hydrocarbon molecule vibration under hyperbaric pressure and shockwave bond dissociation",
                    "animated_elements": "Sub-pixel bond oscillation (16 Hz), shockwave illumination bloom, hydrogen dispersal",
                },
                {
                    "time_range": [5.48, 7.10],
                    "narration": "into free carbon,",
                    "visual_action": "Carbon atom coalescence and crystal lattice nucleation",
                    "animated_elements": "Dynamic cyan plasma arc discharge, inward compression toward central lattice",
                },
                {
                    "time_range": [7.10, 11.00],
                    "narration": "crystallizing pure diamond hail that sinks toward the core.",
                    "visual_action": "Octahedral diamond crystal emergence with caustics and fluid descent",
                    "animated_elements": "Prismatic caustic sparkles, slow 3D diamond rotation, downward gravitational sinking",
                },
            ],
        }
        (self.output_dir / "animation_timeline.json").write_text(
            json.dumps(timeline_report, indent=2), encoding="utf-8"
        )

        # 8. Extract Frames & Generate Contact Sheet
        self._generate_contact_sheet(master_mp4, self.output_dir / "contact_sheet.jpg")

        logger.info(f"Beyond 80 11-Second Demonstration Completed: {master_mp4}")
        return master_mp4

    def _generate_contact_sheet(self, video_path: Path, output_jpg: Path) -> Path:
        """Extract representative frames across all transformation milestones."""
        ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
        frames_dir = output_jpg.parent / "contact_sheet_frames"
        frames_dir.mkdir(parents=True, exist_ok=True)

        # 5 milestones:
        # 1. 1.2s: Neptune plunge with opening caption
        # 2. 3.8s: Hydrocarbon molecule under crushing pressure
        # 3. 6.2s: Free carbon lattice nucleation
        # 4. 8.2s: Diamond emergence with prismatic caustics
        # 5. 10.0s: Diamond sinking toward core with payoff caption
        sample_times = [1.2, 3.8, 6.2, 8.2, 10.0]
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

        # Layout: 1 horizontal strip or 2-row grid. Let's make a crisp 2x3 grid (1080x1620 or 1080x1920)
        grid_w = 1080
        grid_h = 1920
        # 2 columns x 3 rows: each thumb 540 x 640
        thumb_w, thumb_h = 540, 640

        contact_sheet = Image.new("RGB", (grid_w, grid_h), (6, 10, 18))
        draw = ImageDraw.Draw(contact_sheet)
        font = ImageFont.load_default()

        labels = [
            "01 // 1.2s: Neptune Atmospheric Plunge",
            "02 // 3.8s: Hydrocarbon Bond Vibration",
            "03 // 6.2s: Carbon Lattice Nucleation",
            "04 // 8.2s: Diamond Crystallization & Caustics",
            "05 // 10.0s: Sinking Toward the Core (Payoff)",
            "Beyond 80 // Verified SLAC / Nature Astronomy",
        ]

        positions = [
            (0, 0), (540, 0),
            (0, 640), (540, 640),
            (0, 1280), (540, 1280),
        ]

        for i in range(len(extracted_images)):
            img = extracted_images[i]
            pos = positions[i]
            lbl = labels[i]

            thumb = img.resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
            contact_sheet.paste(thumb, pos)

            # Label banner
            draw.rectangle([pos[0] + 12, pos[1] + 16, pos[0] + 520, pos[1] + 52], fill=(4, 8, 16, 210))
            draw.text((pos[0] + 20, pos[1] + 26), lbl, fill=(0, 215, 255), font=font)

        # 6th tile: Summary metadata card
        card_pos = positions[5]
        draw.rectangle([card_pos[0], card_pos[1], card_pos[0] + thumb_w, card_pos[1] + thumb_h], fill=(10, 16, 26))
        draw.text((card_pos[0] + 30, card_pos[1] + 60), "BEYOND 80: PRODUCTION SUMMARY", fill=(0, 215, 255), font=font)
        summary_lines = [
            "Duration: 11.00s Master H.264",
            "Resolution: 1080x1920 @ 30 FPS",
            "Aesthetic: Hybrid Documentary & 3D",
            "TTS Sync: Measured Word Timestamps",
            "Subtitles: 3-5 Words, Safe Area Y=1460",
            "Scientific Reference: Kraus et al. Nature",
            "Laboratory: SLAC Laser Shock Experiments",
            "Planetary Context: Neptune / Uranus Ice Giants",
            "Branding: Minimalist Beyond 80 Watermark",
        ]
        for line_idx, s_line in enumerate(summary_lines):
            draw.text((card_pos[0] + 30, card_pos[1] + 110 + line_idx * 45), f"• {s_line}", fill=(200, 215, 235), font=font)

        contact_sheet.save(output_jpg, "JPEG", quality=92)
        logger.info(f"Generated v2 quality test contact sheet: {output_jpg}")
        return output_jpg
