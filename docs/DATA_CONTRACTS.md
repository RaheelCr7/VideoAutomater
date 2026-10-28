# VideoAutomater — Data Contracts & Schemas (V1.0)

This document specifies the exact JSON schemas and Pydantic data models used throughout VideoAutomater. All inter-agent and inter-module communications strictly adhere to these contracts.

---

## 1. Content Research Schemas

### 1.1 Candidate Topic (`CandidateTopic`)
```json
{
  "id": "uuid-v4",
  "title": "The Quantum Paradox of the Voynich Manuscript",
  "category": "science | technology | history | space | engineering | discoveries | unusual_events",
  "summary": "Brief explanation of the core finding or mystery.",
  "scores": {
    "curiosity_and_hook": 0.92,
    "surprise_and_novelty": 0.88,
    "visual_storytelling": 0.85,
    "audience_relevance": 0.80,
    "narrative_depth": 0.75,
    "freshness_originality": 0.90,
    "composite_score": 0.865
  },
  "primary_source_url": "https://doi.org/10.1038/example",
  "supporting_urls": ["https://nasa.gov/article-1"],
  "factual_verification_status": "VERIFIED | UNVERIFIED | REJECTED",
  "created_at": "2026-10-24T14:00:00Z"
}
```

### 1.2 Research Brief (`ResearchBrief`)
Passed from `ContentResearchAgent` to `ScriptwritingAgent`:
```json
{
  "brief_id": "brief_20261024_001",
  "topic": "The Mystery of Jupiter's Diamond Rain",
  "proposed_title": "Why Diamonds Fall From Jupiter's Sky",
  "headline": "It Rains Diamonds on Jupiter. Here's Why.",
  "alternative_hooks": [
    "Right now, it is literally raining solid diamonds on Jupiter.",
    "Deep inside the largest planet in our solar system, gemstones liquify and fall like hail.",
    "Astronomers just simulated Jupiter's core, and found a hidden ocean of liquid carbon diamonds."
  ],
  "central_question": "How does planetary atmospheric pressure transform methane into falling gemstone hail?",
  "verified_facts": [
    "Atmospheric pressure near Jupiter's interior exceeds 100,000 atmospheres.",
    "Methane (CH4) undergoes thermal pyrolysis, separating carbon from hydrogen.",
    "Carbon crystallizes into diamond particles that sink toward the planet's mantle."
  ],
  "supporting_evidence": [
    {
      "claim": "Atmospheric pressure exceeds 100,000 atmospheres",
      "source_name": "NASA Juno Mission Data & Nature Astronomy",
      "url": "https://nasa.gov/mission_pages/juno"
    }
  ],
  "surprising_revelations": [
    "The diamonds grow into hailstone-sized gems before melting into a liquid diamond sea."
  ],
  "suggested_narrative_angle": "Contrast the hellish storm world with the shimmering beauty of gemstone precipitation.",
  "visual_opportunities": [
    "Dynamic 3D simulation of atmospheric pressure depth gauges",
    "Diagram showing molecular separation of methane into pure diamond crystals",
    "Spectacular space telescope imagery of Jupiter's swirling Great Red Spot"
  ],
  "content_risks": [
    "Avoid implying humans could mine these diamonds, given Jupiter's crushing gravitational field."
  ],
  "confidence_assessment": 0.95,
  "backup_topics": [
    {
      "title": "The 2-Million-Year-Old Deep Biosphere Under Ocean Basalt",
      "category": "science"
    },
    {
      "title": "The Antikythera Mechanism's Hidden Eclipse Predictor",
      "category": "history"
    }
  ],
  "generated_at": "2026-10-24T14:05:00Z"
}
```

---

## 2. Creative Scriptwriting Schemas

