"""
Tests for hook-first publish metadata and live-upload pacing.

Covers the builder (titles, descriptions, tags, pinned comment), the connector-level
sanitizers that keep legacy metadata out, and the posting-cadence guard.
"""

import os
import shutil
import tempfile
import zoneinfo
from datetime import datetime, timedelta, timezone

import pytest

from videoautomater.models.research import FactualEvidence, ResearchBrief
from videoautomater.platform import publishing_engine as pe
from videoautomater.platform.models import (
    JobStatus,
    ProductionJob,
    PublishingPlatform,
    PublishingTask,
    ReviewStatus,
)
from videoautomater.platform.publish_metadata import (
    BRAND_TAG,
    TAGS_MAX,
    TITLE_MAX_CHARS,
    build_publish_metadata,
    build_tags,
    clean_title,
    fit_title,
    hashtags_from_tags,
    sanitize_description,
    sanitize_title,
)
from videoautomater.platform.publishing_engine import (
    PublishingEngine,
    SimulatedPlatformConnector,
    YouTubeLiveConnector,
)
from videoautomater.platform.storage import PlatformStorage
from videoautomater.research.curated_catalog import get_brief_for_candidate, get_candidate_topics

LEGACY_TITLE = "Beyond 80: The Secret Inside the Ice Giants (Diamond Rain Engine) #Shorts"
LEGACY_DESCRIPTION = (
    "Beyond 80: The Secret Inside the Ice Giants (Diamond Rain Engine)\n\n"
    "Produced autonomously by Beyond 80.\n#science #astrophysics #beyond80"
)
EXPECTED_HEADLINES = {
    "cand_space_001": "It Rains Diamonds on Neptune. Here's How.",
    "cand_science_002": "Earth Ran a Nuclear Reactor 2 Billion Years Ago",
    "cand_history_003": "The 2,000-Year-Old Computer Found in a Shipwreck",
}


def _hashtags(text: str):
    return [w for w in text.split() if w.startswith("#")]


# --------------------------------------------------------------------------- titles

def test_clean_title_strips_prefix_parenthetical_and_shorts_tag():
    assert clean_title(LEGACY_TITLE) == "The Secret Inside the Ice Giants"
    assert clean_title("beyond 80 — neutron stars") == "Neutron stars"
    assert clean_title("Beyond 80 Relativistic Episode") == "Beyond 80 Relativistic Episode"  # no separator: not a prefix


def test_fit_title_cuts_on_word_boundary_within_limit():
    long_title = "Black holes bend light so hard that you can see the far side of the disc behind them"
    fitted = fit_title(long_title)
    assert len(fitted) <= TITLE_MAX_CHARS
    assert not fitted.endswith(" ")
    assert long_title.startswith(fitted)
    assert fitted.split()[-1] in long_title.split()


# --------------------------------------------------------------------------- catalog briefs

@pytest.mark.parametrize("candidate", get_candidate_topics(), ids=lambda c: c.id)
def test_catalog_briefs_get_hook_first_metadata(candidate):
    brief = get_brief_for_candidate(candidate.id)
    job = ProductionJob(id="job_preview", topic=candidate.title)
    meta = build_publish_metadata(job, brief=brief)

    if candidate.id in EXPECTED_HEADLINES:
        assert meta.title == EXPECTED_HEADLINES[candidate.id]
    assert len(meta.title) <= TITLE_MAX_CHARS
    assert "Beyond 80" not in meta.title
    assert "#" not in meta.title and "(" not in meta.title

    assert "Produced autonomously" not in meta.description
    assert "#Shorts" not in meta.description
    assert "?" in meta.description
    assert "Sources:" in meta.description
    hashtags = _hashtags(meta.description)
    assert 3 <= len(hashtags) <= 5
    assert hashtags[-1] == f"#{BRAND_TAG}"

    assert BRAND_TAG in meta.tags
    assert len(meta.tags) <= TAGS_MAX
    assert all(len(t) <= 30 for t in meta.tags)
    assert meta.pinned_comment.endswith("80 seconds.")


