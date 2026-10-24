---
name: media-engineering
description: Media sourcing, programmatic graphics, neural narration, subtitle alignment, and FFmpeg master video assembly.
---

# Media Engineering Development Skill

## Purpose
Guides the Media Engineering role in producing high-retention, broadcast-quality 1080x1920 vertical videos.

## Core Rules
1. **Video Specifications**:
   - Resolution: `1080x1920` (9:16 vertical)
   - Duration: $80.0\text{s} \pm 2.0\text{s}$
   - Codec: H.264 (yuv420p) + AAC audio
   - Frame rate: 30.0 fps
2. **Visual Pacing**: Cut or motion shift every 2.5–4.0 seconds. Use Ken Burns zoom/pan and crossfades.
3. **Programmatic Graphics**: When external stock imagery is unsuitable or non-free, generate high-res 1080x1920 graphics using Pillow, SVGwrite, and Matplotlib.
4. **Subtitles**: Perfectly synchronized word-accurate captions positioned in the lower-middle safe zone (160px from bottom) to avoid platform UI clipping.
5. **Audio Mixing**: Clear voiceover normalized to -14 LUFS, background ambient music bed at -22 dB with subtle ducking under speech.
