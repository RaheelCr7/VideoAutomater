"""Timed subtitle generator for mobile 9:16 vertical video safe zone."""

import logging
from pathlib import Path

from videoautomater.models.media import SubtitleSegment

logger = logging.getLogger(__name__)


class SubtitleGenerator:
    """Produces .srt and .ass subtitles formatted for vertical viewing safe zones."""

    @staticmethod
    def _format_srt_timestamp(seconds: float) -> str:
        """Convert float seconds to SRT time string (00:00:00,000)."""
        hrs = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milli = round((seconds - int(seconds)) * 1000)
        return f"{hrs:02d}:{mins:02d}:{secs:02d},{milli:03d}"

    @classmethod
    def generate_srt(cls, segments: list[SubtitleSegment], output_path: Path) -> Path:
        """Generate standard SubRip (.srt) subtitle file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        lines: list[str] = []

        for idx, seg in enumerate(segments):
            start_str = cls._format_srt_timestamp(seg.start_time)
            end_str = cls._format_srt_timestamp(seg.end_time)
            lines.append(str(idx + 1))
            lines.append(f"{start_str} --> {end_str}")
            lines.append(seg.text)
            lines.append("")

        output_path.write_text("\n".join(lines), encoding="utf-8")
        logger.info(f"Generated SRT subtitles: {len(segments)} segments at {output_path}")
        return output_path

    @classmethod
    def generate_ass(cls, segments: list[SubtitleSegment], output_path: Path) -> Path:
        """Generate styled Advanced SubStation (.ass) subtitle file positioned in bottom-center safe zone."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,52,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,5,2,2,60,60,260,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

        events = []
        for seg in segments:
            start_str = cls._format_ass_timestamp(seg.start_time)
            end_str = cls._format_ass_timestamp(seg.end_time)
            # Text with bold and kinetic yellow accent on key words
            clean_text = seg.text.replace("\n", " ").strip()
            events.append(f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{clean_text}")

        content = header + "\n".join(events) + "\n"
        output_path.write_text(content, encoding="utf-8")
        return output_path

    @staticmethod
    def _format_ass_timestamp(seconds: float) -> str:
        """Convert float seconds to ASS time string (H:MM:SS.cc)."""
        hrs = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        centi = round((seconds - int(seconds)) * 100)
        return f"{hrs}:{mins:02d}:{secs:02d}.{centi:02d}"
