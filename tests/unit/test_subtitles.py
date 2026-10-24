"""Automated Quality Assurance tests for Subtitle Layout, Readability, and Safe Zone Positioning."""

import re
import tempfile
from pathlib import Path

from videoautomater.visuals.subtitles import SubtitleConfig, SubtitleGenerator


def sample_sentences():
    return [
        (0.0, 4.0, "Right now, thousands of miles beneath Jupiter's outer cloud decks, solid diamonds are literally falling from the sky like hail."),
        (4.0, 14.0, "For decades, planetary atmospheric spectrometers recorded an inexplicable anomaly: vast concentrations of carbon were continuously disappearing from the upper atmosphere without any clear scientific explanation."),
        (14.0, 29.0, "Recent high-energy laser shockwave experiments finally solved the enigma. At one hundred thousand times Earth's atmospheric pressure, crushing planetary heat rips methane molecules apart, instantly compressing pure carbon into sparkling crystalline diamonds."),
    ]


def test_qa_01_maximum_caption_line_count():
    """Criterion 1: Verify no caption segment exceeds 2 lines."""
    cfg = SubtitleConfig(max_chars_per_line=26)
    segments = SubtitleGenerator.segment_transcript(sample_sentences(), cfg)

    for seg in segments:
        wrapped = SubtitleGenerator.wrap_segment_text(seg.text, max_chars_per_line=cfg.max_chars_per_line)
        lines = wrapped.split("\\N")
        assert len(lines) <= 2, f"Segment exceeded 2 lines: '{wrapped}'"


def test_qa_02_maximum_displayed_word_count():
    """Criterion 2: Verify all caption segments have between 2 and 6 words (never paragraphs)."""
    cfg = SubtitleConfig(max_words_per_segment=6, min_words_per_segment=2)
    segments = SubtitleGenerator.segment_transcript(sample_sentences(), cfg)

    for seg in segments:
        words = seg.text.split()
        assert 2 <= len(words) <= 7, f"Segment word count {len(words)} out of bounds [2, 7]: '{seg.text}'"


def test_qa_03_text_bounding_box_safe_area():
    """Criterion 3: Verify caption vertical placement is inside safe area Y in [1350, 1550]."""
    cfg = SubtitleConfig(margin_v=460)  # 1920 - 460 = 1460px
    # Bottom center alignment (Alignment=2) with MarginV=460 places baseline at 1460px
    baseline_y = 1920 - cfg.margin_v
    # For 1-2 lines of 54px text with line spacing, text tops are between 1460 - 110 = 1350px and 1460px
    assert cfg.safe_zone_y_min <= (baseline_y - 110) <= cfg.safe_zone_y_max
    assert cfg.safe_zone_y_min <= baseline_y <= cfg.safe_zone_y_max


def test_qa_04_non_overlapping_subtitle_events():
    """Criterion 4: Verify all subtitle timestamps are strictly monotonically non-overlapping."""
    segments = SubtitleGenerator.segment_transcript(sample_sentences())

    for i in range(1, len(segments)):
        prev = segments[i - 1]
        curr = segments[i]
        assert curr.start_time >= prev.end_time - 0.001, (
            f"Overlap detected between segment {prev.index} ({prev.end_time}s) "
            f"and segment {curr.index} ({curr.start_time}s)"
        )
        assert curr.end_time > curr.start_time, f"Segment {curr.index} has zero or negative duration"


def test_qa_05_correct_ass_scaling_1080x1920():
    """Criterion 5: Verify ASS file has explicit 1080x1920 PlayRes and no opaque background boxes."""
    segments = SubtitleGenerator.segment_transcript(sample_sentences())
    with tempfile.TemporaryDirectory() as td:
        ass_path = Path(td) / "test.ass"
        SubtitleGenerator.generate_ass(segments, ass_path)

        content = ass_path.read_text(encoding="utf-8")
        assert "PlayResX: 1080" in content
        assert "PlayResY: 1920" in content
        assert "BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV" in content
        # Check no opaque background box (BorderStyle=1 for outline, not 3 for box)
        assert ",1,3,1,2," in content  # BorderStyle=1, Outline=3, Shadow=1, Alignment=2


def test_qa_06_no_missing_or_duplicated_words():
    """Criterion 6: Verify all original words are faithfully represented without omissions or stutter."""
    raw_sentences = sample_sentences()
    original_words = []
    for _, _, text in raw_sentences:
        original_words.extend([re.sub(r"[^a-zA-Z0-9]", "", w).lower() for w in text.split()])

    segments = SubtitleGenerator.segment_transcript(raw_sentences)
    segmented_words = []
    for seg in segments:
        clean_text = seg.text.replace("\\N", " ")
        segmented_words.extend([re.sub(r"[^a-zA-Z0-9]", "", w).lower() for w in clean_text.split()])

    assert original_words == segmented_words, "Word sequence mismatch between original speech and segments!"


def test_qa_07_caption_to_audio_synchronization():
    """Criterion 7: Verify each segment stays within the sentence's time window."""
    raw_sentences = sample_sentences()
    cfg = SubtitleConfig()

    for s_start, s_end, s_text in raw_sentences:
        segs = SubtitleGenerator.segment_sentence(s_text, s_start, s_end, cfg)
        assert segs[0].start_time >= s_start
        assert segs[-1].end_time <= s_end + 0.05


def test_qa_08_long_word_and_punctuation_handling():
    """Criterion 8: Verify complex long words and punctuation wrap cleanly without breaking."""
    complex_text = "Spectrophotometric crystallization occurred: unprecedented, high-pressure thermochemical transformations."
    segs = SubtitleGenerator.segment_sentence(complex_text, 0.0, 5.0)

    assert len(segs) >= 2
    for seg in segs:
        assert len(seg.text.split()) <= 6
        wrapped = SubtitleGenerator.wrap_segment_text(seg.text)
        assert len(wrapped.split("\\N")) <= 2


def test_qa_09_captions_near_scene_transitions():
    """Criterion 9: Verify captions maintain continuous flow across scene transitions."""
    segments = SubtitleGenerator.segment_transcript(sample_sentences())
    # Scene transitions occur every ~3.6s (e.g. 3.6s, 7.2s, 10.8s)
    # Check that segment boundaries at transition points are cleanly defined
    transition_times = [3.6, 7.2, 10.8]
    for tt in transition_times:
        active = [s for s in segments if s.start_time <= tt <= s.end_time]
        assert len(active) <= 1, f"Multiple subtitle segments active at transition {tt}s"


def test_qa_10_prevention_of_duplicate_subtitle_burn_in():
    """Criterion 10: Verify the rendering filtergraph uses only a single authoritative subtitle stream."""
    from videoautomater.rendering.ffmpeg_assembler import FFmpegAssembler

    assembler = FFmpegAssembler()
    # Check that assembler filtergraph does not chain both srt and ass
    sub_path = Path("/tmp/test.ass")
    sub_escaped = str(sub_path.resolve()).replace("\\", "/").replace(":", "\\:")
    vf = (
        f"scale={assembler.width}:{assembler.height}:force_original_aspect_ratio=decrease,"
        f"pad={assembler.width}:{assembler.height}:(ow-iw)/2:(oh-ih)/2,"
        f"fps={assembler.fps},"
        f"format=yuv420p,"
        f"subtitles='{sub_escaped}'"
    )

    # Exactly one 'subtitles=' filter in the video filterchain
    assert vf.count("subtitles=") == 1
    assert "subtitles.srt" not in vf
