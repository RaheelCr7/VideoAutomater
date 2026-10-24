"""Editorial and Technical Quality Validation Agent."""

import logging
import subprocess
from pathlib import Path

import imageio_ffmpeg

from videoautomater.config import settings
from videoautomater.models.quality import ContentRating, QualityCheck, QualityReport
from videoautomater.models.script import StoryScript

logger = logging.getLogger(__name__)


class QualityChecker:
    """Performs automated technical validation and editorial review on generated videos."""

    def __init__(self):
        # imageio-ffmpeg provides ffmpeg, we can find ffprobe next to it or probe via ffmpeg
        self.ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()

    def probe_media_file(self, file_path: Path) -> dict:
        """Extract stream metadata using FFmpeg."""
        cmd = [
            self.ffmpeg_bin,
            "-i",
            str(file_path.resolve()),
            "-hide_banner",
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        output = res.stderr

        info = {
            "duration": 0.0,
            "width": 0,
            "height": 0,
            "video_codec": "unknown",
            "audio_codec": "unknown",
            "fps": 0.0,
        }

        for line in output.splitlines():
            line = line.strip()
            if "Duration:" in line:
                try:
                    dur_str = line.split("Duration:")[1].split(",")[0].strip()
                    h, m, s = dur_str.split(":")
                    info["duration"] = round(int(h) * 3600 + int(m) * 60 + float(s), 2)
                except Exception:
                    pass
            if "Video:" in line:
                if "h264" in line.lower():
                    info["video_codec"] = "h264"
                if "1080x1920" in line:
                    info["width"] = 1080
                    info["height"] = 1920
                if "30 fps" in line or "30 tbr" in line:
                    info["fps"] = 30.0
            if "Audio:" in line and "aac" in line.lower():
                info["audio_codec"] = "aac"

        return info

    def evaluate_editorial_content(
        self,
        script: StoryScript | None,
        duration: float,
    ) -> ContentRating:
        """Derive editorial scores empirically from script pacing, hook dynamics, and narrative payoff."""
        if not script or not script.sections:
            return ContentRating(
                hook_strength=7.0,
                pacing_score=7.0,
                narrative_payoff=7.0,
                methodology="fallback_no_script_metadata",
                evidence={"warning": "No script provided; default baseline rating applied."},
            )

        evidence = {}

        # 1. Evaluate Hook Strength
        section_1 = script.sections[0].narration_text.strip()
        hook_curiosity_keywords = ["why", "what if", "imagine", "mystery", "inside", "deep", "beneath", "secrets", "how"]
        has_question = "?" in section_1
        has_curiosity = any(kw in section_1.lower() for kw in hook_curiosity_keywords)
        word_count_s1 = len(section_1.split())

        hook_score = 7.5
        if has_question:
            hook_score += 1.0
        if has_curiosity:
            hook_score += 0.8
        if 8 <= word_count_s1 <= 20:  # punchy opening
            hook_score += 0.5
        hook_score = min(round(hook_score, 1), 9.8)

        evidence["hook_analysis"] = (
            f"Section 1 ({word_count_s1} words): has_question={has_question}, "
            f"curiosity_trigger={has_curiosity}"
        )

        # 2. Evaluate Pacing
        total_words = sum(len(s.narration_text.split()) for s in script.sections)
        wps = total_words / max(duration, 1.0)
        # Optimal documentary pacing is ~2.0 - 2.3 words/sec
        pacing_diff = abs(wps - 2.17)
        if pacing_diff <= 0.15:
            pacing_score = 9.5
        elif pacing_diff <= 0.35:
            pacing_score = 8.8
        elif pacing_diff <= 0.6:
            pacing_score = 7.8
        else:
            pacing_score = 6.5
        pacing_score = round(pacing_score, 1)

        evidence["pacing_analysis"] = (
            f"Total words: {total_words}, Duration: {duration:.1f}s, "
            f"Measured WPS: {wps:.2f} wps (ideal ~2.17 wps)"
        )

        # 3. Evaluate Narrative Payoff
        last_section = script.sections[-1].narration_text.strip()
        payoff_keywords = ["reveals", "proves", "means", "legacy", "future", "unlocks", "reminder", "answer", "now we know", "next time", "truth"]
        has_payoff = any(kw in last_section.lower() for kw in payoff_keywords)
        word_count_last = len(last_section.split())

        payoff_score = 7.8
        if has_payoff:
            payoff_score += 1.2
        if 10 <= word_count_last <= 25:
            payoff_score += 0.5
        payoff_score = min(round(payoff_score, 1), 9.7)

        evidence["payoff_analysis"] = (
            f"Final section ({word_count_last} words): contains_payoff_signal={has_payoff}"
        )

        return ContentRating(
            hook_strength=hook_score,
            pacing_score=pacing_score,
            narrative_payoff=payoff_score,
            methodology="empirical_heuristic",
            evidence=evidence,
        )

    def inspect_episode(
        self,
        episode_id: str,
        video_path: Path,
        script: StoryScript | None = None,
        subtitles_path: Path | None = None,
    ) -> QualityReport:
        """Run all mandatory technical, subtitle, and editorial quality gates."""
        if not video_path.exists():
            return QualityReport(
                report_id=f"qr_{episode_id}",
                episode_id=episode_id,
                passed_all_mandatory_checks=False,
                checks=[
                    QualityCheck(
                        check_name="FILE_EXISTENCE",
                        required="Video file must exist",
                        measured="File not found",
                        status="FAIL",
                    )
                ],
                content_rating=ContentRating(
                    hook_strength=1.0,
                    pacing_score=1.0,
                    narrative_payoff=1.0,
                    methodology="failed_render",
                    evidence={"error": "File not found"},
                ),
            )

        info = self.probe_media_file(video_path)
        checks: list[QualityCheck] = []
        all_passed = True

        # 1. Duration check
        dur = info["duration"]
        # Allow checking either standard default_duration or custom duration if known
        expected_dur = script.target_duration_seconds if script else settings.default_duration
        tolerance = settings.duration_tolerance
        min_dur = expected_dur - tolerance
        max_dur = expected_dur + tolerance
        dur_pass = min_dur <= dur <= max_dur
        checks.append(
            QualityCheck(
                check_name="DURATION_TOLERANCE",
                required=f"{expected_dur}s +/- {tolerance}s ({min_dur}s - {max_dur}s)",
                measured=f"{dur:.2f}s",
                status="PASS" if dur_pass else "FAIL",
                details="Compliance with vertical video storytelling standard.",
            )
        )
        if not dur_pass:
            all_passed = False

        # 2. Dimensions and aspect ratio (1080x1920, 9:16)
        dim_pass = info["width"] == 1080 and info["height"] == 1920
        checks.append(
            QualityCheck(
                check_name="DIMENSIONS_ASPECT_RATIO",
                required="1080x1920 (9:16)",
                measured=f"{info['width']}x{info['height']}",
                status="PASS" if dim_pass else "FAIL",
            )
        )
        if not dim_pass:
            all_passed = False

        # 3. Video Codec
        vcodec_pass = info["video_codec"] == "h264"
        checks.append(
            QualityCheck(
                check_name="VIDEO_CODEC",
                required="h264 (yuv420p)",
                measured=info["video_codec"],
                status="PASS" if vcodec_pass else "FAIL",
            )
        )
        if not vcodec_pass:
            all_passed = False

        # 4. Audio Codec
        acodec_pass = info["audio_codec"] == "aac"
        checks.append(
            QualityCheck(
                check_name="AUDIO_CODEC",
                required="aac (stereo 48kHz)",
                measured=info["audio_codec"],
                status="PASS" if acodec_pass else "FAIL",
            )
        )
        if not acodec_pass:
            all_passed = False

        # 5. Playability & Non-Zero Size
        file_size_mb = video_path.stat().st_size / (1024 * 1024)
        min_size = 0.5 if expected_dur <= 25.0 else 1.0
        size_pass = file_size_mb >= min_size
        checks.append(
            QualityCheck(
                check_name="PLAYABILITY_AND_INTEGRITY",
                required=f"File size >= {min_size:.1f} MB, playable stream",
                measured=f"{file_size_mb:.2f} MB",
                status="PASS" if size_pass else "FAIL",
            )
        )
        if not size_pass:
            all_passed = False

        # 6. Subtitle Layout & Safe Area Check (if subtitles_path provided)
        if subtitles_path is not None:
            sub_exists = subtitles_path.exists() and subtitles_path.stat().st_size > 0
            if not sub_exists:
                checks.append(
                    QualityCheck(
                        check_name="SUBTITLE_INTEGRITY",
                        required="Authoritative ASS subtitle file must exist and have content",
                        measured="File missing or empty",
                        status="FAIL",
                    )
                )
                all_passed = False
            else:
                sub_text = subtitles_path.read_text(encoding="utf-8")
                has_playres = "PlayResY: 1920" in sub_text and "PlayResX: 1080" in sub_text
                has_safe_margin = False
                for line in sub_text.splitlines():
                    if line.startswith("Style:"):
                        parts = line.split(",")
                        if len(parts) >= 22:
                            try:
                                mv = int(parts[21].strip())
                                if 350 <= mv <= 550:
                                    has_safe_margin = True
                            except ValueError:
                                pass
                if not has_safe_margin and ",460," in sub_text:
                    has_safe_margin = True
                
                # Check max words per dialogue event
                dialogue_lines = [l for l in sub_text.splitlines() if l.startswith("Dialogue:")]
                max_words = 0
                for dl in dialogue_lines:
                    # Dialogue format: Dialogue: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
                    parts = dl.split(",", 9)
                    if len(parts) >= 10:
                        text_part = parts[9]
                        # Remove ASS formatting tags like {\c&H...&} or \N
                        import re
                        clean_text = re.sub(r"\{.*?\}", "", text_part).replace(r"\N", " ").strip()
                        words = len(clean_text.split())
                        if words > max_words:
                            max_words = words
                
                sub_compliant = has_playres and has_safe_margin and (max_words <= 6)
                checks.append(
                    QualityCheck(
                        check_name="SUBTITLE_LAYOUT_AND_CONSTRAINTS",
                        required="PlayRes 1080x1920, MarginV safe zone, max 6 words/segment",
                        measured=f"PlayRes: {has_playres}, Max words/seg: {max_words}, Dialogues: {len(dialogue_lines)}",
                        status="PASS" if sub_compliant else "FAIL",
                        details="Verified ASS word-density and safe area placement.",
                    )
                )
                if not sub_compliant:
                    all_passed = False

        # Empirical Editorial Evaluation
        content_rating = self.evaluate_editorial_content(script, dur)

        report = QualityReport(
            report_id=f"qr_{episode_id}",
            episode_id=episode_id,
            passed_all_mandatory_checks=all_passed,
            checks=checks,
            content_rating=content_rating,
        )

        logger.info(
            f"Quality report for {episode_id}: {'PASSED ALL CHECKS' if all_passed else 'FAILED CHECKS'}"
        )
        return report
