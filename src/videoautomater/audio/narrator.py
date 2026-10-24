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


class SpeechSynthesisResult(tuple):
    """Backwards-compatible tuple (duration, segments) with sentence, word boundary, and sync type attributes."""
    duration: float
    segments: list[SubtitleSegment]
    sentence_events: list[tuple[float, float, str]]
    words: list[SubtitleWord]
    synchronization_type: str

    def __new__(
        cls,
        duration: float,
        segments: list[SubtitleSegment],
        sentence_events: list[tuple[float, float, str]],
        words: list[SubtitleWord],
        synchronization_type: str = "NEURAL_TTS_WORD_BOUNDARIES",
    ):
        obj = super().__new__(cls, (duration, segments))
        obj.duration = duration
        obj.segments = segments
        obj.sentence_events = sentence_events
        obj.words = words
        obj.synchronization_type = synchronization_type
        return obj


class AudioNarrator:
    """Handles neural voiceover generation, word timestamp alignment, and ambient audio mixing."""

    def __init__(self, voice: str | None = None):
        self.voice = voice or settings.tts_voice
        self.ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()

    async def synthesize_speech(
        self,
        script: StoryScript,
        output_wav_path: Path,
        rate: str | None = None,
    ) -> SpeechSynthesisResult:
        """Synthesize script text using Edge-TTS with authentic word-boundary timestamps."""
        output_wav_path.parent.mkdir(parents=True, exist_ok=True)
        temp_mp3 = output_wav_path.with_suffix(".temp.mp3")

        speech_rate = rate or ("+11%" if script.total_spoken_words > 140 else "+0%")
        communicate = edge_tts.Communicate(
            text=script.full_text,
            voice=self.voice,
            rate=speech_rate,
            volume="+0%",
            boundary="WordBoundary",
        )

        words_data: list[SubtitleWord] = []

        try:
            with open(temp_mp3, "wb") as f:
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        f.write(chunk["data"])
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

        sentence_events: list[tuple[float, float, str]] = []
        if words_data:
            # Map section boundaries directly to exact spoken word spans
            curr_w_idx = 0
            for sec in script.sections:
                sec_words = [w for w in sec.narration_text.split() if w.strip()]
                w_count = len(sec_words)
                if curr_w_idx < len(words_data):
                    s_start = words_data[curr_w_idx].start_time
                    end_idx = min(curr_w_idx + w_count - 1, len(words_data) - 1)
                    s_end = words_data[end_idx].end_time
                    sentence_events.append((s_start, s_end, sec.narration_text))
                    curr_w_idx = end_idx + 1

            # Build subtitle segments directly from real TTS word boundaries
            segments = SubtitleGenerator.segment_words(words_data)
            sync_type = "NEURAL_TTS_WORD_BOUNDARIES"
            logger.info(
                f"Synthesized neural narration with real word boundaries: {duration:.2f}s, "
                f"{len(words_data)} words, {len(segments)} segments."
            )
        else:
            # Pacing estimation fallback
            section_events = [(sec.timeline_start, sec.timeline_end, sec.narration_text) for sec in script.sections]
            segments = SubtitleGenerator.segment_transcript(section_events)
            sentence_events = section_events
            sync_type = "ESTIMATED_OFFLINE_FALLBACK"
            logger.warning("No TTS word boundaries emitted. Used estimated pacing fallback.")

        return SpeechSynthesisResult(duration, segments, sentence_events, words_data, sync_type)

    def _get_audio_duration(self, audio_path: Path) -> float:
        """Read duration of an audio file in seconds."""
        info = sf.info(str(audio_path))
        return float(info.duration)

    def _generate_fallback_audio(
        self, script: StoryScript, output_wav_path: Path
    ) -> SpeechSynthesisResult:
        """Generate offline fallback audio tone bed if network TTS is unavailable."""
        sample_rate = 48000
        duration = 80.0
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        carrier = 0.05 * np.sin(2 * np.pi * 220 * t) + 0.03 * np.sin(2 * np.pi * 440 * t)
        sf.write(str(output_wav_path), carrier, sample_rate)

        from videoautomater.visuals.subtitles import SubtitleGenerator
        section_events = [(sec.timeline_start, sec.timeline_end, sec.narration_text) for sec in script.sections]
        segments = SubtitleGenerator.segment_transcript(section_events)
        words_fallback: list[SubtitleWord] = []
        return SpeechSynthesisResult(duration, segments, section_events, words_fallback)

    def generate_ambient_music(self, duration: float, output_path: Path) -> Path:
        """Synthesize a rich, cinematic ambient documentary soundscape with harmonic resolution outro."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        sample_rate = 48000
        total_samples = int(sample_rate * duration)
        t = np.linspace(0, duration, total_samples, endpoint=False)

        # 1. Low cinematic drone (A1: 55Hz, A2: 110Hz, E3: 164.81Hz) with slow breathing LFO
        lfo_slow = 0.5 + 0.5 * np.sin(2 * np.pi * 0.08 * t)
        lfo_mid = 0.5 + 0.5 * np.sin(2 * np.pi * 0.15 * t + 0.5)

        drone_low = 0.16 * np.sin(2 * np.pi * 55.0 * t) + 0.11 * np.sin(2 * np.pi * 110.0 * t + 0.2)
        drone_mid = 0.07 * np.sin(2 * np.pi * 164.81 * t + 0.4) * lfo_slow
        drone_high = 0.04 * np.sin(2 * np.pi * 220.0 * t + 0.7) * lfo_mid

        # 2. Celestial shimmering texture (overtone bells modulated)
        shimmer = 0.02 * np.sin(2 * np.pi * 440.0 * t + np.sin(2 * np.pi * 0.5 * t)) * lfo_slow
        sub_bass = 0.12 * np.sin(2 * np.pi * 27.5 * t)  # Sub-audible atmospheric weight (A0: 27.5 Hz)

        full_bed = drone_low + drone_mid + drone_high + shimmer + sub_bass

        # 3. Outro resolution cadence: In the final 8 seconds, swell a warm resolution chord (Aadd9)
        outro_start = max(0.0, duration - 8.0)
        outro_mask = np.clip((t - outro_start) / 4.0, 0.0, 1.0)
        resolution_chord = (
            0.08 * np.sin(2 * np.pi * 110.0 * t)
            + 0.06 * np.sin(2 * np.pi * 164.81 * t)
            + 0.05 * np.sin(2 * np.pi * 220.0 * t)
            + 0.03 * np.sin(2 * np.pi * 277.18 * t)  # C# major 3rd warmth
        ) * outro_mask

        combined = full_bed + resolution_chord

        # 4. Smooth dynamic envelopes: Gentle 1.5s fade-in, and elegant 1.2s cosine fade-out at end
        fade_in = np.minimum(1.0, t / 1.5)
        # Squeeze fade-out only into the final 1.2 seconds so the ending chord resonates
        tail_start = max(0.0, duration - 1.2)
        fade_out = np.where(
            t < tail_start,
            1.0,
            0.5 + 0.5 * np.cos(np.pi * (t - tail_start) / 1.2),
        )

        ambient_track = combined * fade_in * fade_out

        # Normalize to target music level (-20 dB)
        max_amp = np.max(np.abs(ambient_track))
        if max_amp > 0:
            target_amp = 10 ** ((settings.music_volume_db + 2.0) / 20.0)
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
        """Mix voiceover and background music with dynamic sidechain ducking and EBU R128 normalization."""
        output_mixed_path.parent.mkdir(parents=True, exist_ok=True)

        # Dynamic sidechain compression:
        # Music ducks smoothly under active speech and naturally swells up during pauses and outro
        filter_complex = (
            f"[0:a]apad=whole_dur={target_duration}[voice];"
            f"[1:a]atrim=0:{target_duration}[bg_trimmed];"
            f"[bg_trimmed][voice]sidechaincompress=threshold=0.08:ratio=3.5:attack=50:release=350[ducked_bg];"
            f"[voice][ducked_bg]amix=inputs=2:duration=first:dropout_transition=0,"
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
