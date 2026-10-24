"""Cinematic Motion Engine for Visual-First Documentary Video Production.

Applies authentic camera kinematics, multi-plane optical drift, volumetric light breathing,
and high-end typography to genuine documentary footage and 3D scientific visualizations.
"""

import logging
import math
import subprocess
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFont

logger = logging.getLogger(__name__)


class CinematicMotionEngine:
    """Renders broadcast-quality 1080x1920 30FPS MP4 video clips from high-resolution visual assets."""

    def __init__(self, width: int = 1080, height: int = 1920, fps: int = 30):
        self.width = width
        self.height = height
        self.fps = fps
        self.ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()

    def render_cinematic_clip(
        self,
        image_path: Path,
        output_mp4: Path,
        duration: float,
        camera_mode: str = "CINEMATIC_FLOAT",
        branding_badge: str = "BEYOND 80 // ARCHIVE",
        scientific_label: str | None = None,
    ) -> Path:
        """Render a single high-quality asset into a cinematic 1080x1920 MP4 clip."""
        output_mp4.parent.mkdir(parents=True, exist_ok=True)
        total_frames = max(1, int(round(duration * self.fps)))

        # Load master image and upscale slightly with Lanczos for smooth sub-pixel camera movement
        base_img = Image.open(image_path).convert("RGB")
        target_w, target_h = int(self.width * 1.12), int(self.height * 1.12)
        base_img = base_img.resize((target_w, target_h), Image.Resampling.LANCZOS)

        logger.info(
            f"Rendering cinematic clip from '{image_path.name}': {duration:.2f}s, "
            f"{total_frames} frames @ {self.fps}fps -> {output_mp4.name}"
        )

        cmd = [
            self.ffmpeg_bin,
            "-y",
            "-f",
            "rawvideo",
            "-pix_fmt",
            "rgb24",
            "-s",
            f"{self.width}x{self.height}",
            "-r",
            str(self.fps),
            "-i",
            "-",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "17",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(output_mp4.resolve()),
        ]

        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

        max_dx = target_w - self.width
        max_dy = target_h - self.height

        try:
            for frame_idx in range(total_frames):
                progress = frame_idx / max(1, total_frames - 1)
                t = frame_idx / self.fps

                # Smooth cinematic camera float: sinusoidal ease-in-out drift
                # Prevents harsh linear pans or repetitive harsh zooms
                drift_x = int((0.5 - 0.5 * math.cos(progress * math.pi)) * (max_dx * 0.8))
                drift_y = int((0.5 - 0.5 * math.cos(progress * math.pi * 0.7)) * (max_dy * 0.6))

                # Crop view window
                frame_img = base_img.crop((drift_x, drift_y, drift_x + self.width, drift_y + self.height))

                # Subtle atmospheric breathing: micro-contrast pulse (0.98 - 1.03)
                contrast_factor = 1.0 + 0.025 * math.sin(t * 1.4)
                frame_img = ImageEnhance.Contrast(frame_img).enhance(contrast_factor)

                # Draw minimal branding and scientific label overlays
                self._apply_editorial_overlays(frame_img, branding_badge, scientific_label, t)

                proc.stdin.write(frame_img.tobytes())

            proc.stdin.close()
            proc.wait()

            if proc.returncode != 0:
                err = proc.stderr.read().decode("utf-8", errors="replace")
                raise RuntimeError(f"FFmpeg render failed: {err}")

        except Exception as e:
            if proc.poll() is None:
                proc.kill()
            raise e

        logger.info(f"Rendered {output_mp4.name} successfully ({output_mp4.stat().st_size / (1024*1024):.2f} MB).")
        return output_mp4

    def render_transformation_clip(
        self,
        image_a_path: Path,
        image_b_path: Path,
        output_mp4: Path,
        duration: float,
        branding_badge: str = "BEYOND 80 // SCIENCE SIMULATION",
        scientific_label: str = "PHASE TRANSITION // CH4 -> C (DIAMOND)",
    ) -> Path:
        """Render a cinematic explanatory transformation between two scientific states."""
        output_mp4.parent.mkdir(parents=True, exist_ok=True)
        total_frames = max(1, int(round(duration * self.fps)))

        # Load both states and prepare high-res canvases
        target_w, target_h = int(self.width * 1.10), int(self.height * 1.10)
        img_a = Image.open(image_a_path).convert("RGB").resize((target_w, target_h), Image.Resampling.LANCZOS)
        img_b = Image.open(image_b_path).convert("RGB").resize((target_w, target_h), Image.Resampling.LANCZOS)

        logger.info(f"Rendering transformation clip {image_a_path.name} -> {image_b_path.name}: {duration:.2f}s...")

        cmd = [
            self.ffmpeg_bin,
            "-y",
            "-f",
            "rawvideo",
            "-pix_fmt",
            "rgb24",
            "-s",
            f"{self.width}x{self.height}",
            "-r",
            str(self.fps),
            "-i",
            "-",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "17",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(output_mp4.resolve()),
        ]

        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        max_dx = target_w - self.width
        max_dy = target_h - self.height

        # Transformation curve:
        # 0.0 -> 0.40: State A with dynamic camera push-in
        # 0.40 -> 0.65: High-energy dissociation burst & cross-fade
        # 0.65 -> 1.00: State B (Diamond crystallization reveal) with slow optical float
        try:
            for frame_idx in range(total_frames):
                progress = frame_idx / max(1, total_frames - 1)
                t = frame_idx / self.fps

                # Camera motion coordinates
                crop_x = int((0.5 - 0.5 * math.cos(progress * math.pi)) * (max_dx * 0.7))
                crop_y = int((0.5 - 0.5 * math.cos(progress * math.pi)) * (max_dy * 0.7))

                crop_a = img_a.crop((crop_x, crop_y, crop_x + self.width, crop_y + self.height))
                crop_b = img_b.crop((crop_x, crop_y, crop_x + self.width, crop_y + self.height))

                if progress < 0.40:
                    frame_img = crop_a
                elif progress > 0.65:
                    frame_img = crop_b
                else:
                    # Non-linear smooth cross-dissolve with energy flash
                    dissolve_progress = (progress - 0.40) / 0.25
                    alpha = 0.5 - 0.5 * math.cos(dissolve_progress * math.pi)
                    frame_img = Image.blend(crop_a, crop_b, alpha)

                    # Optical shockwave energy bloom at midpoint
                    flash_intensity = math.sin(dissolve_progress * math.pi) * 0.25
                    if flash_intensity > 0.05:
                        frame_img = ImageEnhance.Brightness(frame_img).enhance(1.0 + flash_intensity)

                self._apply_editorial_overlays(frame_img, branding_badge, scientific_label, t)
                proc.stdin.write(frame_img.tobytes())

            proc.stdin.close()
            proc.wait()

            if proc.returncode != 0:
                err = proc.stderr.read().decode("utf-8", errors="replace")
                raise RuntimeError(f"FFmpeg render failed: {err}")

        except Exception as e:
            if proc.poll() is None:
                proc.kill()
            raise e

        logger.info(f"Rendered transformation clip {output_mp4.name} successfully ({output_mp4.stat().st_size / (1024*1024):.2f} MB).")
        return output_mp4

    def _apply_editorial_overlays(
        self,
        img: Image.Image,
        branding_badge: str,
        scientific_label: str | None,
        t: float,
    ) -> None:
        """Apply subtle, non-intrusive documentary branding and scientific annotation tags."""
        draw = ImageDraw.Draw(img, "RGBA")
        font = ImageFont.load_default()

        # 1. Subtle Beyond 80 Branding Badge in Top Corner (Y = 90 - 130)
        # Never blocks visuals, low-key dark pill with cyan accent
        badge_text = branding_badge.upper()
        badge_len = len(badge_text) * 7
        bx, by = 60, 100
        draw.rounded_rectangle(
            [bx, by, bx + badge_len + 30, by + 34],
            radius=6,
            fill=(10, 15, 25, 175),
            outline=(0, 215, 255, 130),
            width=1,
        )
        # Small glowing cyan status pip
        pip_alpha = int(180 + 75 * math.sin(t * 3.0))
        draw.ellipse([bx + 10, by + 12, bx + 18, by + 20], fill=(0, 215, 255, pip_alpha))
        draw.text((bx + 26, by + 10), badge_text, fill=(220, 230, 245, 220), font=font)

        # 2. Scientific Label & Telemetry Callout (Y = 160 - 220)
        # Well above subtitle safe zone (Y < 1320)
        if scientific_label:
            lbl_text = scientific_label.upper()
            lbl_len = len(lbl_text) * 7
            lx, ly = 60, 150
            draw.rounded_rectangle(
                [lx, ly, lx + lbl_len + 24, ly + 32],
                radius=4,
                fill=(5, 10, 20, 185),
                outline=(255, 215, 0, 140),
                width=1,
            )
            draw.text((lx + 12, ly + 9), lbl_text, fill=(255, 215, 0, 230), font=font)
