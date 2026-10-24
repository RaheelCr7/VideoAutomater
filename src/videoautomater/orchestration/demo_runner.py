"""Demonstration Pipeline Runner for 20-Second Explanatory Animation Proof of Concept."""

import asyncio
import json
import logging
from pathlib import Path

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

from videoautomater.agents.animation_director import AnimationDirectorAgent
from videoautomater.audio.narrator import AudioNarrator
from videoautomater.models.media import Storyboard, StoryboardScene
from videoautomater.models.research import FactualEvidence, ResearchBrief
from videoautomater.models.script import ScriptSection, StoryScript
from videoautomater.quality.checker import QualityChecker
from videoautomater.rendering.ffmpeg_assembler import FFmpegAssembler
from videoautomater.visuals.animation_engine import AnimationEngine
from videoautomater.visuals.subtitles import SubtitleConfig, SubtitleGenerator

logger = logging.getLogger(__name__)


class AnimationDemoRunner:
    """Executes end-to-end production of the 20-second cinematic animation proof-of-concept."""

    def __init__(self, output_dir: Path | None = None):
        self.output_dir = output_dir or Path("output/animation_demo")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.anim_director = AnimationDirectorAgent()
        self.anim_engine = AnimationEngine()
        self.audio_narrator = AudioNarrator()
        self.assembler = FFmpegAssembler()
        self.quality_checker = QualityChecker()

    async def run_demonstration(self) -> Path:
        """Run the complete 20-second explanatory animation demonstration."""
        logger.info("Starting 20-second Explanatory Animation Proof of Concept...")

        # 1. Construct 20-Second High-Impact Science Script
        sections = [
            ScriptSection(
                section_id="demo_sec_01",
                timeline_start=0.0,
                timeline_end=4.5,
                role="HOOK",
                narration_text="Beneath Jupiter's outer cloud decks, an impossible planetary phenomenon begins.",
                visual_intent="Wide celestial establishing shot of planet and approaching exploratory probe.",
            ),
            ScriptSection(
                section_id="demo_sec_02",
                timeline_start=4.5,
                timeline_end=10.0,
                role="ESCALATION",
                narration_text="At one hundred thousand atmospheres, crushing pressure and extreme heat compress atmospheric methane.",
                visual_intent="Explanatory depth and pressure gauge with physical gas particle compression waves.",
            ),
            ScriptSection(
                section_id="demo_sec_03",
                timeline_start=10.0,
                timeline_end=15.5,
                role="REVELATION",
                narration_text="Laser shockwaves rip molecular bonds apart, crystallizing free carbon into pure diamond.",
                visual_intent="Molecular dissociation of CH4 bonds snapping into octahedral diamond crystal lattice.",
            ),
            ScriptSection(
                section_id="demo_sec_04",
                timeline_start=15.5,
                timeline_end=20.0,
                role="PAYOFF",
                narration_text="Precipitating downward, solid diamond hail sinks through liquid metallic hydrogen.",
                visual_intent="Precipitating sparkling diamond crystals sinking through mantle with safe-zone subtitles.",
            ),
        ]

        full_text = " ".join(s.narration_text for s in sections)
        script = StoryScript(
            script_id="demo_script_20s",
            brief_id="demo_brief_01",
            title="Jupiter's Diamond Rain: The Quantum Mechanism",
            selected_hook=sections[0].narration_text,
            alternative_hooks=[
                "Why are diamonds falling inside Jupiter?",
                "What happens to methane under 100,000 atmospheres?",
                "How does planetary pressure forge diamonds in mid-air?",
            ],
            target_duration_seconds=20.0,
            total_spoken_words=len(full_text.split()),
            estimated_reading_speed_wps=round(len(full_text.split()) / 20.0, 2),
            sections=sections,
            full_text=full_text,
        )

        brief = ResearchBrief(
            brief_id="demo_brief_01",
            topic="Jupiter's Diamond Rain",
            proposed_title="Jupiter's Diamond Rain",
            alternative_hooks=[
                "Why are diamonds falling inside Jupiter?",
                "What happens to methane under 100,000 atmospheres?",
                "How does planetary pressure forge diamonds in mid-air?",
            ],
            central_question="How does planetary pressure transform methane gas into falling solid diamonds?",
            verified_facts=[
                "At 100,000 atmospheres, methane dissociates into carbon and hydrogen.",
                "Laser shockwave experiments confirmed diamond crystallization at SLAC.",
            ],
            supporting_evidence=[
                FactualEvidence(
                    claim="Extreme pressures inside gas giants dissociate methane into diamond.",
                    source_name="Nature Astronomy (SLAC laser compression experiments)",
                    url="https://www.nature.com/articles/s41550-020-1118-2",
                    verified=True,
                )
            ],
            suggested_narrative_angle="Explain the step-by-step physical transformation from atmospheric gas to falling crystalline diamonds.",
        )

        # 2. Synthesize Voiceover & Mix Soundscape
        narration_wav = self.output_dir / "narration.wav"
        _measured_dur, word_segments = await self.audio_narrator.synthesize_speech(script, narration_wav)

        music_wav = self.output_dir / "ambient_music.wav"
        self.audio_narrator.generate_ambient_music(duration=20.0, output_path=music_wav)

        mixed_audio = self.output_dir / "mixed_audio.aac"
        self.audio_narrator.mix_narration_and_music(
            narration_wav=narration_wav,
            music_wav=music_wav,
            output_mixed_path=mixed_audio,
            target_duration=20.0,
        )

        # 3. AnimationDirectorAgent: Compile Animation Specification
        # For the 4 demonstration scenes
        demo_script = StoryScript(
            script_id="demo_script_20s",
            brief_id="demo_brief_01",
            title="Jupiter's Diamond Rain",
            selected_hook=sections[0].narration_text,
            target_duration_seconds=20.0,
            total_spoken_words=len(full_text.split()),
            estimated_reading_speed_wps=round(len(full_text.split()) / 20.0, 2),
            sections=sections,
            full_text=full_text,
        )
        # We take the 4 target scenes
        full_plan = self.anim_director.compile_animation_plan(demo_script, brief, target_duration=20.0)
        demo_scenes = full_plan.scenes[:4]

        # Fix start/end times precisely to 0-4.5, 4.5-10.0, 10.0-15.5, 15.5-20.0
        timings = [(0.0, 4.5), (4.5, 10.0), (10.0, 15.5), (15.5, 20.0)]
        for i, (st, et) in enumerate(timings):
            demo_scenes[i].start_time = st
            demo_scenes[i].end_time = et

        animation_storyboard_file = self.output_dir / "animation_storyboard.json"
        animation_storyboard_file.write_text(
            json.dumps({"scenes": [s.model_dump(mode="json") for s in demo_scenes]}, indent=2),
            encoding="utf-8",
        )

        # 4. Render 4 Full-Resolution 1080x1920 30FPS Animation MP4 Clips
        clips_dir = self.output_dir / "clips"
        clips_dir.mkdir(parents=True, exist_ok=True)
        rendered_clips: list[Path] = []
        storyboard_scenes: list[StoryboardScene] = []

        for spec in demo_scenes:
            clip_path = clips_dir / f"{spec.scene_id}.mp4"
            self.anim_engine.render_scene_clip(spec, clip_path)
            rendered_clips.append(clip_path)

            storyboard_scenes.append(
                StoryboardScene(
                    scene_id=spec.scene_id,
                    start_time=spec.start_time,
                    end_time=spec.end_time,
                    duration=spec.duration,
                    asset_type="MOTION_GRAPHIC",
                    asset_source="animation_engine",
                    local_file_path=str(clip_path.resolve()),
                    motion_effect=spec.camera.movement_type,
                    overlay_title=spec.scientific_concept,
                    narration_cue=spec.narration_text,
                )
            )

        storyboard = Storyboard(
            storyboard_id="demo_storyboard",
            script_id="demo_script_20s",
            scenes=storyboard_scenes,
            total_duration=20.0,
        )

        # 5. Generate Word-Synchronized ASS Subtitles in Safe Zone
        # Filter word segments to the 20s demonstration window
        demo_segments = [s for s in word_segments if s.end_time <= 20.5]
        subtitles_ass = self.output_dir / "subtitles.ass"
        subtitles_srt = self.output_dir / "subtitles.srt"
        SubtitleGenerator.generate_ass(demo_segments, subtitles_ass)
        SubtitleGenerator.generate_srt(demo_segments, subtitles_srt)

        # Subtitle alignment report
        sub_report = {
            "total_segments": len(demo_segments),
            "max_words_per_segment": max(len(s.text.split()) for s in demo_segments) if demo_segments else 0,
            "safe_zone_y_range": [1350, 1550],
            "margin_v": 460,
            "playres_x": 1080,
            "playres_y": 1920,
            "segments": [
                {
                    "index": s.index,
                    "start": round(s.start_time, 2),
                    "end": round(s.end_time, 2),
                    "words": len(s.text.split()),
                    "text": s.text.replace(r"\N", " "),
                }
                for s in demo_segments
            ],
        }
        (self.output_dir / "subtitle_alignment_report.json").write_text(json.dumps(sub_report, indent=2), encoding="utf-8")

        # 6. Render Master Demo MP4
        demo_final_mp4 = self.output_dir / "animation_demo.mp4"
        self.assembler.render_master_video(
            storyboard=storyboard,
            audio_path=mixed_audio,
            subtitles_path=subtitles_ass,
            output_mp4_path=demo_final_mp4,
        )

        # 7. Timeline Report
        timeline_report = {
            "demo_id": "animation_demo_20s",
            "total_duration": 20.0,
            "resolution": "1080x1920",
            "fps": 30,
            "scenes": [
                {
                    "scene_id": s.scene_id,
                    "start_time": s.start_time,
                    "end_time": s.end_time,
                    "duration": s.duration,
                    "template": s.template_name,
                    "concept": s.scientific_concept,
                    "camera": s.camera.model_dump(mode="json"),
                    "events": [e.model_dump(mode="json") for e in s.events],
                }
                for s in demo_scenes
            ],
        }
        (self.output_dir / "animation_timeline.json").write_text(json.dumps(timeline_report, indent=2), encoding="utf-8")

        # 8. Run Automated Technical & Visual Quality Checker
        quality_report = self.quality_checker.inspect_episode(
            episode_id="animation_demo",
            video_path=demo_final_mp4,
            script=demo_script,
            subtitles_path=subtitles_ass,
        )
        (self.output_dir / "visual_quality_report.json").write_text(
            quality_report.model_dump_json(indent=2), encoding="utf-8"
        )

        # 9. Extract Actual Rendered Frames & Generate Contact Sheet
        self._generate_contact_sheet(demo_final_mp4, self.output_dir / "contact_sheet.jpg")

        logger.info(f"Demonstration run completed: {demo_final_mp4}")
        return demo_final_mp4

    def _generate_contact_sheet(self, video_path: Path, output_jpg: Path) -> Path:
        """Extract representative frames from the final rendered MP4 and stitch into contact sheet."""
        ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
        frames_dir = output_jpg.parent / "contact_sheet_frames"
        frames_dir.mkdir(parents=True, exist_ok=True)

        # Timestamps across the 4 scenes:
        # Scene 1: 2.0s (celestial opening)
        # Scene 2: 7.0s (pressure/depth compression)
        # Scene 3: 13.0s (molecular diamond lattice transformation)
        # Scene 4: 18.0s (diamond precipitation with subtitle overlay)
        sample_times = [2.0, 7.0, 13.0, 18.0]
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

        # Layout 2x2 grid of 540x960 thumbnails
        grid_w = 1080
        grid_h = 1920
        thumb_w, thumb_h = 540, 960

        contact_sheet = Image.new("RGB", (grid_w, grid_h), (12, 16, 24))
        draw = ImageDraw.Draw(contact_sheet)
        font = ImageFont.load_default()

        labels = [
            "Scene 1: Cinematic Opening (Celestial Approach)",
            "Scene 2: Explanatory Process (Pressure & Depth)",
            "Scene 3: Molecular Reveal (Diamond Crystallization)",
            "Scene 4: Scientific Payoff & Safe-Zone Subtitles",
        ]

        positions = [(0, 0), (540, 0), (0, 960), (540, 960)]

        for img, pos, lbl in zip(extracted_images, positions, labels):
            thumb = img.resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
            contact_sheet.paste(thumb, pos)
            # Label overlay
            draw.rectangle([pos[0] + 10, pos[1] + 20, pos[0] + 520, pos[1] + 60], fill=(0, 0, 0, 200))
            draw.text((pos[0] + 20, pos[1] + 32), lbl, fill=(0, 215, 255), font=font)

        contact_sheet.save(output_jpg, "JPEG", quality=92)
        logger.info(f"Generated contact sheet: {output_jpg}")
        return output_jpg