def test_tags_are_topic_specific_not_one_fixed_list():
    neptune = build_publish_metadata(
        ProductionJob(id="j1", topic="x"), brief=get_brief_for_candidate("cand_space_001")
    )
    oklo = build_publish_metadata(
        ProductionJob(id="j2", topic="x"), brief=get_brief_for_candidate("cand_science_002")
    )
    antikythera = build_publish_metadata(
        ProductionJob(id="j3", topic="x"), brief=get_brief_for_candidate("cand_history_003")
    )

    assert "neptune" in neptune.tags and "diamond rain" in neptune.tags and "space" in neptune.tags
    assert neptune.category == "space"

    assert "nuclear" in oklo.tags and "geology" in oklo.tags and "oklo" in oklo.tags
    assert "astrophysics" not in oklo.tags
    assert oklo.category == "nuclear"
    assert "buried under our feet" in oklo.description

    assert "antikythera mechanism" in antikythera.tags and "history" in antikythera.tags
    assert antikythera.category == "history"

    assert neptune.tags != oklo.tags != antikythera.tags


def test_autonomous_brief_without_headline_falls_back_to_cleaned_title():
    brief = ResearchBrief(
        brief_id="brief_auto_000001",
        topic="Tardigrades",
        proposed_title="Beyond 80: The Secret of Tardigrades",
        alternative_hooks=["hook one", "hook two", "hook three"],
        central_question="q",
        verified_facts=["Tardigrades survive the vacuum of space for days."],
        supporting_evidence=[FactualEvidence(claim="c", source_name="s", url="https://example.org/paper")],
        suggested_narrative_angle="x",
    )
    meta = build_publish_metadata(ProductionJob(id="j", topic="Tardigrades"), brief=brief)
    assert meta.title == "The Secret of Tardigrades"
    assert meta.category == "biology"
    assert "biology" in meta.tags
    assert meta.description.startswith("Tardigrades survive the vacuum of space for days.")
    assert "https://example.org/paper" in meta.description


def test_job_without_brief_still_gets_clean_metadata():
    job = ProductionJob(id="j", topic=LEGACY_TITLE, output_dir="/nonexistent/dir")
    meta = build_publish_metadata(job)
    assert meta.title == "The Secret Inside the Ice Giants"
    assert "diamond rain" in meta.tags
    assert BRAND_TAG in meta.tags
    assert "Produced autonomously" not in meta.description
    assert _hashtags(meta.description)[-1] == f"#{BRAND_TAG}"


def test_non_youtube_platforms_lead_caption_with_title():
    brief = get_brief_for_candidate("cand_space_001")
    meta = build_publish_metadata(
        ProductionJob(id="j", topic=brief.topic), platform=PublishingPlatform.INSTAGRAM_REELS, brief=brief
    )
    assert meta.description.startswith(meta.title)


def test_title_override_wins():
    brief = get_brief_for_candidate("cand_space_001")
    meta = build_publish_metadata(
        ProductionJob(id="j", topic=brief.topic), brief=brief, title_override="Beyond 80: Director's cut #Shorts"
    )
    assert meta.title == "Director's cut"


def test_hashtags_and_tags_helpers():
    tags = build_tags("Neptune's Diamond Rain Engine", "space")
    assert tags[-1] == BRAND_TAG
    assert len(tags) == len(set(tags))
    hashtags = hashtags_from_tags(tags, "space")
    assert hashtags[-1] == f"#{BRAND_TAG}"
    assert 3 <= len(hashtags) <= 5
    assert all(h.startswith("#") and " " not in h for h in hashtags)


# --------------------------------------------------------------------------- connector sanitizing

def test_sanitizers_remove_legacy_metadata():
    assert sanitize_title(LEGACY_TITLE) == "The Secret Inside the Ice Giants (Diamond Rain Engine)"
    cleaned = sanitize_description(LEGACY_DESCRIPTION)
    assert "Produced autonomously" not in cleaned
    assert "#science #astrophysics #beyond80" in cleaned


