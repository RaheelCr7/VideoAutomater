"""Professional short-form documentary subtitle generator and safe zone layout engine."""

import logging
import re
from dataclasses import dataclass
from pathlib import Path

from videoautomater.models.media import SubtitleSegment, SubtitleWord

logger = logging.getLogger(__name__)

STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for", "of",
    "with", "by", "from", "as", "is", "was", "were", "are", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "it", "its", "this", "that", "these",
    "those", "they", "them", "their", "we", "us", "our", "you", "your", "he", "him",
    "his", "she", "her", "so", "than", "too", "very", "can", "will", "just", "into",
}


@dataclass
class SubtitleConfig:
    """Configuration for vertical video captions."""
    font_name: str = "Arial"
    font_size: int = 54
    primary_color: str = "&H00FFFFFF&"      # Crisp white
    outline_color: str = "&H00000000&"      # Deep black outline
    highlight_color: str = "&H00D7FF&"     # Documentary warm gold/yellow accent
    outline_width: int = 3
    shadow_depth: int = 1
    safe_zone_y_min: int = 1350             # Top boundary of lower-middle safe zone
    safe_zone_y_max: int = 1550             # Bottom boundary of safe zone
    margin_v: int = 460                     # 1920 - 460 = 1460px baseline (centered in [1350, 1550])
    margin_lr: int = 100                    # Left/Right margins (880px available width)
    max_words_per_segment: int = 6
    min_words_per_segment: int = 2
    preferred_words_per_segment: int = 4
    max_chars_per_line: int = 26
    max_lines: int = 2


