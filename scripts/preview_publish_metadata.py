#!/usr/bin/env python3
"""
Beyond 80 - Publish Metadata Dry Run

Prints the title, description, tags and pinned comment that the publishing engine would
send for a topic, WITHOUT uploading anything.

  .venv/bin/python scripts/preview_publish_metadata.py --all
  .venv/bin/python scripts/preview_publish_metadata.py --candidate cand_space_001 --candidate cand_science_002
  .venv/bin/python scripts/preview_publish_metadata.py --job job_1761500000000      # a real job from the platform DB
  .venv/bin/python scripts/preview_publish_metadata.py --topic "Why tardigrades survive space"
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from videoautomater.platform.models import ProductionJob, PublishingPlatform  # noqa: E402
from videoautomater.platform.publish_metadata import (  # noqa: E402
    TITLE_HOOK_CHARS,
    TITLE_MAX_CHARS,
    build_publish_metadata,
)
from videoautomater.research.curated_catalog import (  # noqa: E402
    get_brief_for_candidate,
    get_candidate_topics,
)


def show(label: str, meta) -> None:
    print("=" * 78)
    print(f"{label}")
    print("-" * 78)
    print(f"TITLE ({len(meta.title)}/{TITLE_MAX_CHARS} chars; feed shows ~{TITLE_HOOK_CHARS}):")
    print(f"  {meta.title}")
    print(f"  {meta.title[:TITLE_HOOK_CHARS]}{'…' if len(meta.title) > TITLE_HOOK_CHARS else ''}   <- what the Shorts feed shows")
    print("DESCRIPTION:")
    for line in meta.description.split("\n"):
        print(f"  {line}")
    print(f"TAGS ({len(meta.tags)}):")
    print(f"  {', '.join(meta.tags)}")
    print(f"CATEGORY: {meta.category or '(none)'}")
    print("PINNED COMMENT:")
    print(f"  {meta.pinned_comment}")
    print()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--candidate", action="append", default=[], help="catalog candidate id (repeatable)")
    parser.add_argument("--all", action="store_true", help="every candidate in the curated catalog")
    parser.add_argument("--job", action="append", default=[], help="job id from the platform DB (repeatable)")
    parser.add_argument("--topic", action="append", default=[], help="free-text topic with no brief (fallback path)")
    parser.add_argument("--platform", default="youtube_shorts", choices=[p.value for p in PublishingPlatform])
    args = parser.parse_args()

    platform = PublishingPlatform(args.platform)
    shown = 0

    candidate_ids = list(args.candidate)
    if args.all:
        candidate_ids.extend(c.id for c in get_candidate_topics())
    for cid in dict.fromkeys(candidate_ids):
        brief = get_brief_for_candidate(cid)
        if brief is None:
            print(f"!! unknown candidate id: {cid}")
            continue
        job = ProductionJob(id=f"preview_{cid}", topic=brief.topic)
        show(f"CATALOG {cid}: {brief.topic}", build_publish_metadata(job, platform=platform, brief=brief))
        shown += 1

    if args.job:
        from videoautomater.platform.storage import PlatformStorage

        storage = PlatformStorage()
        for job_id in args.job:
            job = storage.get_job(job_id)
            if job is None:
                print(f"!! job not found: {job_id}")
                continue
            show(f"JOB {job.id}: {job.topic}", build_publish_metadata(job, platform=platform))
            shown += 1

    for topic in args.topic:
        job = ProductionJob(id="preview_topic", topic=topic)
        show(f"TOPIC (no research brief): {topic}", build_publish_metadata(job, platform=platform))
        shown += 1

    if not shown:
        parser.print_help()
        return 1
    print("Dry run only. Nothing was uploaded.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
