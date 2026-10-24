"""Audio narration synthesis and soundscape engineering."""

import logging
import subprocess
from pathlib import Path

import edge_tts
import imageio_ffmpeg
import numpy as np
import soundfile as sf

from videoautomater.config import settings
from videoautomater.models.media import SubtitleSegment, SubtitleWord
from videoautomater.models.script import StoryScript

logger = logging.getLogger(__name__)


class AudioNarrator:
    """Handles neural voiceover generation, word timestamp alignment, and ambient audio mixing."""

    def __init__(self, voice: str | None = None):
        self.voice = voice or settings.tts_voice
        self.ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()

    async def synthesize_speech(
        self,
        script: StoryScript,
        output_wav_path: Path,
    ) -> tuple[float, list[SubtitleSegment]]:
        """Synthesize script text using Edge-TTS and capture word timestamps."""
        output_wav_path.parent.mkdir(parents=True, exist_ok=True)
        temp_mp3 = output_wav_path.with_suffix(".temp.mp3")

        communicate = edge_tts.Communicate(
            text=script.full_text,
            voice=self.voice,
            rate="+0%",
            volume="+0%",
        )

        sentence_events: list[tuple[float, float, str]] = []
        words_data: list[SubtitleWord] = []

        try:
            with open(temp_mp3, "wb") as f:
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        f.write(chunk["data"])
                    elif chunk["type"] == "SentenceBoundary":
                        start_sec = chunk["offset"] / 10_000_000.0
                        dur_sec = chunk["duration"] / 10_000_000.0
                        sentence_events.append((round(start_sec, 3), round(start_sec + dur_sec, 3), chunk["text"]))
                    elif chunk["type"] == "WordBoundary":
                        start_sec = chunk["offset"] / 10_000_000.0
                        dur_sec = chunk["duration"] / 10_000_000.0
                        words_data.append(
                            SubtitleWord(
                                word=chunk["text"],
                                start_time=round(start_sec, 3),
                                end_time=round(start_sec + dur_sec, 3),
                            )
                        )
        except Exception as exc:
            logger.warning(f"Edge-TTS synthesis error: {exc}. Generating programmatic audio fallback.")
            return self._generate_fallback_audio(script, output_wav_path)

        # Convert mp3 to standard 48kHz WAV using FFmpeg
        cmd = [
            self.ffmpeg_bin,
            "-y",
            "-i",
            str(temp_mp3),
            "-ar",
            "48000",
            "-ac",
            "2",
            str(output_wav_path),
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if temp_mp3.exists():
            temp_mp3.unlink()

        # Measure audio duration
        duration = self._get_audio_duration(output_wav_path)

        from videoautomater.visuals.subtitles import SubtitleGenerator
        if sentence_events:
            segments = SubtitleGenerator.segment_transcript(sentence_events)
            logger.info(f"Synthesized neural narration: {duration:.2f}s with {len(sentence_events)} sentences and {len(segments)} short caption segments.")
        else:
            # Fallback to section timings
            section_events = [(sec.timeline_start, sec.timeline_end, sec.narration_text) for sec in script.sections]
            segments = SubtitleGenerator.segment_transcript(section_events)
            logger.info(f"Synthesized narration: {duration:.2f}s with {len(segments)} section-derived caption segments.")

        return duration, segments

    def _get_audio_duration(self, audio_path: Path) -> float:
        """Read duration of an audio file in seconds."""
        info = sf.info(str(audio_path))
        return float(info.duration)

    def _generate_fallback_audio(
        self, script: StoryScript, output_wav_path: Path
    ) -> tuple[float, list[SubtitleSegment]]:
        """Generate offline fallback audio tone bed if network TTS is unavailable."""
        sample_rate = 48000
        duration = 80.0
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        carrier = 0.05 * np.sin(2 * np.pi * 220 * t) + 0.03 * np.sin(2 * np.pi * 440 * t)
        sf.write(str(output_wav_path), carrier, sample_rate)

        from videoautomater.visuals.subtitles import SubtitleGenerator
        section_events = [(sec.timeline_start, sec.timeline_end, sec.narration_text) for sec in script.sections]
        segments = SubtitleGenerator.segment_transcript(section_events)
        return duration, segments

    def generate_ambient_music(self, duration: float, output_path: Path) -> Path:
        """Synthesize a subtle, cinematic space-synth ambient track for background mixing."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        sample_rate = 48000
        total_samples = int(sample_rate * duration)
        t = np.linspace(0, duration, total_samples, endpoint=False)

        # Ambient drone: warm low pad (55Hz A1, 110Hz A2, 165Hz E3 harmonic) with slow modulation
        lfo = 0.5 + 0.5 * np.sin(2 * np.pi * 0.1 * t)
        drone = (
            0.15 * np.sin(2 * np.pi * 55 * t)
            + 0.10 * np.sin(2 * np.pi * 110 * t + 0.2)
            + 0.05 * np.sin(2 * np.pi * 164.81 * t + 0.4) * lfo
        )

        # Soft fade in (2s) and fade out (3s)
        fade_in = np.minimum(1.0, t / 2.0)
        fade_out = np.minimum(1.0, (duration - t) / 3.0)
        ambient_track = drone * fade_in * fade_out

        # Normalize to -22 dB
        max_amp = np.max(np.abs(ambient_track))
        if max_amp > 0:
            target_amp = 10 ** (settings.music_volume_db / 20.0)
            ambient_track = (ambient_track / max_amp) * target_amp

        sf.write(str(output_path), ambient_track, sample_rate)
        return output_path

    def mix_narration_and_music(
        self,
        narration_wav: Path,
        music_wav: Path,
        output_mixed_path: Path,
        target_duration: float = 80.0,
    ) -> Path:
        """Mix voiceover and background music, applying EBU R128 loudness normalization to -14 LUFS."""
        output_mixed_path.parent.mkdir(parents=True, exist_ok=True)

        # Build FFmpeg filtergraph:
        # Pad or trim narration to target_duration, mix with music, apply loudnorm
        filter_complex = (
            f"[0:a]apad=whole_dur={target_duration}[voice];"
            f"[1:a]atrim=0:{target_duration},volume=-6dB[bg];"
            f"[voice][bg]amix=inputs=2:duration=first:dropout_transition=2,"
            f"loudnorm=I={settings.target_lufs}:TP=-1.5:LRA=11[out]"
        )

        cmd = [
            self.ffmpeg_bin,
            "-y",
            "-i",
            str(narration_wav),
            "-i",
            str(music_wav),
            "-filter_complex",
            filter_complex,
            "-map",
            "[out]",
            "-ar",
            "48000",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            str(output_mixed_path),
        ]

        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logger.info(f"Mixed and normalized audio track saved: {output_mixed_path}")
        return output_mixed_path