def test_simulated_youtube_connector_no_longer_appends_shorts_tag():
    connector = SimulatedPlatformConnector(PublishingPlatform.YOUTUBE_SHORTS)
    meta = connector.validate_metadata("Black Holes Bend Light", "Plain description.", [])
    assert meta["title"] == "Black Holes Bend Light"
    assert "#Shorts" not in meta["description"]
    assert BRAND_TAG in meta["tags"]


def test_live_youtube_connector_validate_strips_legacy_and_derives_tags():
    meta = YouTubeLiveConnector().validate_metadata(LEGACY_TITLE, LEGACY_DESCRIPTION, [])
    assert meta["title"] == "The Secret Inside the Ice Giants (Diamond Rain Engine)"
    assert "#Shorts" not in meta["title"]
    assert "Produced autonomously" not in meta["description"]
    assert meta["tags"] != ["shorts", "science", "physics", "beyond80"]
    assert "diamond rain" in meta["tags"] and BRAND_TAG in meta["tags"]


def test_live_youtube_connector_rejects_empty_title():
    with pytest.raises(pe.PublishingError):
        YouTubeLiveConnector().validate_metadata("#Shorts", "", [])


# --------------------------------------------------------------------------- posting cadence

@pytest.fixture
def engine_env():
    temp_dir = tempfile.mkdtemp()
    storage = PlatformStorage(base_dir=temp_dir)
    engine = PublishingEngine(storage=storage)
    settings = storage.get_settings()
    settings.default_timezone = "Asia/Karachi"
    settings.publish_min_gap_hours = 20
    settings.publish_hour_local = 20
    storage.save_settings(settings)
    video_path = os.path.join(temp_dir, "master.mp4")
    with open(video_path, "wb") as f:
        f.write(b"0" * 4096)
    yield storage, engine, video_path
    shutil.rmtree(temp_dir, ignore_errors=True)


def _completed_task(account_id: str, published_at: datetime, suffix: str) -> PublishingTask:
    return PublishingTask(
        id=f"pub_task_done_{suffix}",
        job_id="job_done",
        account_id=account_id,
        platform=PublishingPlatform.YOUTUBE_SHORTS,
        status=JobStatus.COMPLETED,
        published_at=published_at,
    )


def test_next_publish_slot_waits_for_gap_and_aligns_to_posting_hour(engine_env):
    storage, engine, _ = engine_env
    tz = zoneinfo.ZoneInfo("Asia/Karachi")
    now = datetime(2026, 10, 28, 12, 0, tzinfo=tz)
    account = engine.register_account(
        PublishingPlatform.YOUTUBE_SHORTS, "Beyond 80 live", credentials={"token": "t"}, is_simulated=False
    )

    assert engine.next_publish_slot(account.id, now=now) is None  # nothing published yet

    storage.save_publishing_task(_completed_task(account.id, now - timedelta(hours=2), "recent"))
    # last publish 10:00 on the 28th -> earliest 06:00 on the 29th -> aligned to 20:00 on the 29th
    assert engine.next_publish_slot(account.id, now=now) == datetime(2026, 10, 29, 20, 0, tzinfo=tz)

    storage.save_publishing_task(_completed_task(account.id, now - timedelta(hours=30), "older"))
    assert engine.next_publish_slot(account.id, now=now) == datetime(2026, 10, 29, 20, 0, tzinfo=tz)  # newest wins


