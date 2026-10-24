# AGENTS.md — VideoAutomater Development Agent Guidelines

This file governs the collaboration and engineering standards for all specialized development roles working on VideoAutomater.

---

## 1. Core Engineering Principles

1. **Production-First Mentality**: Build actual, verifiable, working software. Never stop at theoretical plans or placeholder stubs.
2. **Master Video Rule**: All rendering code must produce a single broadcast-ready vertical master MP4 (1080x1920, 80 seconds, 30fps, H.264/AAC). This master file is published identically to all destination accounts.
3. **Free-First Technology**: Prioritize free-tier models (Gemini API free tier), open-source TTS / Edge-TTS, programmatic SVG/Pillow graphics, and public-domain/CC0 media. Never activate billable cloud features or paid APIs without explicit Director authorization.
4. **Deterministic Architecture**: Use LLMs where cognitive creativity is needed (research ranking, narrative drafting, hook evaluation); use deterministic Python code where reliability is paramount (FFmpeg assembly, audio alignment, rate limiting, OAuth state machines).
5. **Strict Git Discipline**:
   - Never commit directly to `main`.
   - Work in dedicated feature branches (`feat/*`, `fix/*`, `chore/*`, `infra/*`, `test/*`, `docs/*`).
   - Every feature must include automated pytest coverage.
   - Pushes must be accompanied by clean Pull Requests with verifiable acceptance criteria.
   - Never merge to `main` without explicit Content Director approval.
6. **No Secret Commits**: Never commit credentials, OAuth tokens, API keys, or media binary dumps. Maintain strict `.gitignore` rules.

---

## 2. Specialized Development Roles & Skills

| Role | Skill Path | Primary Focus |
|---|---|---|
| **Lead Architect** | `.agents/skills/architecture/` | Overall system architecture, data contracts, interface stability, code integration review. |
| **Content Engineering Agent** | `.agents/skills/content-engineering/` | Research engine, topic discovery, factual claim verification, scriptwriting engine, hook optimization. |
| **Media Engineering Agent** | `.agents/skills/media-engineering/` | Asset acquisition, programmatic rendering, narration synthesis, subtitle synchronization, FFmpeg assembly. |
| **Publishing Agent** | `.agents/skills/publishing/` | Platform connectors (YouTube, Instagram, Facebook), multi-account registry, upload queues, retries. |
| **QA & DevOps Agent** | `.agents/skills/qa-devops/` | Automated test suites, GitHub Actions CI, Docker containerization, Cloud Run, monitoring. |

---

## 3. Working Agreements & Hand-Offs

- **Interface Stability**: Any modification to data models in `docs/DATA_CONTRACTS.md` requires cross-role review before implementation.
- **Parallel Work**: Use isolated Git worktrees (`git worktree add`) when developing parallel features to prevent filesystem collisions.
- **Test Integrity**: Test suites must distinguish mocked unit tests from integration tests requiring external API connectivity.
- **Reporting**: Every completed pull request must report branch name, commit SHA, PR status, test results, and next steps.
