# VideoAutomater

> **Autonomous AI-Powered Video Creation & Multi-Platform Publishing System**

VideoAutomater is a production-grade, centralized, autonomous content engine that researches fascinating subjects, generates compelling 80-second vertical storytelling videos (9:16 H.264/AAC MP4), and publishes the exact same master video across multiple social destinations (YouTube Shorts, Instagram Reels, Facebook Page Reels).

---

## 🌟 Core Pillars

1. **One Master Video, Multi-Destination Publishing**: Generate once (`1080x1920`, 80s, 30fps), publish identically without re-rendering or re-branding.
2. **Free-First Engineering**: Free-tier Gemini models, open-source TTS / Edge TTS, Pillow/FFmpeg programmatic animations, and rights-verified visual assets.
3. **Multi-Agent Architecture**: Dedicated runtime agents for Research, Scriptwriting, Media Production, Editorial Quality, and Publishing Distribution.
4. **Director's Console**: Natural-language agent steering, persistent instruction hierarchy, on-demand creation, review policies (`AUTO_PUBLISH`, `OPTIONAL_REVIEW`, `REQUIRED_APPROVAL`), and independent posting schedules.
5. **Production Quality & Verifiability**: Strict fact-checking eligibility gates, sub-second caption synchronization, and automated visual and audio quality checks.

---

## 🏗️ Repository Layout

```text
VideoAutomater/
├── AGENTS.md                       # Development agent definitions & working agreements
├── .agents/                        # Specialized Antigravity skills
│   └── skills/
│       ├── architecture/
│       ├── content-engineering/
│       ├── media-engineering/
│       ├── publishing/
│       └── qa-devops/
├── docs/                           # Master architecture & design documentation
│   ├── ARCHITECTURE.md
│   ├── IMPLEMENTATION_PLAN.md
│   ├── AGENT_DESIGN.md
│   ├── GIT_WORKFLOW.md
│   └── DATA_CONTRACTS.md
├── src/
│   └── videoautomater/             # Production package
│       ├── agents/                 # Agent interfaces & coordinator
│       ├── research/               # Topic discovery, ranking & verification
│       ├── content/                # Scriptwriting & hook optimization
│       ├── visuals/                # Asset discovery & programmatic graphics
│       ├── audio/                  # Narration & audio mixing
│       ├── rendering/              # FFmpeg master video assembly
│       ├── quality/                # Content & technical validation
│       ├── publishing/             # Platform connectors & distribution
│       ├── accounts/               # Account registry & token management
│       ├── scheduling/             # Production & publishing schedulers
│       ├── orchestration/          # State machine & durable workflows
│       ├── analytics/              # Performance metrics & ingestion
│       └── storage/                # Library & asset storage
├── dashboard/                      # Director's Console UI
├── tests/                          # Unit, integration & pipeline tests
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── pyproject.toml
├── Dockerfile
├── .env.example
├── .gitignore
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+ (Recommended Python 3.11+)
- FFmpeg (via system package or `imageio-ffmpeg`)

```bash
# Clone and setup
git clone https://github.com/RaheelCr7/VideoAutomater.git
cd VideoAutomater

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

---

## 📜 Development & Contribution Workflow

This project adheres to a strict GitHub feature-branch model:
- `main` is protected and represents production-ready code.
- Feature branches (`feat/*`, `fix/*`, `chore/*`, `docs/*`, `test/*`, `infra/*`) require automated test verification and explicit review prior to merging.
- See [docs/GIT_WORKFLOW.md](docs/GIT_WORKFLOW.md) and [AGENTS.md](AGENTS.md) for full engineering guidelines.
