# Beyond 80 — Cloud Deployment & Production Readiness Guide

This document describes the production deployment architecture for the **Beyond 80 Agent Control Center** and autonomous video production pipeline.

---

## 1. Architecture Overview

```
                      +-----------------------------+
                      |   Cloudflare / CDN / WAF    |
                      +--------------+--------------+
                                     |
                                     v
                      +-----------------------------+
                      |       NGINX Ingress         |
                      |     (SSL Termination)       |
                      +--------------+--------------+
                                     |
                 +-------------------+-------------------+
                 |                                       |
                 v                                       v
   +---------------------------+           +---------------------------+
   |   FastAPI Control Center  |           | Background Render Worker  |
   |     (UI & REST APIs)      |           |     (13-Agent Fleet)      |
   +-------------+-------------+           +-------------+-------------+
                 |                                       |
                 +-------------------+-------------------+
                                     |
         +---------------------------+---------------------------+
         |                           |                           |
         v                           v                           v
+-----------------+         +-----------------+         +-----------------+
|  PostgreSQL /   |         |  Redis / Celery |         |   S3 / Cloud    |
| Durable Storage |         |   (Task Queue)  |         | Storage (Videos)|
+-----------------+         +-----------------+         +-----------------+
```

---

## 2. Local vs. Cloud Deployment

### Local Mode (Zero Cost, Fully Operational)
- **Web Server:** `uvicorn videoautomater.server.app:app`
- **Background Orchestrator:** In-process threading with durable JSON storage (`output/platform_db/`)
- **Render Engine:** Local FFmpeg (`imageio-ffmpeg`)
- **Publishing:** Simulated Connectors (`SIMULATED_CONNECTOR`)

### Cloud Production Mode
- **Containerization:** Docker & Docker Compose (`docker-compose.yml`)
- **Task Queue:** Celery with Redis for distributed multi-GPU rendering nodes.
- **Storage:** S3-compatible object storage (AWS S3, Cloudflare R2, MinIO) for immutable video masters.
- **Database:** PostgreSQL for job persistence, review records, and audit logs.
- **Publishing:** Production OAuth credentials with restricted scope.

---

## 3. Quick Start Deployment

### Method A: Local Native
```bash
./scripts/setup_platform.sh
./scripts/run_platform.sh
# Open http://localhost:8000
```

### Method B: Docker Compose
```bash
docker-compose up --build -d
# Check logs:
docker-compose logs -f
```

---

## 4. Environment Variables Reference

| Variable | Description | Default |
| :--- | :--- | :--- |
| `APP_ENV` | Environment mode (`development` / `production`) | `production` |
| `PORT` | Listening HTTP port | `8000` |
| `DEFAULT_TIMEZONE` | Autonomous scheduler timezone | `Asia/Karachi` |
| `DEFAULT_APPROVAL_MODE` | Default governance gate (`REQUIRED_APPROVAL`) | `REQUIRED_APPROVAL` |
| `DATA_DIR` | Directory for persistent platform data | `output/platform_db` |
| `OUTPUT_DIR` | Base directory for rendered video masters | `output` |

---

## 5. Security & Governance Rules

1. **Unpublished Default:** Every generated video is created in `PENDING_HUMAN_APPROVAL` status.
2. **Release Authorization Gate:** Publishing connectors will refuse to dispatch if `publication_authorized` is `False`, even if automated QA passes.
3. **Traceability:** Every master video retains immutable DOI research citations, word-level audio timestamps, and reviewer feedback logs.