### 2.1 Story Script (`StoryScript`)
```json
{
  "script_id": "script_20261024_001",
  "brief_id": "brief_20261024_001",
  "title": "Why Diamonds Fall From Jupiter's Sky",
  "selected_hook": "Right now, it is literally raining solid diamonds on Jupiter.",
  "target_duration_seconds": 80.0,
  "total_spoken_words": 172,
  "estimated_reading_speed_wps": 2.15,
  "sections": [
    {
      "section_id": "sec_01_hook",
      "timeline_start": 0.0,
      "timeline_end": 4.0,
      "role": "HOOK",
      "narration_text": "Right now, thousands of miles beneath Jupiter's clouds, it is literally raining solid diamonds.",
      "visual_intent": "Deep space zoom into Jupiter's violently churning ammonia cloud deck with lightning flashes."
    },
    {
      "section_id": "sec_02_mystery",
      "timeline_start": 4.0,
      "timeline_end": 14.0,
      "role": "MYSTERY",
      "narration_text": "For decades, scientists wondered why planetary atmospheric models showed unexplained carbon depletion in the upper layers.",
      "visual_intent": "Atmospheric cross-section diagram highlighting sinking methane molecules."
    },
    {
      "section_id": "sec_03_revelation",
      "timeline_start": 14.0,
      "timeline_end": 29.0,
      "role": "REVELATION",
      "narration_text": "Recent laboratory laser shockwave experiments delivered the shock: under a hundred thousand atmospheres of pressure, ordinary gas instantly crystallizes.",
      "visual_intent": "Laboratory high-pressure laser compression visualization showing carbon lattice transformation."
    },
    {
      "section_id": "sec_04_escalation",
      "timeline_start": 29.0,
      "timeline_end": 50.0,
      "role": "ESCALATION",
      "narration_text": "As these diamond hail stones plummet deeper through thousands of miles of liquid hydrogen, the friction generates temperatures hot enough to melt steel.",
      "visual_intent": "Sinking diamond hailstones glowing amidst turbulent glowing supercritical metallic hydrogen."
    },
    {
      "section_id": "sec_05_climax",
      "timeline_start": 50.0,
      "timeline_end": 66.0,
      "role": "CLIMAX",
      "narration_text": "At thirty thousand miles deep, the diamonds reach their ultimate melting point, collapsing into vast shimmering oceans of liquid carbon.",
      "visual_intent": "Cinematic visual of a subterranean sea of incandescent liquid carbon beneath planetary clouds."
    },
    {
      "section_id": "sec_06_payoff",
      "timeline_start": 66.0,
      "timeline_end": 80.0,
      "role": "PAYOFF",
      "narration_text": "In our solar system, the rarest gemstones on Earth are nothing more than an unending afternoon thunderstorm on Jupiter.",
      "visual_intent": "Pull back from the stormy giant planet into the quiet black cosmos with memorable closing typography."
    }
  ],
  "full_text": "Right now, thousands of miles beneath Jupiter's clouds..."
}
```

---

## 3. Storyboard & Media Schemas

### 3.1 Storyboard Scene (`StoryboardScene`)
```json
{
  "scene_id": "scene_001",
  "start_time": 0.0,
  "end_time": 3.8,
  "duration": 3.8,
  "asset_type": "SYNTHETIC_CANVAS | LICENSED_IMAGE | MOTION_GRAPHIC | DIAGRAM",
  "asset_source": "programmatic_render | wikimedia | nasa | public_domain",
  "local_file_path": "assets/scenes/scene_001.png",
  "motion_effect": "KEN_BURNS_ZOOM_IN | PAN_LEFT | PAN_RIGHT | PULSE",
  "transition_in": "FADE",
  "transition_duration": 0.3,
  "overlay_text": "DIAMOND HAIL ON JUPITER",
  "narration_cue": "Right now, thousands of miles beneath Jupiter's clouds..."
}
```

---

## 4. Audio & Subtitle Schemas

### 4.1 Subtitle Word Segment (`SubtitleWord`)
```json
{
  "word": "diamonds",
  "start_time": 3.12,
  "end_time": 3.65,
  "confidence": 0.99
}
```

### 4.2 Subtitle Sentence Segment (`SubtitleSegment`)
```json
{
  "index": 1,
  "start_time": 0.00,
  "end_time": 3.85,
  "text": "Right now, thousands of miles beneath Jupiter's clouds,",
  "words": [
    {"word": "Right", "start_time": 0.1, "end_time": 0.4},
    {"word": "now,", "start_time": 0.42, "end_time": 0.75}
  ]
}
```

