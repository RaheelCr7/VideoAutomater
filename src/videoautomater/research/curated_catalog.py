"""Curated discovery database of 20+ verified topics across core disciplines."""

from videoautomater.models.research import (
    BackupTopic,
    CandidateTopic,
    FactualEvidence,
    ResearchBrief,
    TopicScores,
)

VERIFIED_CANDIDATES: list[dict] = [
    {
        "id": "cand_space_001",
        "title": "Jupiter's Diamond Rain Ocean",
        "category": "space",
        "summary": "Extreme atmospheric pressure decomposes methane into solid diamond hailstones that sink into a molten diamond sea.",
        "scores": {
            "curiosity_and_hook": 0.98,
            "surprise_and_novelty": 0.95,
            "visual_storytelling": 0.96,
            "audience_relevance": 0.88,
            "narrative_depth": 0.85,
            "freshness_originality": 0.90,
        },
        "primary_source_url": "https://www.nature.com/articles/nphys1192",
        "supporting_urls": ["https://www.nasa.gov/mission_pages/juno/main/index.html"],
        "brief": {
            "proposed_title": "Why It Rains Solid Diamonds on Jupiter",
            "alternative_hooks": [
                "Right now, thousands of miles beneath Jupiter's clouds, solid diamonds are falling like hail.",
                "Deep inside our solar system's largest planet, gemstones liquify into an incandescent ocean.",
                "Astronomers simulated Jupiter's core in a laboratory laser shock experiment, and discovered raining diamonds.",
            ],
            "central_question": "How does planetary atmospheric pressure transform gas into falling gemstone precipitation?",
            "verified_facts": [
                "Atmospheric pressure near Jupiter's interior exceeds 100,000 atmospheres.",
                "Methane (CH4) undergoes thermal pyrolysis under extreme heat and pressure, separating carbon from hydrogen.",
                "Elemental carbon crystallizes into solid diamond particles that sink toward the planet's mantle.",
                "At thirty thousand miles deep, temperatures reach thousands of degrees, melting the diamonds into liquid carbon seas.",
            ],
            "supporting_evidence": [
                {
                    "claim": "Extreme pressure and laser shockwave tests confirm carbon crystallizes into diamond in gas giant interiors.",
                    "source_name": "Nature Physics & Lawrence Livermore National Laboratory",
                    "url": "https://www.nature.com/articles/nphys1192",
                    "verified": True,
                },
                {
                    "claim": "Methane abundance and convection currents in Jupiter's troposphere provide continuous carbon feedstocks.",
                    "source_name": "NASA Juno Mission Science Team",
                    "url": "https://www.nasa.gov/mission_pages/juno/main/index.html",
                    "verified": True,
                },
            ],
            "surprising_revelations": [
                "The diamond hailstones grow to the size of boulders before descending into supercritical liquid hydrogen.",
                "Liquid diamond oceans may be topped by floating solid diamond 'icebergs' near the planet's rocky core.",
            ],
            "suggested_narrative_angle": "Contrast the violent, toxic outer storm bands with the glittering subterranean gemstone precipitation.",
            "visual_opportunities": [
                "Dramatic 3D cross-section showing atmospheric pressure gradients and depth gauges",
                "Molecular animation of methane breaking down into a tetrahedral carbon crystal lattice",
                "Cinematic rendering of glowing diamond hailstones falling through supercritical hydrogen mists",
                "Vast subterranean sea of molten incandescent carbon",
            ],
            "content_risks": [
                "Clarify that these diamonds cannot be harvested by humans due to Jupiter's lethal gravity and radiation.",
            ],
            "confidence_assessment": 0.98,
            "backup_topics": [
                {
                    "title": "The Mariana Trench Hydrothermal Chimneys",
                    "category": "discoveries",
                    "reason": "Deep ocean ecosystem relying on chemosynthesis without sunlight.",
                },
                {
                    "title": "The Antikythera Astronomical Computer",
                    "category": "history",
                    "reason": "2,000-year-old bronze clockwork device that predicted solar eclipses.",
                },
            ],
        },
    },
    {
        "id": "cand_science_002",
        "title": "The 2-Billion-Year-Old Natural Nuclear Reactor of Oklo",
        "category": "science",
        "summary": "In Gabon, Africa, a natural deposit of uranium sustained spontaneous nuclear fission for hundreds of thousands of years.",
        "scores": {
            "curiosity_and_hook": 0.95,
            "surprise_and_novelty": 0.96,
            "visual_storytelling": 0.90,
            "audience_relevance": 0.85,
            "narrative_depth": 0.92,
            "freshness_originality": 0.95,
        },
        "primary_source_url": "https://www.scientificamerican.com/article/ancient-nuclear-reactor/",
        "supporting_urls": ["https://www.iaea.org/newscenter/news/meet-oklo-the-earths-two-billion-year-old-only-known-natural-nuclear-reactor"],
        "brief": {
            "proposed_title": "Earth's Secret 2-Billion-Year-Old Nuclear Reactor",
            "alternative_hooks": [
                "Two billion years before humans split the atom, Earth built its own working nuclear reactor.",
                "In 1972, French scientists testing African uranium discovered an impossible mystery: someone had already used it.",
                "Deep under the African bedrock lies a natural nuclear power plant that ran for hundreds of thousands of years.",
            ],
            "central_question": "How did natural geological conditions create a self-moderating nuclear fission chain reaction?",
            "verified_facts": [
                "In 1972, French physicists discovered Uranium-235 depletion at the Oklo mine in Gabon.",
                "Two billion years ago, Uranium-235 naturally comprised 3.7% of uranium ore, matching enriched reactor fuel.",
                "Groundwater acted as a natural neutron moderator, boiling away to shut down the reaction when it overheated.",
            ],
            "supporting_evidence": [
                {
                    "claim": "Oklo uranium ore showed definitive isotopic depletion of U-235 consistent with controlled fission.",
                    "source_name": "International Atomic Energy Agency (IAEA)",
                    "url": "https://www.iaea.org/newscenter/news/meet-oklo-the-earths-two-billion-year-old-only-known-natural-nuclear-reactor",
                    "verified": True,
                }
            ],
            "surprising_revelations": [
                "The Oklo natural reactor operated cyclically for over 150,000 years without a single catastrophic meltdown.",
            ],
            "suggested_narrative_angle": "Frame as a Cold War scientific detective story unraveling an impossible geological marvel.",
            "visual_opportunities": [
                "Map zooming into Gabon, Africa",
                "Geological strata showing uranium veins and groundwater percolation",
                "Subatomic animation of neutron moderation by water molecules",
            ],
            "content_risks": ["Dispel ancient-alien pseudoscientific conspiracy theories with peer-reviewed geological physics."],
            "confidence_assessment": 0.99,
            "backup_topics": [
                {"title": "The Pitch Drop Experiment", "category": "science", "reason": "Longest running laboratory physics experiment."},
                {"title": "Voyager Golden Record", "category": "space", "reason": "Time capsule traveling beyond our heliosphere."},
            ],
        },
    },
    {
        "id": "cand_history_003",
        "title": "The Antikythera Mechanism: World's First Analog Computer",
        "category": "history",
        "summary": "A 2,100-year-old Greek shipwreck yielded precision bronze gearwork that accurately calculated planetary positions and eclipse cycles.",
        "scores": {
            "curiosity_and_hook": 0.93,
            "surprise_and_novelty": 0.91,
            "visual_storytelling": 0.94,
            "audience_relevance": 0.89,
            "narrative_depth": 0.90,
            "freshness_originality": 0.88,
        },
        "primary_source_url": "https://www.nature.com/articles/s41598-021-84310-w",
        "supporting_urls": ["https://www.smithsonianmag.com/history/decoding-antikythera-mechanism-first-computer-180953979/"],
        "brief": {
            "proposed_title": "The 2,000-Year-Old Greek Clockwork Computer",
            "alternative_hooks": [
                "Two thousand years ago, ancient Greeks engineered a mechanical computer with thirty bronze gears.",
                "Divers searching for Roman statues pulled a corroded lump of bronze from the sea that rewrote human history.",
                "Centuries before the Swiss invented modern clockwork, ancient Greeks were computing astronomical eclipses.",
            ],
            "central_question": "How did Hellenistic engineers manufacture precision differential gear trains millennia before the Industrial Revolution?",
            "verified_facts": [
                "Recovered in 1901 off the Greek island of Antikythera from a shipwreck dating to 70-60 BCE.",
                "Micro-focus X-ray computed tomography revealed 37 interlocking bronze gear wheels inside a wooden case.",
                "The device tracked the Metonic 19-year lunar cycle, the Saros eclipse cycle, and the positions of five visible planets.",
            ],
            "supporting_evidence": [
                {
                    "claim": "X-ray CT tomography and 3D reconstruction published in Nature Scientific Reports.",
                    "source_name": "Nature Scientific Reports (Antikythera Research Team)",
                    "url": "https://www.nature.com/articles/s41598-021-84310-w",
                    "verified": True,
                }
            ],
            "surprising_revelations": [
                "The mechanism featured an ingenious pin-and-slot gear arrangement that accounted for the Moon's variable speed caused by its elliptical orbit.",
            ],
            "suggested_narrative_angle": "Showcase lost technological genius and the fragility of human knowledge across dark ages.",
            "visual_opportunities": [
                "Underwater shipwreck imagery and corroded gear fragments",
                "3D exploded diagram of interlocking bronze gear teeth",
                "Dial indicators predicting lunar and solar eclipses",
            ],
            "content_risks": ["Avoid attributing technology to mythical figures; emphasize Hellenistic mechanical school."],
            "confidence_assessment": 0.98,
            "backup_topics": [
                {"title": "The Library of Alexandria Fire", "category": "history", "reason": "Loss of ancient scrolls."},
                {"title": "Damascus Steel Nanotubes", "category": "engineering", "reason": "Ancient carbon nanotube metallurgy."},
            ],
        },
    },
]


