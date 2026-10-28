"""
Beyond 80 - Publish Metadata Builder

Turns a production job and its research brief into hook-first publishing metadata
without an LLM:

* title           <= 60 characters with the surprising claim first; no "Beyond 80:" prefix,
                   no "#Shorts" suffix, no parenthetical jargon
* description     two sentences with the surprising fact, one question that invites
                   comments, the sources, then 3-5 topic hashtags
* tags            derived from the topic and its category (always includes "beyond80")
* pinned_comment  the same question, ready to post under the video

The connectors also run the sanitizers in this module, so legacy metadata
("Beyond 80: ... #Shorts", "Produced autonomously by Beyond 80.") cannot reach a platform
through any path.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence

from videoautomater.models.research import ResearchBrief
from videoautomater.platform.models import ProductionJob, PublishingPlatform

logger = logging.getLogger(__name__)

TITLE_MAX_CHARS = 60        # whole title
TITLE_HOOK_CHARS = 40       # what the Shorts feed shows before it truncates
PLATFORM_TITLE_MAX = 100    # YouTube hard limit, enforced by the connectors
TAGS_MAX = 15
HASHTAGS_MAX = 5
HASHTAGS_MIN = 3
SOURCES_MAX = 2
SENTENCE_MAX_CHARS = 220
BRAND_TAG = "beyond80"
DEFAULT_QUESTION = "What should we uncover next?"
PINNED_COMMENT_SUFFIX = "Drop it below and we'll make it in 80 seconds."

_BRAND_PREFIX = re.compile(r"^\s*beyond\s*80\s*(?:[:\-–—|]\s*)+", re.IGNORECASE)
_PARENTHETICAL = re.compile(r"\s*\([^)]*\)")
_HASHTAG = re.compile(r"(?<!\w)#\w+")
_AUTONOMOUS_LINE = re.compile(r"^[ \t]*produced autonomously[^\n]*\n?", re.IGNORECASE | re.MULTILINE)
_MULTI_SPACE = re.compile(r"[ \t]+")
_MULTI_NEWLINE = re.compile(r"\n{3,}")
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
_NON_TAG_CHARS = re.compile(r"[^a-z0-9 ]")
_CATALOG_BRIEF_ID = re.compile(r"^brief_cand_([a-z]+)_\d+$")

_STOPWORDS = {
    "the", "and", "for", "that", "this", "with", "from", "into", "what", "when", "where", "which",
    "who", "why", "how", "its", "our", "your", "their", "they", "them", "are", "was", "were", "has",
    "have", "had", "not", "but", "can", "could", "would", "should", "will", "just", "than", "then",
    "about", "over", "under", "after", "before", "between", "inside", "secret", "secrets", "hidden",
    "mystery", "world", "worlds", "first", "year", "years", "old", "billion", "million", "thousand",
    "ago", "ever", "most", "more", "less", "very", "really", "here", "there", "out", "off", "all",
    "any", "one", "two", "new", "made", "make", "makes", "like", "does", "did", "you", "his", "her",
    "she", "him", "way", "ways", "thing", "things", "still", "also", "even", "natural", "realm",
    "impossible", "beyond",
}

# Specific categories first; a generic catalog category ("science") is refined by these.
_CATEGORY_KEYWORDS: List[tuple[str, tuple[str, ...]]] = [
    ("nuclear", ("nuclear", "uranium", "fission", "reactor", "radioactiv")),
    ("space", ("planet", "neptune", "uranus", "jupiter", "saturn", "mars", "venus", "mercury", "star",
               "galax", "black hole", "cosmic", "nebula", "orbit", "solar", "lunar", "moon", "astronom",
               "voyager", "neutron", "pulsar", "supernova", "exoplanet", "universe", "comet", "asteroid")),
    ("history", ("ancient", "shipwreck", "roman", "greek", "egypt", "medieval", "century", "archaeolog",
                 "civilization", "antikythera", "dynasty", "empire")),
    ("biology", ("cell", "organism", "tardigrade", "dna", "species", "bacteria", "protein", "animal",
                 "plant", "brain", "microb", "extremophile", "fungi", "virus")),
    ("geology", ("volcano", "earthquake", "mineral", "crust", "tectonic", "geolog", "magma", "crystal",
                 "earth's")),
    ("physics", ("quantum", "relativity", "particle", "photon", "gravity", "electron", "entangle",
                 "superconduct", "thermodynam", "magnet")),
    ("engineering", ("machine", "gear", "steel", "bridge", "engine", "computer", "concrete", "invention")),
]
_GENERIC_CATEGORIES = {"", "science", "discoveries", "general"}

# Two-word terms that should stay together as a tag and a hashtag ("#blackholes", not "#black #holes").
_COMPOUNDS = {
    "black hole", "black holes", "neutron star", "neutron stars", "diamond rain", "nuclear reactor",
    "nuclear fission", "nuclear fusion", "solar system", "dark matter", "dark energy", "ice giant",
    "ice giants", "gas giant", "gas giants", "white dwarf", "red giant", "gamma ray", "gamma rays",
    "event horizon", "gravitational lensing", "gravitational waves", "quantum entanglement",
    "natural selection", "plate tectonics", "carbon dating", "big bang", "analog computer",
    "ancient greece", "ancient rome", "ancient egypt", "roman concrete", "damascus steel",
    "rogue planet", "rogue planets", "deep sea", "space telescope", "cosmic rays", "magnetic field",
    "supermassive black", "milky way", "north pole", "south pole", "ice age", "stone age",
}

CATEGORY_TAGS: Dict[str, List[str]] = {
    "space": ["space", "astronomy", "astrophysics"],
    "nuclear": ["nuclear", "geology", "earth science"],
    "geology": ["geology", "earth science"],
    "history": ["history", "archaeology", "ancient history"],
    "engineering": ["engineering", "technology"],
    "biology": ["biology", "nature"],
    "physics": ["physics", "science"],
    "science": ["science"],
    "discoveries": ["science", "discovery"],
}

CATEGORY_QUESTIONS: Dict[str, str] = {
    "space": "Which planet or star should we open up next?",
    "nuclear": "What other secret is buried under our feet?",
    "geology": "What other secret is buried under our feet?",
    "history": "Which ancient invention should we open up next?",
    "engineering": "Which machine should we take apart next?",
    "biology": "Which creature should we put under the microscope next?",
    "physics": "Which law of physics should we break down next?",
}


@dataclass
class PublishMetadata:
    """Everything a connector needs for one upload, plus the follow-up comment."""

    title: str
    description: str
    tags: List[str]
    pinned_comment: str
    category: str = ""
    hashtags: List[str] = field(default_factory=list)

    def task_metadata(self) -> Dict[str, Any]:
        """Extra fields stored on the PublishingTask (the connector posts the comment)."""
        return {
            "pinned_comment": self.pinned_comment,
            "category": self.category,
            "hashtags": list(self.hashtags),
            "metadata_builder": "publish_metadata.v1",
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "description": self.description,
            "tags": list(self.tags),
            "pinned_comment": self.pinned_comment,
            "category": self.category,
            "hashtags": list(self.hashtags),
        }


# --------------------------------------------------------------------------- titles

def clean_title(raw: str | None, drop_parentheticals: bool = True) -> str:
    """Strip the channel prefix, hashtags, (optionally) parentheticals and stray punctuation."""
    text = raw or ""
    text = _HASHTAG.sub("", text)
    text = _BRAND_PREFIX.sub("", text)
    if drop_parentheticals:
        text = _PARENTHETICAL.sub("", text)
    text = _MULTI_SPACE.sub(" ", text).strip(" \t\n-–—:|,;")
    if text and text[0].islower():
        text = text[0].upper() + text[1:]
    return text


def _truncate_words(text: str, limit: int, min_keep: int) -> str:
    """Cut at a sentence or word boundary at or before ``limit`` (never mid-word)."""
    if len(text) <= limit:
        return text
    window = text[: limit + 1]
    for sep in (". ", "? ", "! ", ": ", ", ", " "):
        idx = window.rfind(sep)
        if idx >= min_keep:
            end = idx + 1 if sep[0] in ".?!" else idx
            return text[:end].rstrip(" ,:;-–—")
    return window[:limit].rstrip()


def fit_title(title: str, limit: int = TITLE_MAX_CHARS) -> str:
    """Keep a title within ``limit`` characters, cutting on a word boundary."""
    return _truncate_words(title.strip(), limit, min_keep=int(TITLE_HOOK_CHARS * 0.75))


def choose_title(candidates: Iterable[str | None], limit: int = TITLE_MAX_CHARS) -> str:
    """First candidate that fits after cleaning; otherwise the first candidate, trimmed."""
    cleaned = [clean_title(c) for c in candidates if c and c.strip()]
    cleaned = [c for c in cleaned if c]
    for candidate in cleaned:
        if len(candidate) <= limit:
            return candidate
    return fit_title(cleaned[0], limit) if cleaned else ""


def sanitize_title(title: str | None) -> str:
    """Connector-level cleanup for titles that arrive from outside the builder."""
    return clean_title(title, drop_parentheticals=False)


def sanitize_description(description: str | None) -> str:
    """Remove the legacy 'Produced autonomously' line and '#Shorts' tokens."""
    text = description or ""
    text = _AUTONOMOUS_LINE.sub("", text)
    text = re.sub(r"[ \t]*#shorts\b", "", text, flags=re.IGNORECASE)
    text = _MULTI_NEWLINE.sub("\n\n", text)
    return "\n".join(line.rstrip() for line in text.split("\n")).strip()


# --------------------------------------------------------------------------- category

def infer_category(text: str) -> str:
    """Most-mentioned specific category in ``text``; '' when nothing matches."""
    lowered = (text or "").lower()
    best, best_hits = "", 0
    for category, keywords in _CATEGORY_KEYWORDS:
        hits = sum(lowered.count(k) for k in keywords)
        if hits > best_hits:
            best, best_hits = category, hits
    return best


def category_from_brief_id(brief_id: str) -> str:
    match = _CATALOG_BRIEF_ID.match(brief_id or "")
    return match.group(1) if match else ""


def resolve_category(explicit: str, text: str) -> str:
    explicit = (explicit or "").strip().lower()
    if explicit not in _GENERIC_CATEGORIES:
        return explicit
    return infer_category(text) or explicit


# --------------------------------------------------------------------------- tags

def _topic_words(topic_text: str) -> List[str]:
    core = clean_title(topic_text, drop_parentheticals=False).lower()
    core = core.replace("'s", "").replace("’s", "")
    core = _MULTI_SPACE.sub(" ", _NON_TAG_CHARS.sub(" ", core)).strip()
    return [w for w in core.split() if len(w) >= 3 and w not in _STOPWORDS and not w.isdigit()]


def build_tags(topic_text: str, category: str = "", extra: Sequence[str] = ()) -> List[str]:
    """Per-video tags: the topic phrase, its key bigrams and words, category tags, brand tag."""
    tags: List[str] = []

    def add(tag: str) -> None:
        tag = _MULTI_SPACE.sub(" ", tag.strip().lower())
        if 2 <= len(tag) <= 30 and tag not in tags and len(tags) < TAGS_MAX - 1:
            tags.append(tag)

    words = _topic_words(topic_text)
    phrase = " ".join(words)
    bigrams = [f"{a} {b}" for a, b in zip(words, words[1:])]
    for bigram in bigrams:                      # known compounds first: "black holes", "diamond rain"
        if bigram in _COMPOUNDS:
            add(bigram)
    if 1 < len(words) <= 5:
        add(phrase)
    for bigram in bigrams[:3]:
        add(bigram)
    for word in words[:5]:
        add(word)
    for tag in CATEGORY_TAGS.get((category or "").lower(), []):
        add(tag)
    for tag in extra:
        add(tag)
    add("science shorts")
    tags.append(BRAND_TAG)
    return tags


def hashtags_from_tags(tags: Sequence[str], category: str = "", limit: int = HASHTAGS_MAX) -> List[str]:
    """3-5 hashtags: two topic words, two category tags, then #beyond80 last."""
    chosen: List[str] = []

    def add(tag: str) -> None:
        token = re.sub(r"[^a-z0-9]", "", tag.lower())
        if 3 <= len(token) <= 24 and token not in chosen and token != BRAND_TAG:
            chosen.append(token)

    compounds = [t for t in tags if t in _COMPOUNDS]
    covered = {w for c in compounds for w in c.split()}
    single_words = [t for t in tags if " " not in t and t not in (BRAND_TAG, "science shorts")]
    category_tags = CATEGORY_TAGS.get((category or "").lower(), [])
    topic_first = compounds[:1] + [t for t in single_words if t not in category_tags and t not in covered]
    for tag in topic_first[:2]:
        add(tag)
    for tag in category_tags[:2]:
        add(tag)
    for tag in single_words:
        if len(chosen) >= limit - 1:
            break
        add(tag)
    if not chosen:
        add("science")
    return [f"#{t}" for t in chosen[: limit - 1]] + [f"#{BRAND_TAG}"]


