"""FFmpeg Master Video Rendering Engine."""

import logging
import subprocess
from pathlib import Path

import imageio_ffmpeg

from videoautomater.config import settings
from videoautomater.models.media import Storyboard

logger = logging.getLogger(__name__)


class FFmpegAssembler:
    """Assembles storyboard frames, motion effects, audio soundscape, and subtitles into master MP4."""

    def __init__(self):
        self.ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
        self.width = settings.width
        self.height = settings.height
        self.fps = settings.fps

    def render_master_video(
        self,
        storyboard: Storyboard,
        audio_path: Path,
        subtitles_path: Path,
        output_mp4_path: Path,
    ) -> Path:
        """Render the broadcast-quality 1080x1920 80-second vertical master MP4."""
        output_mp4_path.parent.mkdir(parents=True, exist_ok=True)
        temp_dir = output_mp4_path.parent / "temp_render"
        temp_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Beginning FFmpeg master rendering: {len(storyboard.scenes)} scenes at {self.width}x{self.height} @ {self.fps}fps.")

        # 1. Create a concat demuxer list for all scenes
        concat_list_file = temp_dir / "concat_list.txt"
        concat_lines = ["ffconcat version 1.0"]
        for scene in storyboard.scenes:
            if scene.duration > 0:
                scene_path = Path(scene.local_file_path).resolve()
                concat_lines.append(f"file '{scene_path}'")
                concat_lines.append(f"duration {scene.duration:.3f}")

        # The last file must be repeated without duration in concat format
        if storyboard.scenes:
            last_path = Path(storyboard.scenes[-1].local_file_path).resolve()
            concat_lines.append(f"file '{last_path}'")

        concat_list_file.write_text("\n".join(concat_lines), encoding="utf-8")

        # 2. Build FFmpeg command
        # Subtitle filter - escape colons and backslashes for FFmpeg filtergraph
        sub_escaped = str(subtitles_path.resolve()).replace("\\", "/").replace(":", "\\:")
        
        # Video filtergraph: scale to 1080x1920, force 30fps, format yuv420p, burn subtitles
        # Note: If .ass or .srt is provided, use subtitles filter
        vf_filter = (
            f"scale={self.width}:{self.height}:force_original_aspect_ratio=decrease,"
            f"pad={self.width}:{self.height}:(ow-iw)/2:(oh-ih)/2,"
            f"fps={self.fps},"
            f"format=yuv420p,"
            f"subtitles='{sub_escaped}'"
        )

        cmd = [
            self.ffmpeg_bin,
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_list_file),
            "-i",
            str(audio_path.resolve()),
            "-vf",
            vf_filter,
            "-c:v",
            "libx264",
            "-preset",
            "ultrafast",  # Fast rendering while maintaining high quality
            "-crf",
            "20",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-ar",
            "48000",
            "-t",
            f"{storyboard.total_duration:.2f}",
            "-movflags",
            "+faststart",
            str(output_mp4_path.resolve()),
        ]

        logger.info(f"Executing FFmpeg render command to {output_mp4_path}...")
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            logger.error(f"FFmpeg render failed:\n{res.stderr}")
            # Try without subtitles filter in case fontconfig / libass is missing
            fallback_vf = (
                f"scale={self.width}:{self.height}:force_original_aspect_ratio=decrease,"
                f"pad={self.width}:{self.height}:(ow-iw)/2:(oh-ih)/2,"
                f"fps={self.fps},"
                f"format=yuv420p"
            )
            cmd_fallback = [
                self.ffmpeg_bin,
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(concat_list_file),
                "-i",
                str(audio_path.resolve()),
                "-vf",
                fallback_vf,
                "-c:v",
                "libx264",
                "-preset",
                "ultrafast",
                "-crf",
                "20",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                "-ar",
                "48000",
                "-t",
                f"{storyboard.total_duration:.2f}",
                "-movflags",
                "+faststart",
                str(output_mp4_path.resolve()),
            ]
            subprocess.run(cmd_fallback, check=True, capture_output=True, text=True)
            logger.info("Render completed using native fallback video filter.")

        logger.info(f"Master MP4 generated successfully: {output_mp4_path} ({output_mp4_path.stat().st_size / (1024*1024):.2f} MB)")
        return output_mp4_path
