"""Persistent history and duplicate topic detection registry."""

import json
import re
from pathlib import Path


class TopicRegistry:
    """Tracks historical topics to prevent duplication across production runs."""

    def __init__(self, storage_path: Path | None = None):
        self.storage_path = storage_path or Path("output/topic_history.json")
        self._history: list[dict] = []
        self._normalized_titles: set[str] = set()
        self._load()

    def _normalize(self, text: str) -> str:
        """Strip punctuation, lowercase, and tokenize text."""
        cleaned = re.sub(r"[^\w\s]", "", text.lower())
        tokens = [w for w in cleaned.split() if len(w) > 2]
        return " ".join(tokens)

    def _load(self) -> None:
        if self.storage_path.exists():
            try:
                data = json.loads(self.storage_path.read_text(encoding="utf-8"))
                self._history = data.get("topics", [])
                for item in self._history:
                    self._normalized_titles.add(self._normalize(item.get("title", "")))
            except (json.JSONDecodeError, OSError):
                self._history = []
                self._normalized_titles = set()

    def _save(self) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        data = {"topics": self._history}
        self.storage_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def is_duplicate(self, title: str, threshold: float = 0.55) -> bool:
        """Check if a topic title is semantically too close to any previously produced topic."""
        norm_title = self._normalize(title)
        if not norm_title:
            return False

        if norm_title in self._normalized_titles:
            return True

        title_words = set(norm_title.split())
        for existing in self._normalized_titles:
            existing_words = set(existing.split())
            if not existing_words:
                continue
            intersection = title_words.intersection(existing_words)
            union = title_words.union(existing_words)
            jaccard = len(intersection) / len(union) if union else 0.0
            # Also check containment overlap
            overlap = len(intersection) / min(len(title_words), len(existing_words)) if intersection else 0.0
            if jaccard >= threshold or overlap >= 0.70:
                return True

        return False

    def record_topic(self, topic_id: str, title: str, category: str) -> None:
        """Persist a produced topic into the historical registry."""
        norm_title = self._normalize(title)
        self._normalized_titles.add(norm_title)
        self._history.append({
            "id": topic_id,
            "title": title,
            "normalized": norm_title,
            "category": category,
        })
        self._save()