---

## 5. Quality Assurance Schemas

### 5.1 Quality Report (`QualityReport`)
```json
{
  "report_id": "qr_20261024_001",
  "episode_id": "ep_20261024_001",
  "passed_all_mandatory_checks": true,
  "checks": [
    {
      "check_name": "DURATION_TOLERANCE",
      "required": "80.0s +/- 2.0s",
      "measured": "79.85s",
      "status": "PASS"
    },
    {
      "check_name": "DIMENSIONS_ASPECT_RATIO",
      "required": "1080x1920 (9:16)",
      "measured": "1080x1920",
      "status": "PASS"
    },
    {
      "check_name": "VIDEO_CODEC",
      "required": "h264 (yuv420p)",
      "measured": "h264 (yuv420p)",
      "status": "PASS"
    },
    {
      "check_name": "AUDIO_CODEC_AND_LOUDNESS",
      "required": "aac, -14.0 LUFS +/- 2.0",
      "measured": "aac, -14.2 LUFS",
      "status": "PASS"
    },
    {
      "check_name": "FRAME_RATE",
      "required": "30 fps",
      "measured": "30.0 fps",
      "status": "PASS"
    },
    {
      "check_name": "SUBTITLE_SYNC_AND_BOUNDS",
      "required": "Safe vertical margins, no overlap",
      "measured": "Safe margin 160px from bottom, aligned",
      "status": "PASS"
    },
    {
      "check_name": "FACTUAL_INTEGRITY",
      "required": "100% claims match research brief",
      "measured": "Verified against 3 sources",
      "status": "PASS"
    }
  ],
  "content_rating": {
    "hook_strength": 9.4,
    "pacing_score": 9.2,
    "narrative_payoff": 9.5
  },
  "reviewed_at": "2026-10-24T14:15:00Z"
}
```

---

## 6. Publishing & Accounts Schemas

### 6.1 Connected Account (`ConnectedAccount`)
```json
{
  "account_id": "acc_yt_01",
  "platform": "YOUTUBE",
  "account_name": "Cosmic Chronicles (Official)",
  "channel_id": "UCxxxxxxx",
  "is_active": true,
  "rate_limits": {
    "max_posts_per_day": 3,
    "min_spacing_minutes": 180
  },
  "auth_token_encrypted_path": "secrets/tokens/acc_yt_01.enc",
  "last_health_check": "2026-10-24T12:00:00Z",
  "health_status": "VALID"
}
```

### 6.2 Publishing Job (`PublishingJob`)
```json
{
  "job_id": "pub_job_20261024_001_yt",
  "episode_id": "ep_20261024_001",
  "account_id": "acc_yt_01",
  "platform": "YOUTUBE",
  "master_video_path": "output/episode_001/final.mp4",
  "custom_metadata": {
    "title": "Why It Rains Diamonds on Jupiter #Shorts #Science",
    "description": "Deep within Jupiter, extreme pressure creates diamond hail. Here is the science.",
    "tags": ["space", "science", "astronomy", "jupiter", "shorts"]
  },
  "scheduled_at": "2026-10-24T18:00:00Z",
  "status": "PENDING | IN_PROGRESS | PUBLISHED | FAILED | RETRYING",
  "external_post_id": null,
  "published_url": null,
  "attempt_count": 0,
  "max_attempts": 3,
  "last_error": null
}
```

---

## 7. Director Instruction Schemas

### 7.1 Director Instruction (`DirectorInstruction`)
```json
{
  "instruction_id": "inst_001",
  "target_agent": "ContentResearchAgent | ScriptwritingAgent | MediaEngineeringAgent | PublishingEngine | ALL",
  "scope": "GLOBAL | CAMPAIGN | EPISODE | TEMPORARY",
  "natural_language_prompt": "Focus research on unusual discoveries in deep ocean and extreme planetary science.",
  "status": "ACTIVE | DISABLED | EXPIRED",
  "created_at": "2026-10-24T14:00:00Z",
  "expires_at": null,
  "priority": 100
}
```
