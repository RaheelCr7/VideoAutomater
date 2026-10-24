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

                # Camera kinematics based on shot direction mode
                mode_upper = camera_mode.upper()
                if "PLUNGE" in mode_upper:
                    # Inward acceleration plunge with micro-turbulence
                    turb = int(2.5 * math.sin(t * 22.0) * (1.0 - progress * 0.5))
                    drift_x = int(progress * max_dx * 0.9) + turb
                    drift_y = int(progress * max_dy * 0.9) + turb
                elif "ARCHIVAL" in mode_upper or "TELEMETRY" in mode_upper:
                    # Slow, deliberate archival horizontal telemetry drift
                    drift_x = int((0.5 - 0.5 * math.cos(progress * math.pi * 0.8)) * max_dx)
                    drift_y = int(max_dy * 0.3 + 8.0 * math.sin(t * 0.8))
                elif "DESCENT" in mode_upper:
                    # Downward gravitational tracking through planetary mantle
                    drift_x = int(max_dx * 0.5 + (max_dx * 0.25) * math.sin(progress * math.pi))
                    drift_y = int(progress * max_dy)
                elif "PULLBACK" in mode_upper:
                    # Majestic cosmic pull-back: easing from deep crop outwards
                    ease_out = 1.0 - math.pow(1.0 - progress, 2.5)
                    drift_x = int((1.0 - ease_out) * (max_dx * 0.7))
                    drift_y = int((1.0 - ease_out) * (max_dy * 0.7))
                elif "CRYSTALLINE" in mode_upper or "REVEAL" in mode_upper:
                    # Elegant orbital float around crystalline subject
                    drift_x = int((0.5 + 0.5 * math.sin(progress * math.pi * 1.2)) * (max_dx * 0.8))
                    drift_y = int((0.5 - 0.5 * math.cos(progress * math.pi * 0.9)) * (max_dy * 0.7))
                else:
                    # Default CINEMATIC_FLOAT
                    drift_x = int((0.5 - 0.5 * math.cos(progress * math.pi)) * (max_dx * 0.8))
                    drift_y = int((0.5 - 0.5 * math.cos(progress * math.pi * 0.7)) * (max_dy * 0.6))

                drift_x = max(0, min(max_dx, drift_x))
                drift_y = max(0, min(max_dy, drift_y))

                # Crop view window
                frame_img = base_img.crop((drift_x, drift_y, drift_x + self.width, drift_y + self.height))

                # Subtle atmospheric breathing: micro-contrast pulse (0.98 - 1.03)
                contrast_factor = 1.0 + 0.025 * math.sin(t * 1.4)
                frame_img = ImageEnhance.Contrast(frame_img).enhance(contrast_factor)

                # Optional mode-specific optical enhancements
                if "ARCHIVAL" in mode_upper:
                    # Extremely subtle documentary film grain & telemetry scan
                    draw_arch = ImageDraw.Draw(frame_img, "RGBA")
                    scan_y = int((t * 260) % self.height)
                    draw_arch.line([(0, scan_y), (self.width, scan_y)], fill=(0, 215, 255, 22), width=1)

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

    def render_multi_stage_transformation_clip(
        self,
        stages: list[tuple[Path, float, float, str]],
        output_mp4: Path,
        total_duration: float,
        branding_badge: str = "BEYOND 80",
    ) -> Path:
        """Render a continuous, narration-synchronized explanatory transformation across physical states."""
        output_mp4.parent.mkdir(parents=True, exist_ok=True)
        total_frames = max(1, int(round(total_duration * self.fps)))

        # Pre-load and scale all stage images
        target_w, target_h = int(self.width * 1.10), int(self.height * 1.10)
        stage_imgs = [
            Image.open(p).convert("RGB").resize((target_w, target_h), Image.Resampling.LANCZOS)
            for p, _, _, _ in stages
        ]

        logger.info(
            f"Rendering multi-stage transformation clip ({len(stages)} stages): "
            f"{total_duration:.2f}s, {total_frames} frames @ {self.fps}fps -> {output_mp4.name}"
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
                t = frame_idx / self.fps
                progress = frame_idx / max(1, total_frames - 1)

                # Camera motion: slow cinematic drift downwards (simulating depth descent)
                cam_x = int((0.5 - 0.5 * math.cos(progress * math.pi * 0.8)) * (max_dx * 0.7))
                cam_y = int(progress * (max_dy * 0.9))

                # Determine active stage and compute morph/transition
                frame_img = None
                for i in range(len(stages)):
                    _p, st, et, mode = stages[i]
                    if st <= t < et or (i == len(stages) - 1 and t >= st):
                        stage_dur = max(0.001, et - st)
                        stage_progress = (t - st) / stage_dur
                        img_curr = stage_imgs[i]

                        # Apply stage-specific authentic explanatory object animation
                        if "vibration" in mode:
                            # 1. Covalent bond vibration, shockwave propagation, and bond rupture
                            vib_amp = 1.0 + 3.0 * stage_progress
                            vib_offset = int(vib_amp * math.sin(t * 32.0 * math.pi))
                            crop_x = max(0, min(max_dx, cam_x + vib_offset))
                            crop_y = max(0, min(max_dy, cam_y))
                            curr_frame = img_curr.crop((crop_x, crop_y, crop_x + self.width, crop_y + self.height))

                            # Bloom lighting as shockwave arrives
                            if stage_progress > 0.65:
                                bloom_t = (stage_progress - 0.65) / 0.35
                                flash = 0.25 * math.sin(bloom_t * math.pi)
                                curr_frame = ImageEnhance.Brightness(curr_frame).enhance(1.0 + flash)

                            curr_frame = self._draw_hydrocarbon_dissociation_layer(curr_frame, stage_progress, t)

                        elif "nucleation" in mode:
                            # 2. Free carbon atom inward migration and sp3 crystal lattice nucleation
                            curr_frame = img_curr.crop((cam_x, cam_y, cam_x + self.width, cam_y + self.height))
                            pulse = 0.05 * math.sin(t * 8.0)
                            curr_frame = ImageEnhance.Contrast(curr_frame).enhance(1.0 + pulse)
                            curr_frame = self._draw_carbon_nucleation_layer(curr_frame, stage_progress, t)

                        else:  # diamond caustics and sinking
                            # 3. Rotating 3D octahedral diamond with prismatic caustics and fluid descent
                            sink_offset = int(12.0 * math.sin(t * 1.5))
                            crop_x = max(0, min(max_dx, cam_x + sink_offset))
                            crop_y = max(0, min(max_dy, cam_y))
                            curr_frame = img_curr.crop((crop_x, crop_y, crop_x + self.width, crop_y + self.height))
                            curr_frame = self._draw_3d_diamond_crystal_layer(curr_frame, stage_progress, t)

                        # Handle cross-fade into next stage during transition overlap
                        transition_window = 0.40  # 0.4s smooth optical cross-dissolve between stages
                        time_to_end = et - t
                        if time_to_end < transition_window and i < len(stages) - 1:
                            next_raw = stage_imgs[i + 1].crop((cam_x, cam_y, cam_x + self.width, cam_y + self.height))
                            # Draw next stage's initial state for seamless transition
                            if "nucleation" in stages[i + 1][3]:
                                next_frame = self._draw_carbon_nucleation_layer(next_raw, 0.0, t)
                            else:
                                next_frame = self._draw_3d_diamond_crystal_layer(next_raw, 0.0, t)
                            alpha = 0.5 - 0.5 * math.cos((1.0 - time_to_end / transition_window) * math.pi)
                            curr_frame = Image.blend(curr_frame, next_frame, alpha)

                        frame_img = curr_frame
                        break

                if frame_img is None:
                    frame_img = stage_imgs[-1].crop((cam_x, cam_y, cam_x + self.width, cam_y + self.height))

                self._apply_editorial_overlays(frame_img, branding_badge, None, t)
                proc.stdin.write(frame_img.tobytes())

            proc.stdin.close()
            proc.wait()

            if proc.returncode != 0:
                err = proc.stderr.read().decode("utf-8", errors="replace")
                raise RuntimeError(f"FFmpeg multi-stage render failed: {err}")

        except Exception as e:
            if proc.poll() is None:
                proc.kill()
            raise e

        logger.info(f"Rendered multi-stage transformation clip {output_mp4.name} ({output_mp4.stat().st_size / (1024*1024):.2f} MB).")
        return output_mp4

    def _apply_optical_shockwave_refraction(
        self, frame: Image.Image, cx: int, cy: int, shock_r: float, amp: float = 14.0
    ) -> Image.Image:
        """Apply Snell-like optical shockwave refraction distortion to image pixels."""
        if shock_r < 25 or shock_r > 1200:
            return frame
        x0 = max(0, int(cx - shock_r - 70))
        x1 = min(self.width, int(cx + shock_r + 70))
        y0 = max(0, int(cy - shock_r - 70))
        y1 = min(self.height, int(cy + shock_r + 70))
        bw, bh = x1 - x0, y1 - y0
        if bw <= 0 or bh <= 0:
            return frame

        arr = np.array(frame)
        patch = arr[y0:y1, x0:x1]

        y, x = np.ogrid[:bh, :bw]
        rx = (x + x0) - cx
        ry = (y + y0) - cy
        r = np.hypot(rx, ry)
        r_safe = np.maximum(r, 1e-4)

        # Refractive ripple: Gaussian-damped Snell lens distortion
        sigma = 35.0
        ripple = amp * np.sin(0.12 * (r - shock_r)) * np.exp(-((r - shock_r) / sigma) ** 2)

        dx = (rx / r_safe) * ripple
        dy = (ry / r_safe) * ripple

        map_x = np.clip(x + dx, 0, bw - 1).astype(np.int32)
        map_y = np.clip(y + dy, 0, bh - 1).astype(np.int32)

        # Refract patch with chromatic dispersion
        refracted = patch.copy()
        refracted[:, :, 0] = patch[np.clip(y + dy * 1.15, 0, bh - 1).astype(np.int32), np.clip(x + dx * 1.15, 0, bw - 1).astype(np.int32), 0]
        refracted[:, :, 1] = patch[map_y, map_x, 1]
        refracted[:, :, 2] = patch[np.clip(y + dy * 0.85, 0, bh - 1).astype(np.int32), np.clip(x + dx * 0.85, 0, bw - 1).astype(np.int32), 2]

        arr[y0:y1, x0:x1] = refracted
        return Image.fromarray(arr)

    def _draw_hydrocarbon_dissociation_layer(
        self,
        base_frame: Image.Image,
        stage_progress: float,
        t: float,
    ) -> Image.Image:
        """Render coherent molecular transformation: optical shockwave refraction, 3D bond vibration and rupture."""
        # Center coordinates for molecular core
        cx = 540
        cy = 820 + int(18 * math.sin(t * 2.0))

        # 1. Optical shockwave refraction directly warping the background image
        shock_phase = (stage_progress * 2.2) % 1.0
        shock_r = float(140 + shock_phase * 720)
        amp = float(max(0.0, 16.0 * (1.0 - shock_phase)))
        warped_frame = self._apply_optical_shockwave_refraction(base_frame, cx, cy, shock_r, amp)

        overlay = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay, "RGBA")

        # 4 hydrogen atoms in 3D tetrahedral projection
        angles = [0.85, 2.25, 3.90, 5.30]
        base_dist = 175.0

        # Covalent bond vibration (18 Hz)
        vib_freq = 18.0 * (1.0 + stage_progress)
        vib_offset = 5.0 * math.sin(t * vib_freq * math.pi)

        # Covalent bond rupture begins around stage_progress > 0.40
        if stage_progress < 0.40:
            sep_factor = 0.0
        else:
            sep_norm = (stage_progress - 0.40) / 0.60
            sep_factor = (sep_norm ** 1.6) * 480.0

        for k, angle in enumerate(angles):
            dist = base_dist + vib_offset + sep_factor
            hx = cx + int(dist * math.cos(angle))
            hy = cy + int(dist * math.sin(angle))

            # 3D Covalent bond: cylindrical beam with energy core
            if sep_factor < 120:
                bond_w = max(2, int(8 * (1.0 - sep_factor / 150.0)))
                draw.line([(cx, cy), (hx, hy)], fill=(80, 210, 255, 190), width=bond_w)
                draw.line([(cx, cy), (hx, hy)], fill=(255, 255, 255, 220), width=max(1, bond_w // 2))
            elif sep_factor < 260:
                # Organic plasma discharge filaments across breaking bonds
                arc_points = [(cx, cy)]
                steps = 6
                for step in range(1, steps):
                    frac = step / steps
                    mid_x = cx + int(frac * (hx - cx)) + int(16 * math.sin(t * 32 + step * 2.3))
                    mid_y = cy + int(frac * (hy - cy)) + int(16 * math.cos(t * 32 + step * 2.3))
                    arc_points.append((mid_x, mid_y))
                arc_points.append((hx, hy))
                for ap_idx in range(len(arc_points) - 1):
                    draw.line([arc_points[ap_idx], arc_points[ap_idx + 1]], fill=(140, 240, 255, 220), width=3)
                    draw.line([arc_points[ap_idx], arc_points[ap_idx + 1]], fill=(255, 255, 255, 240), width=1)

            # Volumetric 3D Hydrogen Sphere (white core + specular Phong highlight + cyan diffuse halo)
            hr = 26
            if sep_factor > 20:
                wake_len = min(80, int(sep_factor * 0.4))
                wx = hx - int(wake_len * math.cos(angle))
                wy = hy - int(wake_len * math.sin(angle))
                draw.line([(wx, wy), (hx, hy)], fill=(0, 200, 255, 90), width=10)

            # Diffuse glow & volumetric gradient
            draw.ellipse([hx - hr - 14, hy - hr - 14, hx + hr + 14, hy + hr + 14], fill=(0, 210, 255, 55))
            draw.ellipse([hx - hr, hy - hr, hx + hr, hy + hr], fill=(225, 245, 255, 240))
            # 3D Specular highlight
            draw.ellipse([hx - 9, hy - 11, hx - 2, hy - 4], fill=(255, 255, 255, 255))

        # Central Carbon Atom Core (heated under hyperbaric shock)
        cr = 46
        core_heat = min(1.0, stage_progress * 1.2)
        r_col = int(20 + 200 * core_heat)
        g_col = int(180 + 70 * (1.0 - core_heat))
        b_col = int(255 * (1.0 - 0.4 * core_heat))
        draw.ellipse([cx - cr - 26, cy - cr - 26, cx + cr + 26, cy + cr + 26], fill=(r_col, g_col, b_col, 50))
        draw.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=(r_col, g_col, b_col, 220))
        draw.ellipse([cx - cr + 10, cy - cr + 8, cx - cr + 26, cy - cr + 24], fill=(255, 255, 255, 230))

        return Image.alpha_composite(warped_frame.convert("RGBA"), overlay).convert("RGB")

    def _draw_carbon_nucleation_layer(
        self,
        base_frame: Image.Image,
        stage_progress: float,
        t: float,
    ) -> Image.Image:
        """Render converging free carbon atoms coalescing into sp3 diamond crystal lattice seed."""
        overlay = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay, "RGBA")

        cx = 540
        cy = 840 + int(15 * math.sin(t * 1.5))

        conv_t = min(1.0, stage_progress * 1.2)
        conv_s = 1.0 - (1.0 - conv_t) ** 3

        outer_angles = [0.0, 1.05, 2.09, 3.14, 4.19, 5.24]
        r_start = 450.0
        r_target = 135.0
        r_curr = r_start * (1.0 - conv_s) + r_target * conv_s

        carbon_positions = [(cx, cy)]
        for angle in outer_angles:
            swirl = (1.0 - conv_s) * 0.8
            ax = cx + int(r_curr * math.cos(angle + swirl))
            ay = cy + int(r_curr * math.sin(angle + swirl))
            carbon_positions.append((ax, ay))

        # Dynamic convergent particle wake lines under hyperbaric compression
        if conv_s < 0.95:
            for angle in outer_angles:
                tail_len = int(80 * (1.0 - conv_s))
                tx = cx + int((r_curr + tail_len) * math.cos(angle))
                ty = cy + int((r_curr + tail_len) * math.sin(angle))
                hx = cx + int(r_curr * math.cos(angle))
                hy = cy + int(r_curr * math.sin(angle))
                draw.line([(tx, ty), (hx, hy)], fill=(0, 220, 255, int(90 * (1.0 - conv_s))), width=4)

        # Covalent bonding beams locking in
        if conv_s > 0.45:
            bond_lock = (conv_s - 0.45) / 0.55
            bond_alpha = int(220 * bond_lock)
            for i in range(1, len(carbon_positions)):
                draw.line([(cx, cy), carbon_positions[i]], fill=(0, 240, 255, bond_alpha), width=4)
                draw.line([(cx, cy), carbon_positions[i]], fill=(255, 255, 255, int(bond_alpha * 0.8)), width=1)
                next_i = 1 if i == len(carbon_positions) - 1 else i + 1
                draw.line([carbon_positions[i], carbon_positions[next_i]], fill=(0, 190, 240, int(bond_alpha * 0.6)), width=2)

        # Draw plasma arcs across forming lattice
        arc_prob = math.sin(t * 16.0)
        if arc_prob > 0.3 and len(carbon_positions) > 3:
            p1 = carbon_positions[int(abs(math.sin(t * 7)) * 6) + 1]
            p2 = carbon_positions[int(abs(math.cos(t * 5)) * 6) + 1]
            draw.line([p1, p2], fill=(160, 240, 255, 180), width=2)

        # Draw carbon atom nodes
        for idx, (px, py) in enumerate(carbon_positions):
            node_r = 34 if idx == 0 else 24
            draw.ellipse([px - node_r - 10, py - node_r - 10, px + node_r + 10, py + node_r + 10], fill=(0, 200, 255, 50))
            draw.ellipse([px - node_r, py - node_r, px + node_r, py + node_r], fill=(30, 45, 75, 230), outline=(0, 230, 255, 210), width=2)
            draw.ellipse([px - 6, py - 8, px, py - 2], fill=(220, 245, 255, 240))

        # Central lattice crystallization flash
        if stage_progress > 0.75:
            flash_t = (stage_progress - 0.75) / 0.25
            flash_r = int(200 * math.sin(flash_t * math.pi))
            draw.ellipse([cx - flash_r, cy - flash_r, cx + flash_r, cy + flash_r], fill=(200, 245, 255, int(110 * math.sin(flash_t * math.pi))))

        return Image.alpha_composite(base_frame.convert("RGBA"), overlay).convert("RGB")

    def _draw_3d_diamond_crystal_layer(
        self,
        base_frame: Image.Image,
        stage_progress: float,
        t: float,
    ) -> Image.Image:
        """Render a 3D faceted octahedral diamond crystal rotating, refracting caustics, and sinking through mantle fluid."""
        overlay = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay, "RGBA")

        # Downward gravitational descent coordinates
        cx = 540
        start_y = 680
        total_sink = 320.0
        cy = int(start_y + stage_progress * total_sink)

        # Fluid streamlines moving upward past sinking diamond
        streamline_count = 12
        for s_idx in range(streamline_count):
            sx = int(cx - 360 + (s_idx * 60) + 15 * math.sin(s_idx + t))
            sy_base = (t * 220 + s_idx * 160) % self.height
            sy_start = int(self.height - sy_base)
            sy_end = sy_start - int(120 + 40 * math.sin(s_idx))
            draw.line([(sx, sy_start), (sx, sy_end)], fill=(0, 215, 255, 35), width=2)

        # 3D Octahedral Diamond Geometry
        H = 240.0
        R = 190.0
        rot_y = t * 1.35
        tilt_x = 0.26

        v_top = np.array([0.0, -H, 0.0])
        v_bot = np.array([0.0, +H, 0.0])
        equator = []
        for i in range(4):
            phi = rot_y + i * (math.pi / 2.0)
            equator.append(np.array([R * math.cos(phi), 0.0, R * math.sin(phi)]))

        def project_3d(v: np.ndarray) -> tuple[float, float, float]:
            x, y, z = v[0], v[1], v[2]
            cos_tx, sin_tx = math.cos(tilt_x), math.sin(tilt_x)
            y_rot = y * cos_tx - z * sin_tx
            z_rot = y * sin_tx + z * cos_tx
            return cx + x, cy + y_rot, z_rot

        p_top = project_3d(v_top)
        p_bot = project_3d(v_bot)
        p_eq = [project_3d(v) for v in equator]

        facets = [
            (p_top, p_eq[0], p_eq[1]),
            (p_top, p_eq[1], p_eq[2]),
            (p_top, p_eq[2], p_eq[3]),
            (p_top, p_eq[3], p_eq[0]),
            (p_bot, p_eq[1], p_eq[0]),
            (p_bot, p_eq[2], p_eq[1]),
            (p_bot, p_eq[3], p_eq[2]),
            (p_bot, p_eq[0], p_eq[3]),
        ]

        light_dir = np.array([-0.35, -0.65, -0.67])
        light_dir = light_dir / np.linalg.norm(light_dir)

        # Prismatic caustic rays radiating from vertices
        for pt in [p_top, p_bot, p_eq[0], p_eq[2]]:
            px, py, _ = pt
            c_angle = rot_y * 1.5 + px * 0.01
            for beam in range(3):
                b_ang = c_angle + beam * (2.0 * math.pi / 3.0)
                ray_len = 160.0 + 40.0 * math.sin(t * 5.0 + beam)
                bx = px + ray_len * math.cos(b_ang)
                by = py + ray_len * math.sin(b_ang)
                c_colors = [(180, 100, 255, 60), (0, 220, 255, 75), (255, 215, 80, 60)]
                draw.polygon([(px, py), (bx - 12, by + 12), (bx + 12, by - 12)], fill=c_colors[beam])

        def facet_z(f):
            return (f[0][2] + f[1][2] + f[2][2]) / 3.0

        sorted_facets = sorted(facets, key=facet_z, reverse=True)

        for pt1, pt2, pt3 in sorted_facets:
            poly2d = [(pt1[0], pt1[1]), (pt2[0], pt2[1]), (pt3[0], pt3[1])]
            v_a = np.array([pt2[0] - pt1[0], pt2[1] - pt1[1], pt2[2] - pt1[2]])
            v_b = np.array([pt3[0] - pt1[0], pt3[1] - pt1[1], pt3[2] - pt1[2]])
            normal = np.cross(v_a, v_b)
            norm_len = np.linalg.norm(normal)
            if norm_len < 1e-6:
                continue
            normal = normal / norm_len

            if normal[2] > 0.05:
                continue

            diff = max(0.15, float(np.dot(-normal, light_dir)))
            view_dir = np.array([0.0, 0.0, -1.0])
            ref_dir = light_dir - 2.0 * np.dot(light_dir, normal) * normal
            spec = max(0.0, float(np.dot(ref_dir, view_dir))) ** 16

            r_val = int(min(255, 140 + 115 * spec + 30 * diff))
            g_val = int(min(255, 210 + 45 * spec))
            b_val = 255
            alpha_val = int(min(240, 130 + 80 * diff + 50 * spec))

            draw.polygon(poly2d, fill=(r_val, g_val, b_val, alpha_val))
            draw.line([poly2d[0], poly2d[1]], fill=(220, 245, 255, 220), width=2)
            draw.line([poly2d[1], poly2d[2]], fill=(220, 245, 255, 220), width=2)
            draw.line([poly2d[2], poly2d[0]], fill=(220, 245, 255, 220), width=2)

            if spec > 0.55:
                centroid_x = int((poly2d[0][0] + poly2d[1][0] + poly2d[2][0]) / 3.0)
                centroid_y = int((poly2d[0][1] + poly2d[1][1] + poly2d[2][1]) / 3.0)
                flare_len = int(45 * spec)
                draw.line([(centroid_x - flare_len, centroid_y), (centroid_x + flare_len, centroid_y)], fill=(255, 255, 255, 250), width=3)
                draw.line([(centroid_x, centroid_y - flare_len), (centroid_x, centroid_y + flare_len)], fill=(255, 255, 255, 250), width=3)
                draw.ellipse([centroid_x - 8, centroid_y - 8, centroid_x + 8, centroid_y + 8], fill=(255, 255, 255, 255))

        return Image.alpha_composite(base_frame.convert("RGBA"), overlay).convert("RGB")

    def _apply_editorial_overlays(
        self,
        img: Image.Image,
        branding_badge: str,
        scientific_label: str | None,
        t: float,
    ) -> None:
        """Apply minimalist Beyond 80 documentary watermark (uncluttered, no fake technical boxes)."""
        draw = ImageDraw.Draw(img, "RGBA")
        font = ImageFont.load_default()

        # Minimalist Beyond 80 Watermark in Top Corner (Y = 85 - 120)
        # Discrete semi-transparent dark pill with subtle cyan status pip
        badge_text = branding_badge.upper()
        badge_len = len(badge_text) * 7
        bx, by = 60, 90
        draw.rounded_rectangle(
            [bx, by, bx + badge_len + 28, by + 32],
            radius=6,
            fill=(8, 12, 20, 160),
            outline=(0, 215, 255, 90),
            width=1,
        )
        # Small glowing status pip
        pip_alpha = int(170 + 70 * math.sin(t * 3.0))
        draw.ellipse([bx + 10, by + 11, bx + 18, by + 19], fill=(0, 215, 255, pip_alpha))
        draw.text((bx + 26, by + 9), badge_text, fill=(225, 235, 245, 220), font=font)
