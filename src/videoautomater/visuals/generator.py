"""Programmatic visual asset synthesis and storyboard compilation."""

import logging
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from videoautomater.models.media import Storyboard, StoryboardScene
from videoautomater.models.script import StoryScript

logger = logging.getLogger(__name__)


class VisualAssetGenerator:
    """Generates high-resolution 1080x1920 vertical scenes with dynamic typography and motion cues."""

    def __init__(self, width: int = 1080, height: int = 1920):
        self.width = width
        self.height = height

    def _get_font(self, size: int) -> ImageFont.ImageFont:
        """Load default or system TrueType font."""
        try:
            # Common macOS font paths
            for path in [
                "/System/Library/Fonts/Helvetica.ttc",
                "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
                "/System/Library/Fonts/SFCompactText.ttf",
            ]:
                if Path(path).exists():
                    return ImageFont.truetype(path, size)
        except Exception:
            pass
        return ImageFont.load_default()

    def create_gradient_canvas(
        self, top_color: tuple[int, int, int], bottom_color: tuple[int, int, int]
    ) -> Image.Image:
        """Create a smooth vertical gradient canvas at 1080x1920."""
        base = Image.new("RGB", (self.width, self.height), top_color)
        draw = ImageDraw.Draw(base)

        for y in range(self.height):
            ratio = y / float(self.height)
            r = int(top_color[0] + (bottom_color[0] - top_color[0]) * ratio)
            g = int(top_color[1] + (bottom_color[1] - top_color[1]) * ratio)
            b = int(top_color[2] + (bottom_color[2] - top_color[2]) * ratio)
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))

        return base

    def render_scene_frame(
        self,
        scene_idx: int,
        title: str,
        category: str,
        role: str,
        theme: str,
        output_path: Path,
    ) -> Path:
        """Render a single high-definition vertical 1080x1920 scene image."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Color themes based on scene narrative role
        color_palettes = {
            "HOOK": ((10, 15, 35), (75, 20, 90)),       # Deep cosmic purple/indigo
            "MYSTERY": ((5, 20, 45), (15, 55, 80)),     # Deep oceanic cyan
            "REVELATION": ((25, 10, 40), (120, 40, 60)), # Laser shock crimson
            "ESCALATION": ((40, 15, 10), (160, 60, 20)), # Thermal incandescent amber
            "CLIMAX": ((20, 25, 40), (40, 120, 160)),   # Liquid diamond cyan glow
            "PAYOFF": ((10, 10, 25), (30, 45, 90)),     # Cosmic deep blue
        }

        top_col, bot_col = color_palettes.get(role, ((10, 15, 30), (30, 40, 70)))
        img = self.create_gradient_canvas(top_col, bot_col)
        draw = ImageDraw.Draw(img)

        # 1. Kinetic Background Elements (particles, nebular circles, grid)
        # Decorative orbital rings
        center_x, center_y = self.width // 2, self.height // 2 - 120
        radius = 280 + (scene_idx % 4) * 35
        draw.ellipse(
            [center_x - radius, center_y - radius, center_x + radius, center_y + radius],
            outline=(255, 255, 255, 45),
            width=3,
        )

        inner_rad = radius - 80
        draw.ellipse(
            [center_x - inner_rad, center_y - inner_rad, center_x + inner_rad, center_y + inner_rad],
            outline=(200, 220, 255, 60),
            width=2,
        )

        # Decorative planetary/crystal core glow
        core_rad = 120
        for r_glow in range(core_rad, 20, -10):
            alpha = int(120 * (1.0 - (r_glow / core_rad)))
            draw.ellipse(
                [center_x - r_glow, center_y - r_glow, center_x + r_glow, center_y + r_glow],
                fill=(255, 255, 255, alpha),
            )

        # Particle stars
        import random
        rng = random.Random(scene_idx * 42)
        for _ in range(120):
            px = rng.randint(40, self.width - 40)
            py = rng.randint(100, self.height - 350)
            size = rng.randint(2, 5)
            brightness = rng.randint(140, 255)
            draw.ellipse([px, py, px + size, py + size], fill=(brightness, brightness, brightness))

        # 2. Category & Stage Badge (Top Safe Area: y=200px)
        badge_font = self._get_font(28)
        badge_text = f"● {category.upper()} // {role}"
        draw.rounded_rectangle([center_x - 220, 220, center_x + 220, 280], radius=30, fill=(0, 0, 0, 160), outline=(255, 255, 255, 120), width=2)
        draw.text((center_x, 250), badge_text, fill=(240, 240, 255), font=badge_font, anchor="mm")

        # 3. Main Narrative Visual Title (Middle Display: y=980px)
        title_font = self._get_font(52)
        words = title.upper().split()
        lines = []
        cur_line = []
        for w in words:
            cur_line.append(w)
            if len(" ".join(cur_line)) > 18:
                lines.append(" ".join(cur_line))
                cur_line = []
        if cur_line:
            lines.append(" ".join(cur_line))

        y_offset = center_y + 360
        for line in lines[:3]:
            # Glow shadow
            draw.text((center_x + 3, y_offset + 3), line, fill=(0, 0, 0, 200), font=title_font, anchor="mm")
            draw.text((center_x, y_offset), line, fill=(255, 255, 255), font=title_font, anchor="mm")
            y_offset += 65

        # 4. Technical Metric or Scientific Badge
        metric_font = self._get_font(30)
        metrics = [
            "ATMOSPHERIC DEPTH: 12,000 KM",
            "PRESSURE: 100,000+ ATMOSPHERES",
            "CORE TEMPERATURE: 4,000° C",
            "CRYSTALLIZATION: 99.8% PURE CARBON",
            "STATE: SUPERCRITICAL HYDROGEN",
            "EVIDENCE: NATURE PHYSICS & NASA JUNO",
        ]
        metric_text = metrics[scene_idx % len(metrics)]
        draw.text((center_x, y_offset + 40), metric_text, fill=(180, 220, 255), font=metric_font, anchor="mm")

        img.save(str(output_path), "PNG")
        return output_path

    def compile_storyboard(
        self, script: StoryScript, assets_dir: Path, target_duration: float = 80.0
    ) -> Storyboard:
        """Create a complete storyboard with a visual scene change every 3.0 to 4.0 seconds."""
        assets_dir.mkdir(parents=True, exist_ok=True)
        scenes: list[StoryboardScene] = []

        # Scale number of scenes based on target duration (approx 1 scene every 3.6s)
        num_scenes = max(3, min(22, int(round(target_duration / 3.6))))
        scene_duration = target_duration / num_scenes

        motion_effects = [
            "KEN_BURNS_ZOOM_IN",
            "PAN_LEFT",
            "KEN_BURNS_ZOOM_OUT",
            "PAN_RIGHT",
        ]

        # Titles and themes matching the 6 sections
        scene_titles = [
            ("DIAMOND PRECIPITATION", "HOOK", "Deep Cosmic"),
            ("JUPITER'S CLOUD DECK", "HOOK", "Atmospheric"),
            ("THE MISSING CARBON", "MYSTERY", "Spectrometry"),
            ("ANOMALOUS DATA", "MYSTERY", "Probe telemetry"),
            ("PRESSURE THRESHOLD", "MYSTERY", "Deep interior"),
            ("LABORATORY LASER SHOCK", "REVELATION", "Shockwave physics"),
            ("PYROLYSIS BREAKTHROUGH", "REVELATION", "Methane separation"),
            ("CRYSTAL LATTICE FORMS", "REVELATION", "Diamond compression"),
            ("FALLING BOULDERS", "REVELATION", "Hail formation"),
            ("TERMINAL VELOCITY", "ESCALATION", "Plunge into hydrogen"),
            ("SUPERCRITICAL HYDROGEN", "ESCALATION", "Crushing depths"),
            ("EXTREME FRICTION HEAT", "ESCALATION", "Thermal vaporization"),
            ("INCANDESCENT SHOWER", "ESCALATION", "Atmospheric storm"),
            ("DEEPER MANTLE DESCENT", "ESCALATION", "Tungsten melting point"),
            ("LIQUID DIAMOND COLLAPSE", "CLIMAX", "Extreme pressure"),
            ("SUBTERRANEAN OCEANS", "CLIMAX", "Molten carbon sea"),
            ("FLOATING DIAMOND BERGS", "CLIMAX", "Hydrocarbon mantle"),
            ("ENDLESS SHIMMERING CORE", "CLIMAX", "Planetary depth"),
            ("COSMIC PERSPECTIVE", "PAYOFF", "Deep universe"),
            ("EARTH'S RAREST GEM", "PAYOFF", "Comparative science"),
            ("SOLAR SYSTEM WONDER", "PAYOFF", "Cosmic storm"),
            ("UNENDING THUNDERSTORM", "PAYOFF", "Jupiter master payoff"),
        ]

        for idx in range(num_scenes):
            start_t = round(idx * scene_duration, 2)
            end_t = round(min((idx + 1) * scene_duration, target_duration), 2)
            dur = round(end_t - start_t, 2)

            title_info = scene_titles[idx] if idx < len(scene_titles) else ("COSMIC REVELATION", "PAYOFF", "Science")
            title_text, role, theme = title_info

            file_path = assets_dir / f"scene_{idx+1:02d}.png"
            self.render_scene_frame(
                scene_idx=idx + 1,
                title=title_text,
                category="SCIENCE",
                role=role,
                theme=theme,
                output_path=file_path,
            )

            scene = StoryboardScene(
                scene_id=f"scene_{idx+1:02d}",
                start_time=start_t,
                end_time=end_t,
                duration=dur,
                asset_type="SYNTHETIC_CANVAS",
                asset_source="programmatic_render",
                local_file_path=str(file_path),
                motion_effect=motion_effects[idx % len(motion_effects)],
                transition_in="FADE",
                transition_duration=0.3,
                overlay_title=title_text,
                narration_cue=f"Phase: {role}",
            )
            scenes.append(scene)

        storyboard = Storyboard(
            storyboard_id=f"sb_{script.script_id}",
            script_id=script.script_id,
            total_duration=target_duration,
            scenes=scenes,
        )
        logger.info(f"Storyboard compiled: {len(scenes)} scenes spanning {target_duration}s.")
        return storyboard
