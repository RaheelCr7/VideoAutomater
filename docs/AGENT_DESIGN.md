# VideoAutomater — Agent Design & Architecture (V1.0)

This document formalizes the division of labor between **Development Agents** (who build and maintain the codebase) and **Runtime Production Agents** (who execute autonomous video creation and distribution).

---

## 1. Development Agents (Engineering Team Roles)

In accordance with Section 3.A of the Master Architecture, five specialized engineering roles govern the project's evolution.

```
       ┌─────────────────────────────────────────────────────┐
       │              Agent 1: Lead Architect                │
       │    (System Design, Contracts, Code Integration)     │
       └─────────────────────────┬───────────────────────────┘
                                 │
     ┌───────────────────────────┼───────────────────────────┐
     │                           │                           │
┌────┴─────────────────┐ ┌───────┴──────────────┐ ┌──────────┴─────────────┐
│ Agent 2: Content Eng │ │ Agent 3: Media Eng   │ │ Agent 4: Publishing    │
│ (Research, Scripts,  │ │ (Visuals, Audio,     │ │ (Connectors, Queues,   │
│  Topic Ranking)      │ │  FFmpeg Pipeline)    │ │  Multi-Account OAuth)  │
└──────────────────────┘ └──────────────────────┘ └────────────────────────┘
                                 │
       ┌─────────────────────────┴───────────────────────────┐
       │             Agent 5: QA, DevOps & Automation        │
       │     (CI/CD, Pytest, Docker, Cloud Run, Cloud Sched) │
       └─────────────────────────────────────────────────────┘
```

### Agent 1 — Lead Architect
- **Mandate**: Overall system architecture, cross-module data contracts, API designs, tech stack choices, pull request standards, coordination across features.
- **Rule**: Does not bypass automated tests or GitHub feature branch reviews.

### Agent 2 — Content Engineering Agent
- **Mandate**: Research engine, topic discovery, factual claim verification, scriptwriting engine, hook optimization, narrative pacing, anti-duplicate logic.

### Agent 3 — Media Engineering Agent
- **Mandate**: Asset discovery, programmatic graphics generation (Pillow/Matplotlib/SVG), Edge-TTS neural narration, phonetic synchronization, subtitle timing, FFmpeg filtergraph rendering.

### Agent 4 — Publishing & Platform Integration Agent
- **Mandate**: Reusable platform connector framework, YouTube Shorts, Instagram Reels, Facebook Reels, multi-account credential management, upload queue, retry reconciliation.

### Agent 5 — QA, DevOps & Automation Agent
- **Mandate**: Test suites, Docker containerization, GitHub Actions CI workflows, Cloud Run Job deployment specs, Cloud Scheduler, structured telemetry, secret management.

---

## 2. Runtime Production Agents

Runtime agents are the operational components executing in production.

### 2.1 Content Research Agent (`ContentResearchAgent`)
- **Role**: Discovers, scores, fact-checks, and compiles research briefs.
- **Inputs**: Global director instructions, category filters, historical episode topics.
- **Outputs**: Strongly typed `ResearchBrief`.
- **Eligibility Gates**: Rejects any candidate if the central factual premise cannot be corroborated by credible source links.

### 2.2 Creative Scriptwriting Agent (`ScriptwritingAgent`)
- **Role**: Transforms verified research into an emotional, high-tension 80-second script.
- **Structure**:
  - `0–4s`: Immediate hook (no greetings or fluff).
  - `4–14s`: Establish mystery.
  - `14–29s`: First revelation.
  - `29–50s`: Escalation & depth.
  - `50–66s`: Climactic reveal.
  - `66–80s`: Payoff & unforgettable takeaway.
- **Output**: `StoryScript` with exact word counts and scene markers.

### 2.3 Video Production Engine (`MediaProductionEngine`)
- **Visuals Sub-agent**: Slices timeline into 2.5–4.0s scenes, fetches/renders imagery, applies Ken Burns effects.
- **Audio Sub-agent**: Synthesizes speech, measures word timestamps, mixes ambient score at -22 dB beneath voice at -14 LUFS.
- **Subtitle Sub-agent**: Renders responsive, high-contrast, center-bottom vertical subtitles.
- **FFmpeg Sub-agent**: Blends video stream, audio stream, and subtitles into standard `1080x1920` H.264/AAC MP4.

### 2.4 Editorial Quality Agent (`QualityAgent`)
- **Role**: Automated quality gatekeeper.
- **Checks**:
  1. Duration ($80\text{s} \pm 2\text{s}$).
  2. Resolution ($1080 \times 1920$, aspect ratio 9:16).
  3. Video/Audio codecs (`h264`, `aac`).
  4. Audio loudness (-14 LUFS $\pm 2$ LUFS).
  5. File playable and moov atom positioned at file start.
  6. Subtitle placement safely away from platform UI boundaries.
  7. Zero hallucinations against verified facts.

### 2.5 Publishing & Distribution Engine (`PublishingEngine`)
- **Role**: Takes the single master MP4 and dispatches it cleanly to each selected connected account.
- **Guarantees**:
  - Exact binary reuse (no platform-specific watermarking or transcoding).
  - Independent job tracking per account.
  - Idempotent uploads (prevents double posting).

### 2.6 Production Orchestrator (`ProductionOrchestrator`)
- **Role**: Coordinates the entire lifecycle, managing job queues, state transitions, retry budgets, and director approvals.
