# VideoAutomater — Implementation Plan & Roadmap (V1.0)

## Overview & Progression

This roadmap outlines the phased development of VideoAutomater across six milestones, prioritizing a verified, playable 80-second vertical video pipeline first before layering distribution and cloud automation.

---

## Milestone 1: Foundation & Video Generation Engine
**Primary Acceptance Criterion**: `python -m videoautomater generate --duration 80 --topic auto` produces a complete, verified, playable 80s 1080x1920 MP4 with voice narration, accurate subtitles, and structured episode artifacts in `output/episode_xxx/`.

- **M1.1 Project Bootstrap (`chore/project-bootstrap`)**:
  - Python packaging (`pyproject.toml`), directory tree, dependency declarations.
  - Development agent rules (`AGENTS.md`) and Antigravity skills (`.agents/skills/*`).
  - GitHub Actions CI matrix, pre-commit style, pytest configuration.
  - Baseline documentation and contracts.
- **M1.2 Viral Content Research Agent (`feat/content-research-agent`)**:
  - Raw topic discovery across science, tech, history, space, engineering.
  - Multi-factor scoring matrix (curiosity, novelty, visual potential, relevance, depth, originality).
  - Fact-checking & primary source verification gate.
  - Topic history persistence and semantic duplicate detection.
  - Production of validated `ResearchBrief`.
- **M1.3 Creative Scriptwriting Agent (`feat/scriptwriting-agent`)**:
  - 80-second narrative arc generator (Hook, Mystery, Revelation, Escalation, Climax, Payoff).
  - Multi-hook generation and scoring.
  - Spoken word-count calibration (165–185 words).
  - Production of validated `StoryScript`.
- **M1.4 Media Production & Audio Engine (`feat/video-production-engine`)**:
  - Edge-TTS / local neural narration synthesis with offline fallback.
  - Audio normalization to EBU R128 (-14 LUFS).
  - Subtitle timing and word-level alignment generation (`.srt` / `.ass`).
  - Programmatic visual asset generator (Pillow / SVG / Matplotlib) and licensed image fetching.
  - FFmpeg rendering engine with dynamic Ken Burns zooms, crossfades, and vertical typography overlays.
- **M1.5 Editorial Quality Agent (`feat/video-quality-checker`)**:
  - Automated inspection of duration ($80\text{s} \pm 2\text{s}$), resolution ($1080\times1920$), aspect ratio ($9:16$), codecs (H.264/AAC), loudness, and playability.
  - Full output artifact bundling into `output/episode_xxx/`.

---

## Milestone 2: Agent Control Center (Director's Console)
**Primary Acceptance Criterion**: Authenticated web dashboard allowing the Content Director to configure creative settings, issue natural-language instructions to agents, review scripts/storyboards, and set automation modes.

- **M2.1 Dashboard Core (`feat/agent-control-center-core`)**:
  - FastAPI backend with secure session authentication.
  - Modern, responsive dark-mode UI (HTML5, Vanilla CSS, JS).
- **M2.2 Global Creative Settings & Agent Steering (`feat/agent-guidance`)**:
  - Niche selection, style presets, duration boundaries.
  - Natural-language guidance interface per agent with persistent scope (Global, Campaign, Episode, Temporary).
- **M2.3 Director Feedback Loop**:
  - Feedback input on topics, hooks, and completed videos, persisted for future generation context.

---

## Milestone 3: On-Demand Production & Scheduling
**Primary Acceptance Criterion**: Director can prompt on-demand video creation ("Create video on black holes") or set automated cadences (X/day, X/hour) with configurable review policies (`AUTO_PUBLISH`, `OPTIONAL_REVIEW`, `REQUIRED_APPROVAL`).

- **M3.1 On-Demand Generation Interface (`feat/on-demand-production`)**:
  - Free-form natural-language prompt handler.
  - Interactive job progress tracker.
- **M3.2 Production Scheduler & Durable Queue (`feat/production-scheduler`)**:
  - Chron-based job dispatch (videos per hour / per day).
  - Backlog and rate-limit guardrails.
- **M3.3 Centralized Video Library**:
  - Searchable catalog of generated episodes, status history, review tools, and asset previews.

---

## Milestone 4: Multi-Platform & Multi-Account Publishing
**Primary Acceptance Criterion**: One master MP4 is dispatched cleanly and concurrently to multiple selected accounts across YouTube, Instagram, and Facebook without re-rendering or transcoding.

- **M4.1 Platform Connector Framework (`feat/platform-connector-framework`)**:
  - Reusable abstract connector with token lifecycle, validation, chunked upload, and status polling.
- **M4.2 Account & Destination Registry (`feat/multi-account-publishing`)**:
  - Multi-account management per platform, publishing groups ("Science Network", "History Hub").
  - Independent job tracking, preventing cross-account re-upload failures.
- **M4.3 Specific Connectors**:
  - YouTube Shorts connector (`feat/youtube-publisher`).
  - Instagram Reels connector (`feat/instagram-publisher`).
  - Facebook Page Reels connector (`feat/facebook-publisher`).

---

## Milestone 5: Cloud Deployment & Unattended Operation
**Primary Acceptance Criterion**: Full system operates persistently on Google Cloud Run Jobs + Cloud Scheduler with Secret Manager and budget protection limits.

- **M5.1 Containerization & Cloud Run (`infra/cloud-run-deployment`)**:
  - Multi-stage Dockerfile bundling Python 3.11, FFmpeg, fonts, and dependencies.
  - Job execution configuration with non-root security.
- **M5.2 Secrets & Cloud Scheduler (`infra/cloud-scheduler`)**:
  - Automated triggers in `Asia/Karachi` timezone.
  - Secret Manager integration and zero-cost safeguard enforcement.

---

## Milestone 6: Performance Analytics & Continuous Improvement
**Primary Acceptance Criterion**: Automated ingestion of platform engagement metrics (views, retention, likes, shares) feeding back into topic discovery and hook scoring.

- **M6.1 Metrics Ingestion Engine (`feat/performance-analytics`)**:
  - Periodic polling of authorized platform APIs for 24h, 72h, and 7-day stats.
- **M6.2 Closed-Loop Quality Optimization**:
  - Correlating topic categories and hook styles with actual retention curves.