class SubtitleGenerator:
    """Produces professional documentary captions formatted strictly within the mobile safe zone."""

    def __init__(self, config: SubtitleConfig | None = None):
        self.config = config or SubtitleConfig()

    @staticmethod
    def _clean_word(word: str) -> str:
        """Strip punctuation from word for stopword check."""
        return re.sub(r"[^a-zA-Z0-9]", "", word).lower()

    @classmethod
    def select_highlight_word(cls, words: list[str]) -> str | None:
        """Select one impactful word in the segment for subtle yellow emphasis."""
        candidates = []
        for w in words:
            clean = cls._clean_word(w)
            if clean and clean not in STOP_WORDS and len(clean) >= 3:
                # Prioritize numbers, capitalized terms, or longer meaningful words
                score = len(clean) + (5 if any(c.isdigit() for c in clean) else 0)
                candidates.append((score, w))

        if candidates:
            candidates.sort(key=lambda x: x[0], reverse=True)
            return candidates[0][1]
        return None

    @classmethod
    def wrap_segment_text(cls, text: str, max_chars_per_line: int = 26) -> str:
        """Wrap text into at most 2 balanced lines using ASS newline tag (\\N)."""
        words = text.split()
        if len(text) <= max_chars_per_line or len(words) <= 3:
            return text

        # Find best split point near the middle
        mid = len(words) // 2
        line1 = " ".join(words[:mid])
        line2 = " ".join(words[mid:])
        return f"{line1}\\N{line2}"

    @classmethod
    def segment_sentence(
        cls,
        sentence_text: str,
        start_time: float,
        end_time: float,
        config: SubtitleConfig | None = None,
    ) -> list[SubtitleSegment]:
        """Split a long sentence into rhythm-aligned 3-6 word caption segments with precise sub-second timing."""
        cfg = config or SubtitleConfig()
        words = sentence_text.split()
        if not words:
            return []

        # Calculate word weights based on character count and punctuation pauses
        weights = []
        for w in words:
            clean_len = len(re.sub(r"[^a-zA-Z0-9]", "", w))
            pause_bonus = 2.5 if w.endswith((",", ";")) else 4.0 if w.endswith((".", ":", "!")) else 0.0
            weights.append(clean_len + pause_bonus)

        total_weight = sum(weights) or 1.0
        total_duration = max(end_time - start_time, 0.5)

        # Compute start and end times for each word
        word_markers: list[SubtitleWord] = []
        curr_t = start_time
        for i, w in enumerate(words):
            w_dur = (weights[i] / total_weight) * total_duration
            word_markers.append(
                SubtitleWord(
                    word=w,
                    start_time=round(curr_t, 3),
                    end_time=round(curr_t + w_dur, 3),
                )
            )
            curr_t += w_dur

        # Group words into short 3-6 word segments
        chunks: list[list[SubtitleWord]] = []
        curr_chunk: list[SubtitleWord] = []

        for idx, wm in enumerate(word_markers):
            curr_chunk.append(wm)
            remaining = len(word_markers) - (idx + 1)
            # Decide if chunk should close:
            # 1. Reached max words (6)
            # 2. Reached preferred words (4-5) and hit punctuation
            # 3. Remaining words can form their own valid segment (>=2)
            should_close = False
            if len(curr_chunk) >= cfg.max_words_per_segment:
                should_close = True
            elif wm.word.endswith((",", ";", ":", ".")) and len(curr_chunk) >= cfg.min_words_per_segment:
                if remaining >= cfg.min_words_per_segment or remaining == 0:
                    should_close = True
            elif len(curr_chunk) >= cfg.preferred_words_per_segment and remaining <= cfg.max_words_per_segment:
                if remaining >= cfg.min_words_per_segment or remaining == 0:
                    should_close = True

            if should_close:
                chunks.append(curr_chunk)
                curr_chunk = []

        if curr_chunk:
            if chunks and len(curr_chunk) < cfg.min_words_per_segment:
                # Merge tiny orphan with previous chunk if it doesn't exceed 7 words
                if len(chunks[-1]) + len(curr_chunk) <= 7:
                    chunks[-1].extend(curr_chunk)
                else:
                    chunks.append(curr_chunk)
            else:
                chunks.append(curr_chunk)

        # Build SubtitleSegment objects
        segments: list[SubtitleSegment] = []
        for idx, chunk in enumerate(chunks):
            seg_text = " ".join(w.word for w in chunk)
            seg_start = chunk[0].start_time
            seg_end = chunk[-1].end_time

            segments.append(
                SubtitleSegment(
                    index=idx + 1,
                    start_time=seg_start,
                    end_time=seg_end,
                    text=seg_text,
                    words=chunk,
                )
            )

        return segments

    @classmethod
    def segment_transcript(
        cls,
        sentence_events: list[tuple[float, float, str]],
        config: SubtitleConfig | None = None,
    ) -> list[SubtitleSegment]:
        """Transform full speech transcript into clean, non-overlapping 3-6 word segments."""
        cfg = config or SubtitleConfig()
        all_segments: list[SubtitleSegment] = []

        for s_start, s_end, s_text in sentence_events:
            sentence_segs = cls.segment_sentence(s_text, s_start, s_end, cfg)
            all_segments.extend(sentence_segs)

        # Renumber and ensure strict monotonicity (no overlaps)
        for i, seg in enumerate(all_segments):
            seg.index = i + 1
            if i > 0 and seg.start_time < all_segments[i - 1].end_time:
                # Align start time with previous end time
                seg.start_time = all_segments[i - 1].end_time

        return all_segments

    @staticmethod
    def _format_srt_timestamp(seconds: float) -> str:
        """Convert float seconds to SRT time string (00:00:00,000)."""
        hrs = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milli = round((seconds - int(seconds)) * 1000)
        return f"{hrs:02d}:{mins:02d}:{secs:02d},{milli:03d}"

    @staticmethod
    def _format_ass_timestamp(seconds: float) -> str:
        """Convert float seconds to ASS time string (H:MM:SS.cc)."""
        hrs = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        centi = round((seconds - int(seconds)) * 100)
        return f"{hrs}:{mins:02d}:{secs:02d}.{centi:02d}"

    @classmethod
    def generate_srt(cls, segments: list[SubtitleSegment], output_path: Path) -> Path:
        """Generate clean standard SubRip (.srt) subtitle file with short segments."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        lines: list[str] = []

        for idx, seg in enumerate(segments):
            start_str = cls._format_srt_timestamp(seg.start_time)
            end_str = cls._format_srt_timestamp(seg.end_time)
            clean_text = seg.text.replace("\\N", " ").strip()
            lines.append(str(idx + 1))
            lines.append(f"{start_str} --> {end_str}")
            lines.append(clean_text)
            lines.append("")

        output_path.write_text("\n".join(lines), encoding="utf-8")
        logger.info(f"Generated SRT subtitles: {len(segments)} segments at {output_path}")
        return output_path

    @classmethod
    def generate_ass(
        cls,
        segments: list[SubtitleSegment],
        output_path: Path,
        config: SubtitleConfig | None = None,
    ) -> Path:
        """Generate styled ASS subtitle file strictly scaled to 1080x1920 with safe zone layout."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cfg = config or SubtitleConfig()

        header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{cfg.font_name},{cfg.font_size},{cfg.primary_color},&H000000FF&,{cfg.outline_color},&H00000000&,-1,0,0,0,100,100,0,0,1,{cfg.outline_width},{cfg.shadow_depth},2,{cfg.margin_lr},{cfg.margin_lr},{cfg.margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

        events = []
        for seg in segments:
            start_str = cls._format_ass_timestamp(seg.start_time)
            end_str = cls._format_ass_timestamp(seg.end_time)

            words = seg.text.split()
            highlight_target = cls.select_highlight_word(words)

            styled_words = []
            highlight_applied = False
            for w in words:
                clean_w = cls._clean_word(w)
                clean_target = cls._clean_word(highlight_target) if highlight_target else ""
                if clean_target and clean_w == clean_target and not highlight_applied:
                    styled_words.append(f"{{\\c{cfg.highlight_color}}}{w}{{\\c{cfg.primary_color}}}")
                    highlight_applied = True
                else:
                    styled_words.append(w)

            # Auto-wrap into at most 2 balanced lines if character count warrants it
            if len(seg.text) > cfg.max_chars_per_line and len(styled_words) > 3:
                mid = len(styled_words) // 2
                styled_text = " ".join(styled_words[:mid]) + "\\N" + " ".join(styled_words[mid:])
            else:
                styled_text = " ".join(styled_words)

            events.append(f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{styled_text}")

        content = header + "\n".join(events) + "\n"
        output_path.write_text(content, encoding="utf-8")
        logger.info(f"Generated ASS subtitles: {len(segments)} segments styled for 1080x1920 at {output_path}")
        return output_path