def test_next_publish_slot_is_none_once_gap_has_passed(engine_env):
    storage, engine, _ = engine_env
    tz = zoneinfo.ZoneInfo("Asia/Karachi")
    now = datetime(2026, 10, 28, 12, 0, tzinfo=tz)
    account = engine.register_account(
        PublishingPlatform.YOUTUBE_SHORTS, "Beyond 80 live", credentials={"token": "t"}, is_simulated=False
    )
    storage.save_publishing_task(_completed_task(account.id, now - timedelta(hours=25), "old"))
    assert engine.next_publish_slot(account.id, now=now) is None

    naive = (now - timedelta(hours=1)).replace(tzinfo=None)  # legacy tasks stored naive local times
    storage.save_publishing_task(_completed_task(account.id, naive, "naive"))
    assert engine.next_publish_slot(account.id, now=now) is not None


def test_execute_schedules_live_upload_when_too_soon_and_passes_comment(engine_env, monkeypatch):
    storage, engine, video_path = engine_env
    tz = zoneinfo.ZoneInfo("Asia/Karachi")
    account = engine.register_account(
        PublishingPlatform.YOUTUBE_SHORTS, "Beyond 80 live", credentials={"token": "t"}, is_simulated=False
    )
    job = ProductionJob(
        id="job_live",
        topic="Neptune's Diamond Rain Engine",
        master_video_path=video_path,
        status=JobStatus.COMPLETED,
        review_status=ReviewStatus.APPROVED_FOR_RELEASE,
        publication_authorized=True,
    )
    storage.save_job(job)
    storage.save_publishing_task(_completed_task(account.id, datetime.now(tz) - timedelta(hours=1), "recent"))

    captured = {}

    def fake_publish(self, account, master_video_path, title, description, tags, idempotency_key,
                     publish_at=None, pinned_comment=None):
        captured.update(publish_at=publish_at, pinned_comment=pinned_comment, title=title)
        return {"remote_id": "vid123", "share_url": "https://www.youtube.com/shorts/vid123",
                "comment": {"posted": False, "text": pinned_comment}}

    monkeypatch.setattr(pe.YouTubeLiveConnector, "publish_video", fake_publish)

    task = engine.create_publishing_task(
        job.id, account.id, LEGACY_TITLE, LEGACY_DESCRIPTION, [], metadata={"pinned_comment": "Which planet next?"}
    )
    done = engine.execute_publishing_task(task.id)

    assert done.status == JobStatus.COMPLETED
    assert captured["publish_at"] is not None
    assert captured["publish_at"].astimezone(tz).hour == 20
    assert captured["pinned_comment"] == "Which planet next?"
    assert done.metadata["scheduled_publish_at"] == captured["publish_at"].isoformat()
    assert done.metadata["comment"]["text"] == "Which planet next?"
    assert done.published_at == captured["publish_at"]

    # The scheduled go-live time now counts as the last publish, so the next one chains after it.
    following = engine.next_publish_slot(account.id)
    assert following is not None and following > captured["publish_at"]

    # force_now bypasses the pacing for a deliberate exception.
    task2 = engine.create_publishing_task(job.id, account.id, "Second title", "desc", ["x"])
    done2 = engine.execute_publishing_task(task2.id, force_now=True)
    assert done2.status == JobStatus.COMPLETED
    assert captured["publish_at"] is None
    assert done2.published_at.tzinfo is not None


def test_simulated_accounts_are_not_paced(engine_env):
    storage, engine, video_path = engine_env
    account = engine.register_account(PublishingPlatform.YOUTUBE_SHORTS, "Beyond 80 sim", is_simulated=True)
    job = ProductionJob(
        id="job_sim",
        topic="Neptune's Diamond Rain Engine",
        master_video_path=video_path,
        status=JobStatus.COMPLETED,
        review_status=ReviewStatus.APPROVED_FOR_RELEASE,
        publication_authorized=True,
    )
    storage.save_job(job)
    storage.save_publishing_task(_completed_task(account.id, datetime.now(timezone.utc) - timedelta(hours=1), "recent"))

    task = engine.create_publishing_task(job.id, account.id, "Sim title", "desc", [])
    done = engine.execute_publishing_task(task.id)
    assert done.status == JobStatus.COMPLETED
    assert "scheduled_publish_at" not in done.metadata
