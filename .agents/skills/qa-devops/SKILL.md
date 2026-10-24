---
name: qa-devops
description: Automated test suites, CI/CD pipelines, Docker containerization, Cloud Run execution, and observability.
---

# QA, DevOps & Automation Skill

## Purpose
Guides the QA and DevOps role in ensuring test coverage, reproducible container builds, secure cloud automation, and runtime observability.

## Core Rules
1. **Testing First**: Every component must have automated unit tests with mocks and deterministic fixtures.
2. **End-to-End Validation**: Pipeline tests must verify duration, codecs, audio LUFS, and output artifact trees.
3. **Reproducibility**: Docker container with multi-stage build, minimal Debian/Alpine base, bundled FFmpeg, and pinned dependencies.
4. **Cloud Guardrails**: Cloud Run Job definitions must include budget caps, execution timeouts (e.g. 10m), and structured JSON logging.
