"""
Integration tests for FastAPI Agent Control Center endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from videoautomater.server.app import app
from videoautomater.platform.models import ReviewStatus, JobStatus


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_api_health_endpoint(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "orchestrator_running" in data


def test_api_dashboard_endpoint(client):
    res = client.get("/api/dashboard")
    assert res.status_code == 200
    data = res.json()
    assert "total_jobs" in data
    assert "completed_videos" in data


def test_api_director_chat_endpoint(client):
    res = client.post("/api/director/chat", json={
        "message": "Create an 80-second cinematic video explaining how black holes bend light. Use scientifically accurate 3D animations and save for my review."
    })
    assert res.status_code == 200
    data = res.json()
    assert "content" in data
    assert "black hole" in data["content"].lower()


def test_api_jobs_crud(client):
    # Create job
    create_res = client.post("/api/jobs", json={
        "topic": "General Relativity and Light Bending",
        "target_duration_sec": 80.0,
        "approval_mode": "REQUIRED_APPROVAL",
        "director_instructions": "Accurate photon sphere"
    })
    assert create_res.status_code == 200
    job = create_res.json()
    job_id = job["id"]

    # Get job
    get_res = client.get(f"/api/jobs/{job_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == job_id


def test_api_agents_endpoint(client):
    res = client.get("/api/agents")
    assert res.status_code == 200
    agents = res.json()
    assert len(agents) == 13


def test_api_review_authorization_protection(client):
    # Try to authorize release on a video that is still PENDING_HUMAN_APPROVAL
    create_res = client.post("/api/jobs", json={
        "topic": "Test Video for Release",
        "target_duration_sec": 80.0
    })
    job_id = create_res.json()["id"]

    # Attempt release authorization
    auth_res = client.post(f"/api/review/{job_id}/authorize-publication", json={"authorized": True})
    assert auth_res.status_code == 400
    assert "APPROVED_FOR_RELEASE" in auth_res.json()["detail"]