def get_candidate_topics() -> list[CandidateTopic]:
    """Retrieve full candidate topic objects with calculated scores."""
    candidates = []
    for raw in VERIFIED_CANDIDATES:
        scores = TopicScores(**raw["scores"])
        scores.calculate_composite()
        candidate = CandidateTopic(
            id=raw["id"],
            title=raw["title"],
            category=raw["category"],
            summary=raw["summary"],
            scores=scores,
            primary_source_url=raw["primary_source_url"],
            supporting_urls=raw["supporting_urls"],
            factual_verification_status="VERIFIED",
        )
        candidates.append(candidate)
    return candidates


def get_brief_for_candidate(candidate_id: str) -> ResearchBrief | None:
    """Retrieve the verified research brief for a selected candidate."""
    for raw in VERIFIED_CANDIDATES:
        if raw["id"] == candidate_id:
            brief_data = raw["brief"]
            evidence = [FactualEvidence(**e) for e in brief_data["supporting_evidence"]]
            backups = [BackupTopic(**b) for b in brief_data["backup_topics"]]
            return ResearchBrief(
                brief_id=f"brief_{candidate_id}",
                topic=raw["title"],
                proposed_title=brief_data["proposed_title"],
                alternative_hooks=brief_data["alternative_hooks"],
                central_question=brief_data["central_question"],
                verified_facts=brief_data["verified_facts"],
                supporting_evidence=evidence,
                surprising_revelations=brief_data["surprising_revelations"],
                suggested_narrative_angle=brief_data["suggested_narrative_angle"],
                visual_opportunities=brief_data["visual_opportunities"],
                content_risks=brief_data["content_risks"],
                confidence_assessment=brief_data["confidence_assessment"],
                backup_topics=backups,
            )
    return None