# --------------------------------------------------------------------------- description

def _first_sentences(texts: Sequence[str], count: int = 2, max_len: int = SENTENCE_MAX_CHARS) -> List[str]:
    out: List[str] = []
    for text in texts:
        for sentence in _SENTENCE_SPLIT.split((text or "").strip()):
            sentence = _MULTI_SPACE.sub(" ", sentence).strip()
            if not sentence:
                continue
            if len(sentence) > max_len:
                sentence = _truncate_words(sentence, max_len, min_keep=max_len // 2)
            if sentence[-1] not in ".!?":
                sentence += "."
            if sentence not in out:
                out.append(sentence)
            if len(out) == count:
                return out
    return out


def question_for(category: str) -> str:
    return CATEGORY_QUESTIONS.get((category or "").lower(), DEFAULT_QUESTION)


def build_description(
    fact_sources: Sequence[str],
    category: str,
    hashtags: Sequence[str],
    source_urls: Sequence[str] = (),
) -> str:
    sentences = _first_sentences(fact_sources)
    parts: List[str] = []
    if sentences:
        parts.append(" ".join(sentences))
    parts.append(question_for(category))
    urls = [u for u in source_urls if u][:SOURCES_MAX]
    if urls:
        parts.append("Sources:\n" + "\n".join(urls))
    parts.append(" ".join(hashtags))
    return "\n\n".join(parts)


def pinned_comment_for(category: str) -> str:
    return f"{question_for(category)} {PINNED_COMMENT_SUFFIX}"


# --------------------------------------------------------------------------- entry point

def load_brief_for_job(job: ProductionJob) -> ResearchBrief | None:
    """The research brief the orchestrator wrote next to the job's outputs, if any."""
    if not job.output_dir:
        return None
    path = Path(job.output_dir) / "research_brief.json"
    if not path.exists():
        return None
    try:
        return ResearchBrief.model_validate_json(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - a broken brief must not block publishing
        logger.warning(f"Could not read research brief at {path}: {exc}")
        return None


def build_publish_metadata(
    job: ProductionJob,
    platform: PublishingPlatform = PublishingPlatform.YOUTUBE_SHORTS,
    brief: ResearchBrief | None = None,
    title_override: str | None = None,
    category: str | None = None,
) -> PublishMetadata:
    """Hook-first title, question-led description, per-video tags and a comment for ``job``."""
    brief = brief or load_brief_for_job(job)
    topic_text = (brief.topic if brief and brief.topic else job.topic) or ""

    category_text = " ".join(filter(None, [job.topic, topic_text, brief.proposed_title if brief else ""]))
    resolved_category = resolve_category(
        category or (category_from_brief_id(brief.brief_id) if brief else ""), category_text
    )

    title = choose_title(
        [
            title_override,
            brief.headline if brief else None,
            brief.proposed_title if brief else None,
            *(brief.alternative_hooks if brief else []),
            job.topic,
        ]
    )
    if not title:
        title = clean_title(job.topic) or "Beyond 80"

    tags = build_tags(topic_text or job.topic, resolved_category)
    hashtags = hashtags_from_tags(tags, resolved_category)

    fact_sources: List[str] = []
    source_urls: List[str] = []
    if brief:
        fact_sources.extend(brief.surprising_revelations)
        fact_sources.extend(brief.verified_facts)
        source_urls.extend(e.url for e in brief.supporting_evidence)
    if job.script_summary:
        fact_sources.append(job.script_summary)
    if not fact_sources:
        fact_sources.append(clean_title(job.topic, drop_parentheticals=False))

    description = build_description(fact_sources, resolved_category, hashtags, source_urls)
    if platform != PublishingPlatform.YOUTUBE_SHORTS:
        # Reels and TikTok have no separate title field; lead the caption with it.
        description = f"{title}\n\n{description}"

    return PublishMetadata(
        title=title,
        description=description,
        tags=tags,
        pinned_comment=pinned_comment_for(resolved_category),
        category=resolved_category,
        hashtags=hashtags,
    )
