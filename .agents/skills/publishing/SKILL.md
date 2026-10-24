---
name: publishing
description: Multi-platform connectors, multi-account token management, publishing queues, and distribution logic.
---

# Publishing & Platform Integration Skill

## Purpose
Guides the Publishing role in distributing the master MP4 across YouTube Shorts, Instagram Reels, Facebook Reels, and future destinations.

## Core Rules
1. **Master Binary Reuse**: Never re-encode, rebrand, or alter the MP4 binary per platform. Dispatch the exact same file.
2. **Account Independence**: Each connected account gets its own tracking record. An Instagram failure must never trigger re-upload to YouTube.
3. **Security**: Encrypt OAuth refresh tokens at rest. Never print tokens in logs or expose them via API responses.
4. **Resilience**: Chunked resumable uploads with exponential backoff and idempotency keys to eliminate double-posting.
