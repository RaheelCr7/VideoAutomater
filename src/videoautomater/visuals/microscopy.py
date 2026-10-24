"""High-resolution biological microscopy and cellular visualization generator."""

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont


class MicroscopyVisualGenerator:
    """Generates detailed 1080x1920 scientific microscopy visuals for biological and physical phenomena."""

    def __init__(self, width: int = 1080, height: int = 1920):
        self.width = width
        self.height = height

    def _get_font(self, size: int) -> ImageFont.ImageFont:
        for p in [
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/SFCompactText.ttf",
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        ]:
            if Path(p).exists():
                try:
                    return ImageFont.truetype(p, size)
                except Exception:
                    pass
        return ImageFont.load_default()

    def generate_active_tardigrade_scene(self, output_path: Path) -> Path:
        """Render high-definition environmental scanning electron micrograph of active tardigrade on moss."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        img = Image.new("RGB", (self.width, self.height), (6, 18, 22))
        draw = ImageDraw.Draw(img)

        # 1. Organic moss substrate background (moss cells, chloroplasts)
        for y_cell in range(0, self.height, 140):
            for x_cell in range(0, self.width, 140):
                # Polygonal plant cell walls
                draw.rectangle([x_cell + 4, y_cell + 4, x_cell + 136, y_cell + 136], outline=(15, 45, 38), width=3)
                # Chloroplast clusters
                for cp in range(3):
                    cpx = x_cell + 30 + cp * 35
                    cpy = y_cell + 40 + (cp % 2) * 40
                    draw.ellipse([cpx - 14, cpy - 14, cpx + 14, cpy + 14], fill=(12, 60, 42))

        # 2. Tardigrade Morphology (Cylindrical body with 4 articulated segments and paired clawed lobopodia)
        cx, cy = self.width // 2, self.height // 2 - 100

        # Radial bio-illumination glow
        for r in range(400, 50, -25):
            alpha = int(40 * (1.0 - r / 400))
            draw.ellipse([cx - r, cy - int(r * 1.4), cx + r, cy + int(r * 1.4)], outline=(20, 80, 75))

        # Body Segments (Cephalic head + 3 trunk segments + caudal tail)
        segments = [
            (cx, cy - 260, 140, 110, "Cephalic Head & Buccal Ring"),
            (cx, cy - 140, 175, 130, "Trunk Segment I"),
            (cx, cy, 195, 145, "Trunk Segment II"),
            (cx, cy + 150, 180, 135, "Trunk Segment III"),
            (cx, cy + 280, 145, 110, "Caudal Segment IV"),
        ]

        # Draw segmented cuticle
        for sx, sy, rx, ry, _ in segments:
            draw.ellipse([sx - rx, sy - ry, sx + rx, sy + ry], fill=(18, 55, 62), outline=(45, 135, 145), width=4)

        # Articulated Lobopodial Legs with chitinous claws
        leg_offsets = [
            (-180, -130, -260, -110),
            (180, -130, 260, -110),
            (-200, 10, -285, 30),
            (200, 10, 285, 30),
            (-190, 160, -275, 190),
            (190, 160, 275, 190),
            (-150, 290, -220, 340),
            (150, 290, 220, 340),
        ]
        for lx1, ly1, lx2, ly2 in leg_offsets:
            draw.line([(cx + lx1, cy + ly1), (cx + lx2, cy + ly2)], fill=(35, 110, 120), width=18)
            # Claws
            draw.line([(cx + lx2, cy + ly2), (cx + lx2 - 15, cy + ly2 + 25)], fill=(120, 220, 230), width=4)
            draw.line([(cx + lx2, cy + ly2), (cx + lx2 + 15, cy + ly2 + 25)], fill=(120, 220, 230), width=4)

        # Subtle scientific scale overlay
        font_sm = self._get_font(26)
        draw.line([(100, self.height - 300), (350, self.height - 300)], fill=(200, 240, 255), width=4)
        draw.text((100, self.height - 340), "SCALE: 250 µm // ESEM 2.5 kV", fill=(200, 240, 255), font=font_sm)

        img.save(output_path, quality=95)
        return output_path

    def generate_vitrification_matrix_scene(self, output_path: Path) -> Path:
        """Render molecular-scale visualization of intrinsically disordered TDP proteins vitrifying into bioglass."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        img = Image.new("RGB", (self.width, self.height), (12, 10, 28))
        draw = ImageDraw.Draw(img)

        cx, cy = self.width // 2, self.height // 2 - 80

        # Interconnected molecular bioglass lattice
        np.random.seed(42)
        num_nodes = 70
        nodes = []
        for _ in range(num_nodes):
            nx = int(np.random.normal(cx, 320))
            ny = int(np.random.normal(cy, 450))
            if 60 <= nx <= self.width - 60 and 200 <= ny <= self.height - 350:
                nodes.append((nx, ny))

        # Covalent & hydrogen bonding network
        for i, (x1, y1) in enumerate(nodes):
            for j, (x2, y2) in enumerate(nodes[i + 1:], start=i + 1):
                dist = math.hypot(x2 - x1, y2 - y1)
                if dist < 160:
                    alpha_glow = int(220 * (1.0 - dist / 160))
                    col = (110, 80, 220) if dist < 100 else (60, 160, 210)
                    draw.line([(x1, y1), (x2, y2)], fill=col, width=max(1, int(4 * (1.0 - dist / 160))))

        # Protein nodes (TDP vitrification clusters)
        for nx, ny in nodes:
            r = np.random.randint(8, 20)
            draw.ellipse([nx - r, ny - r, nx + r, ny + r], fill=(160, 120, 255), outline=(220, 200, 255), width=2)

        # Vitrification Glass Transition Boundary line
        draw.line([(100, cy + 280), (self.width - 100, cy + 280)], fill=(240, 180, 50), width=3)
        font = self._get_font(28)
        draw.text((100, cy + 295), "VITRIFICATION BOUNDARY // AMORPHOUS BIOGLASS (Tg = -20 °C)", fill=(240, 180, 50), font=font)

        img.save(output_path, quality=95)
        return output_path

    def generate_cryptobiotic_tun_scene(self, output_path: Path) -> Path:
        """Render desiccated cryptobiotic 'tun' state showing suspended metabolic animation."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        img = Image.new("RGB", (self.width, self.height), (10, 14, 20))
        draw = ImageDraw.Draw(img)

        cx, cy = self.width // 2, self.height // 2 - 100

        # Compressed spherical 'tun' organism state (3% residual hydration)
        for r_glow in range(320, 60, -20):
            draw.ellipse([cx - r_glow, cy - int(r_glow * 0.9), cx + r_glow, cy + int(r_glow * 0.9)], outline=(30, 60, 75))

        # Folded compact cuticle body
        draw.ellipse([cx - 240, cy - 200, cx + 240, cy + 200], fill=(22, 38, 48), outline=(80, 170, 190), width=6)

        # Invaginated limb folds
        draw.arc([cx - 200, cy - 140, cx + 200, cy + 140], 30, 150, fill=(70, 140, 160), width=4)
        draw.arc([cx - 180, cy - 80, cx + 180, cy + 80], 210, 330, fill=(70, 140, 160), width=4)

        # Vitrified Core Shield
        draw.ellipse([cx - 130, cy - 110, cx + 130, cy + 110], fill=(15, 60, 75), outline=(130, 230, 255), width=3)

        font = self._get_font(26)
        draw.text((100, self.height - 320), "STATE: CRYPTOBIOSIS // DESICCATED TUN", fill=(140, 220, 240), font=font)
        draw.text((100, self.height - 280), "METABOLIC ACTIVITY: 0.00% // RESIDUAL H2O: 3.1%", fill=(140, 220, 240), font=font)

        img.save(output_path, quality=95)
        return output_path
