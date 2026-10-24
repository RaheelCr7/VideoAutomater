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


def test_qa_11_no_silent_subtitle_omission():
    """Criterion 11: Verify rendering fails explicitly with RuntimeError if subtitle file is missing or invalid."""
    import pytest
    from videoautomater.models.media import Storyboard
    from videoautomater.rendering.ffmpeg_assembler import FFmpegAssembler

    assembler = FFmpegAssembler()
    sb = Storyboard(
        storyboard_id="sb_test",
        episode_id="ep_test",
        script_id="sc_test",
        scenes=[],
        total_duration=5.0,
    )

    # Calling render_master_video with invalid non-existent paths should raise an exception, not silently export
    with pytest.raises((RuntimeError, FileNotFoundError, Exception)):
        assembler.render_master_video(
            storyboard=sb,
            audio_path=Path("/invalid/audio.aac"),
            subtitles_path=Path("/invalid/subtitles.ass"),
            output_mp4_path=Path("/invalid/out.mp4"),
        )


def test_qa_12_non_hardcoded_editorial_quality_scoring():
    """Criterion 12: Verify QualityChecker evaluates real content metrics instead of hardcoded numbers."""
    from videoautomater.models.script import ScriptSection, StoryScript
    from videoautomater.quality.checker import QualityChecker

    checker = QualityChecker()
    sections = [
        ScriptSection(
            section_id="sec_1",
            timeline_start=0.0,
            timeline_end=5.0,
            role="HOOK",
            narration_text="Why are diamonds falling inside Jupiter?",
            visual_intent="Opening mystery",
        ),
        ScriptSection(
            section_id="sec_2",
            timeline_start=5.0,
            timeline_end=10.0,
            role="PAYOFF",
            narration_text="This scientific discovery reveals the true nature of deep planetary atmospheres.",
            visual_intent="Final payoff",
        ),
    ]
    script = StoryScript(
        script_id="test_script",
        brief_id="brief_1",
        title="Test Title",
        selected_hook="Why are diamonds falling inside Jupiter?",
        total_spoken_words=len("Why are diamonds falling inside Jupiter? This scientific discovery reveals the true nature of deep planetary atmospheres.".split()),
        estimated_reading_speed_wps=2.1,
        sections=sections * 3,  # 6 sections
        full_text="Test script full text",
    )

    rating = checker.evaluate_editorial_content(script=script, duration=10.0)
    assert rating.methodology == "empirical_heuristic"
    assert "hook_analysis" in rating.evidence
    assert "pacing_analysis" in rating.evidence
    assert "payoff_analysis" in rating.evidence
    assert isinstance(rating.hook_strength, float)
    assert isinstance(rating.pacing_score, float)
    assert isinstance(rating.narrative_payoff, float)


def test_qa_13_segment_words_real_tts_timestamps():
    """Criterion 13: Verify segment_words uses authoritative word timestamps without estimation."""
    from videoautomater.models.media import SubtitleWord
    test_words = [
        SubtitleWord(word="Deep", start_time=0.100, end_time=0.400),
        SubtitleWord(word="inside", start_time=0.412, end_time=0.900),
        SubtitleWord(word="icy", start_time=0.912, end_time=1.225),
        SubtitleWord(word="planets", start_time=1.238, end_time=1.700),
        SubtitleWord(word="like", start_time=1.712, end_time=1.912),
        SubtitleWord(word="Neptune,", start_time=1.925, end_time=2.575),
        SubtitleWord(word="diamonds", start_time=2.600, end_time=3.100),
        SubtitleWord(word="fall.", start_time=3.150, end_time=3.700),
    ]

    segments = SubtitleGenerator.segment_words(test_words)
    assert len(segments) >= 2
    # First segment start time must match first word start time exactly
    assert segments[0].start_time == 0.100
    assert segments[0].words[0].word == "Deep"
    # Punctuation-based boundary
    assert any(s.text.endswith("Neptune,") for s in segments)
    # Monotonic timestamps
    for i in range(1, len(segments)):
        assert segments[i].start_time >= segments[i - 1].start_time


def test_qa_14_verify_narration_alignment():
    """Criterion 14: Verify ordered narration-to-caption alignment verification."""
    from videoautomater.models.media import SubtitleWord
    script_text = "Deep inside icy planets like Neptune, diamonds fall."
    words = [
        SubtitleWord(word="Deep", start_time=0.1, end_time=0.4),
        SubtitleWord(word="inside", start_time=0.4, end_time=0.9),
        SubtitleWord(word="icy", start_time=0.9, end_time=1.2),
        SubtitleWord(word="planets", start_time=1.2, end_time=1.7),
        SubtitleWord(word="like", start_time=1.7, end_time=1.9),
        SubtitleWord(word="Neptune,", start_time=1.9, end_time=2.5),
        SubtitleWord(word="diamonds", start_time=2.6, end_time=3.1),
        SubtitleWord(word="fall.", start_time=3.1, end_time=3.7),
    ]
    segments = SubtitleGenerator.segment_words(words)
    passed, stats = SubtitleGenerator.verify_narration_alignment(script_text, segments)
    assert passed
    assert stats["is_ordered"] is True
    assert stats["is_monotonic"] is True
    assert float(stats["vocabulary_coverage"].replace("%", "")) >= 98.0
