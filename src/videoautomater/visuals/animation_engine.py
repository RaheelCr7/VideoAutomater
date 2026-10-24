"""High-Performance Motion Graphics and Explanatory Animation Engine.

Renders 1080x1920 30FPS H.264 scientific and documentary animation clips.
"""

import logging
import math
import subprocess
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from videoautomater.models.animation import SceneAnimationSpec

logger = logging.getLogger(__name__)


class AnimationEngine:
    """Renders structured SceneAnimationSpec specifications into high-definition 1080x1920 30fps MP4 clips."""

    def __init__(self, width: int = 1080, height: int = 1920, fps: int = 30):
        self.width = width
        self.height = height
        self.fps = fps
        self.ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()

    def render_scene_clip(self, spec: SceneAnimationSpec, output_mp4: Path) -> Path:
        """Render a single scene animation into an MP4 clip."""
        output_mp4.parent.mkdir(parents=True, exist_ok=True)
        duration = spec.duration
        total_frames = max(1, int(round(duration * self.fps)))

        logger.info(
            f"Rendering animation scene '{spec.scene_id}' ({spec.template_name}): "
            f"{duration:.2f}s, {total_frames} frames @ {self.fps}fps -> {output_mp4.name}"
        )

        # Launch FFmpeg process reading raw RGB24 frames from stdin
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
            "18",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(output_mp4.resolve()),
        ]

        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

        try:
            for frame_idx in range(total_frames):
                t = frame_idx / self.fps
                progress = frame_idx / max(1, total_frames - 1)

                frame_bytes = self._render_frame(spec, t, progress)
                proc.stdin.write(frame_bytes)

            proc.stdin.close()
            proc.wait()

            if proc.returncode != 0:
                err = proc.stderr.read().decode("utf-8", errors="replace")
                raise RuntimeError(f"FFmpeg animation render failed for {spec.scene_id}: {err}")

        except Exception as e:
            if proc.poll() is None:
                proc.kill()
            raise e

        logger.info(f"Rendered {output_mp4.name} successfully ({output_mp4.stat().st_size / 1024:.1f} KB).")
        return output_mp4

    def _render_frame(self, spec: SceneAnimationSpec, t: float, progress: float) -> bytes:
        """Dispatch rendering to appropriate procedural template and return raw RGB bytes."""
        template = spec.template_name.lower()
        if "celestial" in template or "approach" in template:
            img = self._render_celestial_approach(spec, t, progress)
        elif "pressure" in template or "depth" in template:
            img = self._render_pressure_depth_gauge(spec, t, progress)
        elif "molecular" in template or "crystalliz" in template:
            img = self._render_molecular_crystallization(spec, t, progress)
        elif "precipitation" in template or "diamond" in template:
            img = self._render_diamond_precipitation(spec, t, progress)
        else:
            img = self._render_celestial_approach(spec, t, progress)

        # Draw on-screen scientific labels (placed above subtitle safe zone Y < 1350)
        self._overlay_labels(img, spec, t)

        return img.tobytes()

    # -------------------------------------------------------------------------
    # TEMPLATE 1: CELESTIAL APPROACH (Planet Scale, Atmospheric Glow, Probe Arc)
    # -------------------------------------------------------------------------
    def _render_celestial_approach(self, spec: SceneAnimationSpec, t: float, progress: float) -> Image.Image:
        # Base space background with gradient
        img = Image.new("RGB", (self.width, self.height), (4, 7, 16))
        draw = ImageDraw.Draw(img, "RGBA")

        # Static starfield with slight parallax
        np.random.seed(42)
        star_x = np.random.randint(0, self.width, 140)
        star_y = np.random.randint(0, self.height, 140)
        star_b = np.random.randint(120, 255, 140)
        for x, y, b in zip(star_x, star_y, star_b):
            alpha = int(b * (0.8 + 0.2 * math.sin(t * 3.0 + x)))
            draw.point((x, y), fill=(b, b, b, alpha))

        # Camera zoom simulation
        zoom = spec.camera.start_zoom + (spec.camera.end_zoom - spec.camera.start_zoom) * progress
        planet_center_x = 540.0
        planet_center_y = int(750.0 + progress * 40.0)
        base_radius = 320.0
        planet_radius = int(base_radius * zoom)

        # Multi-layer atmospheric glow behind planet
        for r_offset, alpha in [(60, 25), (40, 45), (20, 70), (5, 110)]:
            rad = planet_radius + r_offset
            draw.ellipse(
                [planet_center_x - rad, planet_center_y - rad, planet_center_x + rad, planet_center_y + rad],
                fill=(45, 110, 180, alpha),
            )

        # Jupiter-style planetary disk with atmospheric banding
        bands = [
            (210, 155, 105),  # Light zone
            (175, 115, 75),   # Dark belt
            (225, 175, 125),  # Equator zone
            (160, 95, 60),    # Equatorial belt
            (200, 140, 95),   # Tropical zone
            (150, 90, 55),    # Polar belt
        ]
        # Draw base planet sphere
        draw.ellipse(
            [planet_center_x - planet_radius, planet_center_y - planet_radius, planet_center_x + planet_radius, planet_center_y + planet_radius],
            fill=(180, 125, 80),
        )

        # Atmospheric bands mask
        band_height = int(planet_radius * 2 / len(bands))
        for i, color in enumerate(bands):
            y_top = planet_center_y - planet_radius + i * band_height
            y_bot = y_top + band_height
            # Add slight sinusoidal turbulence shift with time
            turbulence = int(8.0 * math.sin(t * 1.5 + i))
            draw.rectangle(
                [planet_center_x - planet_radius, y_top + turbulence, planet_center_x + planet_radius, y_bot + turbulence],
                fill=(*color, 160),
            )

        # Planet shadow / spherical shading mask on left side for 3D depth
        for step in range(20):
            shade_alpha = int(180 * (1.0 - step / 20.0))
            offset_x = int(planet_radius * (step / 20.0) - planet_radius)
            draw.ellipse(
                [planet_center_x - planet_radius, planet_center_y - planet_radius, planet_center_x + offset_x, planet_center_y + planet_radius],
                fill=(0, 0, 0, shade_alpha),
            )

        # Approaching Spacecraft Probe
        probe_start_x, probe_start_y = 180.0, 380.0
        probe_target_x, probe_target_y = 480.0, 680.0
        probe_x = int(probe_start_x + (probe_target_x - probe_start_x) * progress)
        probe_y = int(probe_start_y + (probe_target_y - probe_start_y) * progress)

        # Trajectory arc path behind probe
        for step in range(max(1, int(progress * 40))):
            p_step = step / 40.0
            tx = int(probe_start_x + (probe_target_x - probe_start_x) * p_step)
            ty = int(probe_start_y + (probe_target_y - probe_start_y) * p_step)
            draw.ellipse([tx - 2, ty - 2, tx + 2, ty + 2], fill=(0, 215, 255, 90))

        # Spacecraft icon & solar panels
        draw.line([probe_x - 30, probe_y, probe_x + 30, probe_y], fill=(0, 215, 255), width=4)
        draw.rectangle([probe_x - 12, probe_y - 12, probe_x + 12, probe_y + 12], fill=(230, 240, 255), outline=(0, 215, 255), width=2)
        # Pulsing telemetry beacon
        beacon_alpha = int(255 * (0.5 + 0.5 * math.sin(t * 8.0)))
        draw.ellipse([probe_x - 4, probe_y - 4, probe_x + 4, probe_y + 4], fill=(255, 215, 0, beacon_alpha))

        return img.convert("RGB")

    # -------------------------------------------------------------------------
    # TEMPLATE 2: PRESSURE & DEPTH GAUGE (Crushing Planetary Atmosphere Compression)
    # -------------------------------------------------------------------------
    def _render_pressure_depth_gauge(self, spec: SceneAnimationSpec, t: float, progress: float) -> Image.Image:
        # Gradient background representing atmospheric darkening with depth
        img = Image.new("RGB", (self.width, self.height), (8, 14, 28))
        draw = ImageDraw.Draw(img, "RGBA")

        # Vertical atmospheric gradient (upper atmosphere cyan -> deep violet -> pitch black)
        for y in range(0, 1300, 10):
            norm_y = y / 1300.0
            r = int(15 * (1.0 - norm_y))
            g = int(45 * (1.0 - norm_y))
            b = int(90 * (1.0 - norm_y) + 20 * norm_y)
            draw.rectangle([0, y, self.width, y + 10], fill=(r, g, b))

        # High-tech Depth & Pressure Telemetry Gauge on Left Edge (X = 90 to 220)
        gauge_top, gauge_bottom = 350, 1200
        gauge_height = gauge_bottom - gauge_top
        current_fill_y = int(gauge_top + gauge_height * progress)

        # Background track
        draw.rectangle([110, gauge_top, 140, gauge_bottom], fill=(25, 35, 55), outline=(60, 80, 120), width=2)
        # Active filling bar (red/orange warning gradient)
        draw.rectangle([112, gauge_top, 138, current_fill_y], fill=(255, 69, 58))

        # Hash marks and readings along gauge
        depth_km = int(progress * 10000)
        pressure_atm = int(1.0 + (progress ** 2) * 99999.0)

        for mark in [0.25, 0.5, 0.75, 1.0]:
            my = int(gauge_top + gauge_height * mark)
            draw.line([95, my, 155, my], fill=(120, 140, 180), width=2)

        # Draw moving compression wavefronts (ripple rings)
        center_x, center_y = 620, 750
        num_waves = 6
        for w in range(num_waves):
            wave_phase = (progress * 3.0 + w / num_waves) % 1.0
            wave_rad = int(30 + wave_phase * 340)
            wave_alpha = int(180 * (1.0 - wave_phase))
            draw.ellipse(
                [center_x - wave_rad, center_y - wave_rad, center_x + wave_rad, center_y + wave_rad],
                outline=(255, 158, 0, wave_alpha),
                width=3,
            )

        # Particle Swarm (Methane & Hydrogen molecules compressing)
        np.random.seed(101)
        num_particles = 90
        base_radii = np.random.uniform(50, 360, num_particles)
        angles = np.random.uniform(0, 2 * math.pi, num_particles)
        # As pressure increases, particles compress inward toward center
        compression = 1.0 - (progress * 0.7)

        for br, ang in zip(base_radii, angles):
            r = br * compression + 10.0 * math.sin(t * 4.0 + ang)
            px = int(center_x + r * math.cos(ang + t * 0.5))
            py = int(center_y + r * math.sin(ang + t * 0.5))
            color = (0, 240, 255) if (br % 2 == 0) else (255, 100, 100)
            draw.ellipse([px - 5, py - 5, px + 5, py + 5], fill=color)

        # Dynamic Telemetry Display Card
        card_x1, card_y1, card_x2, card_y2 = 170, 420, 460, 560
        draw.rectangle([card_x1, card_y1, card_x2, card_y2], fill=(15, 23, 42, 220), outline=(0, 215, 255), width=2)
        font = ImageFont.load_default()
        draw.text((card_x1 + 15, card_y1 + 15), "DEPTH TELEMETRY", fill=(0, 215, 255), font=font)
        draw.text((card_x1 + 15, card_y1 + 45), f"{depth_km:,} KM", fill=(255, 255, 255), font=font)
        draw.text((card_x1 + 15, card_y1 + 80), f"{pressure_atm:,} ATM", fill=(255, 69, 58), font=font)

        return img.convert("RGB")

    # -------------------------------------------------------------------------
    # TEMPLATE 3: MOLECULAR CRYSTALLIZATION (Pyrolysis & Diamond Lattice Assembly)
    # -------------------------------------------------------------------------
    def _render_molecular_crystallization(self, spec: SceneAnimationSpec, t: float, progress: float) -> Image.Image:
        # Dark high-energy quantum laboratory / reaction chamber backdrop
        img = Image.new("RGB", (self.width, self.height), (6, 9, 20))
        draw = ImageDraw.Draw(img, "RGBA")

        center_x, center_y = 540, 720

        # Phase transition occurs at progress ~ 40%
        transition_point = 0.40
        is_dissociating = progress < transition_point
        transform_prog = max(0.0, min(1.0, (progress - transition_point) / (1.0 - transition_point)))

        if is_dissociating:
            # PHASE 1: Methane (CH4) Molecules with vibrating C-H bonds
            dissoc_subprog = progress / transition_point
            draw.text((360, 360), "MOLECULAR STATE: METHANE (CH4)", fill=(48, 209, 88))

            # Central Carbon Atom
            c_rad = 32
            draw.ellipse([center_x - c_rad, center_y - c_rad, center_x + c_rad, center_y + c_rad], fill=(60, 65, 75), outline=(0, 240, 255), width=3)
            draw.text((center_x - 6, center_y - 8), "C", fill=(255, 255, 255))

            # 4 Hydrogen Atoms around carbon
            h_distance = 130 + dissoc_subprog * 120  # Hydrogen atoms flying away
            for i in range(4):
                ang = i * (math.pi / 2) + (t * 0.8)
                hx = int(center_x + h_distance * math.cos(ang))
                hy = int(center_y + h_distance * math.sin(ang))

                # Bond line rupturing
                bond_alpha = int(255 * (1.0 - dissoc_subprog))
                draw.line([center_x, center_y, hx, hy], fill=(0, 215, 255, bond_alpha), width=3)

                # Hydrogen atom
                draw.ellipse([hx - 16, hy - 16, hx + 16, hy + 16], fill=(230, 240, 255), outline=(0, 215, 255), width=2)
                draw.text((hx - 4, hy - 6), "H", fill=(10, 10, 20))

            # Shockwave energy flash when rupture approaches
            if dissoc_subprog > 0.7:
                flash_alpha = int(180 * (dissoc_subprog - 0.7) / 0.3)
                draw.ellipse([center_x - 280, center_y - 280, center_x + 280, center_y + 280], fill=(255, 255, 255, flash_alpha))

        else:
            # PHASE 2: Carbon Lattice Crystallization into Diamond Octahedron
            # Assembly animation
            rot_angle = t * 1.2
            lattice_scale = 140.0 * (0.6 + 0.4 * transform_prog)

            # 3D diamond octahedron vertex projections
            raw_vertices = [
                (0, -1.8, 0),   # Top apex
                (0, 1.8, 0),    # Bottom apex
                (-1.2, 0, -1.2),# Front left
                (1.2, 0, -1.2), # Front right
                (1.2, 0, 1.2),  # Back right
                (-1.2, 0, 1.2), # Back left
            ]

            proj_pts = []
            for vx, vy, vz in raw_vertices:
                # Rotate around Y-axis
                rx = vx * math.cos(rot_angle) + vz * math.sin(rot_angle)
                rz = -vx * math.sin(rot_angle) + vz * math.cos(rot_angle)
                ry = vy
                px = int(center_x + rx * lattice_scale)
                py = int(center_y + ry * lattice_scale)
                proj_pts.append((px, py))

            # Draw diamond facets with alpha shading
            edges = [
                (0, 2), (0, 3), (0, 4), (0, 5),  # Top pyramid edges
                (1, 2), (1, 3), (1, 4), (1, 5),  # Bottom pyramid edges
                (2, 3), (3, 4), (4, 5), (5, 2),  # Equator edges
            ]
            for idx1, idx2 in edges:
                draw.line([proj_pts[idx1], proj_pts[idx2]], fill=(0, 215, 255), width=3)

            # Draw sparkling diamond lattice nodes
            for px, py in proj_pts:
                draw.ellipse([px - 14, py - 14, px + 14, py + 14], fill=(255, 255, 255), outline=(0, 215, 255), width=2)

            # Refraction facet sparkle
            sparkle_alpha = int(255 * (0.5 + 0.5 * math.sin(t * 10.0)))
            draw.line([center_x - 35, center_y, center_x + 35, center_y], fill=(255, 255, 255, sparkle_alpha), width=2)
            draw.line([center_x, center_y - 35, center_x, center_y + 35], fill=(255, 255, 255, sparkle_alpha), width=2)

            draw.text((360, 360), "PHASE: SP3 COVALENT DIAMOND LATTICE", fill=(0, 215, 255))

        return img.convert("RGB")

    # -------------------------------------------------------------------------
    # TEMPLATE 4: DIAMOND PRECIPITATION (Precipitating Diamonds in Mantle Layers)
    # -------------------------------------------------------------------------
    def _render_diamond_precipitation(self, spec: SceneAnimationSpec, t: float, progress: float) -> Image.Image:
        # Deep interior metallic hydrogen mantle (deep dark metallic navy)
        img = Image.new("RGB", (self.width, self.height), (5, 10, 25))
        draw = ImageDraw.Draw(img, "RGBA")

        # Layered geological zones in upper screen
        draw.line([0, 300, self.width, 300], fill=(60, 90, 140), width=2)
        draw.text((50, 270), "MOLECULAR HYDROGEN MANTLE (10,000 KM)", fill=(100, 130, 180))

        draw.line([0, 550, self.width, 550], fill=(120, 70, 180), width=2)
        draw.text((50, 520), "METALLIC HYDROGEN TRANSITION ZONE (20,000 KM)", fill=(180, 120, 255))

        # Falling diamond crystals (precipitation simulation)
        np.random.seed(88)
        num_diamonds = 35
        x_coords = np.random.randint(60, self.width - 60, num_diamonds)
        speeds = np.random.uniform(220.0, 480.0, num_diamonds)
        sizes = np.random.randint(14, 38, num_diamonds)
        phases = np.random.uniform(0, 1000.0, num_diamonds)

        for x, spd, sz, ph in zip(x_coords, speeds, sizes, phases):
            # Calculate falling Y position looping seamlessly across frame
            curr_y = int((ph + t * spd) % (1300 - 320) + 320)

            # Draw diamond octahedron symbol
            d_half = sz // 2
            diamond_pts = [
                (x, curr_y - sz),
                (x + d_half, curr_y),
                (x, curr_y + sz),
                (x - d_half, curr_y),
            ]
            # Diamond body
            draw.polygon(diamond_pts, fill=(240, 248, 255, 210), outline=(0, 215, 255, 255))

            # Sparkle streak
            draw.line([x, curr_y - sz - 10, x, curr_y + sz + 10], fill=(255, 255, 255, 140), width=1)

        # Depth descent indicator bar on right side
        draw.rectangle([980, 320, 1000, 1280], fill=(20, 30, 50), outline=(0, 215, 255))
        indicator_y = int(320 + (1280 - 320) * progress)
        draw.rectangle([975, indicator_y - 6, 1005, indicator_y + 6], fill=(255, 215, 0))

        return img.convert("RGB")

    def _overlay_labels(self, img: Image.Image, spec: SceneAnimationSpec, t: float) -> None:
        """Render active on-screen labels ensuring they never violate subtitle safe zones."""
        draw = ImageDraw.Draw(img, "RGBA")
        font = ImageFont.load_default()

        for lbl in spec.labels:
            if lbl.start_time <= t <= lbl.end_time:
                lx, ly = lbl.position
                # Enforce safe zone constraint: must not be in [1320, 1580]
                if 1320 <= ly <= 1580:
                    ly = 1250.0  # Reposition safely above subtitle zone

                # Draw subtle dark badge pill behind label
                text_len = len(lbl.text) * 8
                draw.rounded_rectangle(
                    [lx - text_len // 2 - 16, ly - 18, lx + text_len // 2 + 16, ly + 22],
                    radius=8,
                    fill=(10, 16, 28, 200),
                    outline=(0, 215, 255, 180),
                    width=1,
                )
                draw.text((lx - text_len // 2, ly - 6), lbl.text, fill=lbl.color, font=font)
