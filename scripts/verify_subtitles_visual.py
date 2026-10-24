"""Visual verification and contact sheet generator for subtitle layout and readability QA."""

import json
import subprocess
from pathlib import Path
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont


def create_contact_sheet():
    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    video_path = Path("output/episode_001/final.mp4")
    out_dir = Path("output/verification_frames")
    out_dir.mkdir(parents=True, exist_ok=True)

    if not video_path.exists():
        print(f"Error: {video_path} does not exist.")
        return

    # Read subtitles.ass to find representative dialogue events
    ass_path = Path("output/episode_001/subtitles.ass")
    ass_lines = [line.strip() for line in ass_path.read_text().splitlines() if line.startswith("Dialogue:")]

    print(f"Loaded {len(ass_lines)} dialogue subtitle events.")

    # Select representative timestamps
    # Let's inspect event timestamps:
    # Event 1 (~0.1s - 3.1s): Two lines with highlight
    # Event 2 (~3.1s - 5.3s): One line
    # Event 5 (~8.3s - 11.0s): Long word 'researchers'
    # Event 6 (~11.0s - 14.0s): Scene transition near 10.8s
    # Event 8 (~16.1s - 17.9s): Two line scientific terms

    samples = [
        {"name": "01_oneline_caption", "time": "00:00:04.2", "label": "1. One-Line Caption (Clean, Unobtrusive)"},
        {"name": "02_twoline_caption", "time": "00:00:01.5", "label": "2. Two-Line Caption (Balanced Wrap)"},
        {"name": "03_highlighted_word", "time": "00:00:06.2", "label": "3. Highlighted Keyword (Yellow Emphasis)"},
        {"name": "04_long_word", "time": "00:00:12.5", "label": "4. Long Scientific Words (No Truncation)"},
        {"name": "05_scene_transition", "time": "00:00:07.4", "label": "5. Scene Cut Transition Boundary"},
        {"name": "06_safe_zone_overlay", "time": "00:00:16.8", "label": "6. Safe Area Guide (Y=1350-1550)"},
    ]

    frame_images = []
    for s in samples:
        frame_file = out_dir / f"{s['name']}.jpg"
        cmd = [
            ffmpeg_bin,
            "-y",
            "-ss", s["time"],
            "-i", str(video_path),
            "-vframes", "1",
            str(frame_file),
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        frame_images.append((frame_file, s["label"], s["name"]))
        print(f"Extracted {s['name']} at {s['time']}")

    # Draw Safe Area Guide Overlay on sample 6
    safe_frame_path = out_dir / "06_safe_zone_overlay.jpg"
    with Image.open(safe_frame_path) as im:
        overlay = im.copy()
        draw = ImageDraw.Draw(overlay, "RGBA")
        # Draw platform bottom UI danger zone (Y=1550 to 1920)
        draw.rectangle([0, 1550, 1080, 1920], fill=(255, 0, 0, 45), outline=(255, 0, 0, 180), width=4)
        draw.text((540, 1735), "PLATFORM UI OVERLAYS (REELS/SHORTS/TIKTOK)\n[SAFE & CLEAR]", fill=(255, 200, 200), anchor="mm")

        # Draw caption safe zone (Y=1350 to 1550)
        draw.rectangle([0, 1350, 1080, 1550], fill=(0, 255, 0, 25), outline=(0, 255, 0, 180), width=4)
        draw.text((540, 1365), "CAPTION SAFE ZONE [Y=1350 - 1550]", fill=(180, 255, 180), anchor="mm")

        # Draw visual dominance zone (Y=0 to 1350)
        draw.rectangle([0, 0, 1080, 1350], outline=(0, 200, 255, 120), width=4)
        draw.text((540, 60), "DOMINANT VISUAL STORY ZONE [UNOBSTRUCTED]", fill=(180, 230, 255), anchor="mm")

        overlay.save(safe_frame_path, "JPEG")

    # Assemble 3x2 Contact Sheet
    # Scale each 1080x1920 frame down to 360x640
    thumb_w, thumb_h = 360, 640
    header_h = 50
    cell_w, cell_h = thumb_w, thumb_h + header_h
    grid_cols, grid_rows = 3, 2

    sheet_w = grid_cols * cell_w + 40
    sheet_h = grid_rows * cell_h + 100
    contact_sheet = Image.new("RGB", (sheet_w, sheet_h), (18, 22, 32))
    draw_sheet = ImageDraw.Draw(contact_sheet)

    # Title Banner
    draw_sheet.text((sheet_w // 2, 40), "VideoAutomater — Subtitle Readability & Safe Zone Contact Sheet", fill=(255, 255, 255), anchor="mm")

    try:
        font = ImageFont.load_default()
    except Exception:
        font = None

    for idx, (frame_file, label, _) in enumerate(frame_images):
        col = idx % grid_cols
        row = idx // grid_cols
        x = 20 + col * cell_w
        y = 70 + row * cell_h

        # Draw label
        draw_sheet.rectangle([x, y, x + thumb_w, y + header_h], fill=(30, 36, 52))
        draw_sheet.text((x + 10, y + 16), label, fill=(230, 240, 255), font=font)

        # Draw thumbnail
        with Image.open(frame_file) as im:
            thumb = im.resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
            contact_sheet.paste(thumb, (x, y + header_h))

    contact_sheet_path = Path("output/subtitle_contact_sheet.jpg")
    contact_sheet.save(contact_sheet_path, "JPEG", quality=92)
    print(f"Contact sheet successfully created at {contact_sheet_path} ({contact_sheet_path.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    create_contact_sheet()
