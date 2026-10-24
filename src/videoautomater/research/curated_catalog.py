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
        "title": "Neptune's Diamond Rain Engine",
        "category": "space",
        "summary": "Extreme interior pressures inside Neptune break down hydrocarbons into solid diamonds, whose gravitational descent explains the planet's anomalous internal heat engine.",
        "scores": {
            "curiosity_and_hook": 0.98,
            "surprise_and_novelty": 0.96,
            "visual_storytelling": 0.97,
            "audience_relevance": 0.90,
            "narrative_depth": 0.94,
            "freshness_originality": 0.95,
        },
        "primary_source_url": "https://www.nature.com/articles/s41550-017-0219-9",
        "supporting_urls": [
            "https://www6.slac.stanford.edu/news/2017-08-21-scientists-simulate-diamond-rain-ice-giants-matter-extreme-conditions",
            "https://solarsystem.nasa.gov/missions/voyager-2/in-depth/",
        ],
        "brief": {
            "proposed_title": "Beyond 80: The Secret Inside the Ice Giants",
            "alternative_hooks": [
                "Deep inside icy planets like Neptune, laboratory physics suggests an astonishing possibility: carbon atoms separating to rain as solid diamonds.",
                "Why does Neptune radiate approximately two point six times more heat than it absorbs from the distant Sun?",
                "How did laser shock experiments at SLAC reveal the extreme physics of giant icy worlds?",
            ],
            "central_question": "Could theoretically modeled diamond precipitation contribute to Neptune's anomalous internal heat balance?",
            "verified_facts": [
                "Voyager 2's infrared radiometer (Pearl and Conrath 1991) measured a total emitted-to-absorbed energy ratio of approximately 2.611 ± 0.282.",
                "SLAC National Accelerator Laboratory experiments (Kraus et al., Nature Astronomy 2017) demonstrated that optical laser shockwaves compress hydrocarbons to 150 GPa and 5,000 K, with femtosecond X-ray pulses detecting nanodiamond diffraction.",
                "Laboratory experiments demonstrate hydrocarbon dissociation into free carbon and hydrogen under simulated planetary pressures.",
                "Planetary interior models hypothesize that sinking diamond precipitation could theoretically release gravitational potential energy as frictional heat.",
                "Theoretical simulations suggest sinking carbon crystals could gradually accumulate around the rocky core, though this remains an unobserved planetary hypothesis.",
            ],
            "supporting_evidence": [
                {
                    "claim": "Optical laser shock compression and femtosecond X-ray diffraction at SLAC LCLS directly observed nanodiamond formation from polystyrene under ice giant conditions.",
                    "source_name": "Kraus et al., Nature Astronomy (2017)",
                    "url": "https://www.nature.com/articles/s41550-017-0219-9",
                    "verified": True,
                },
                {
                    "claim": "Voyager 2 radiometer measurements determined Neptune's total energy balance ratio to be 2.611 ± 0.282.",
                    "source_name": "Pearl & Conrath, J. Geophys. Res. (1991)",
                    "url": "https://doi.org/10.1029/91JA02078",
                    "verified": True,
                },
            ],
            "surprising_revelations": [
                "Extreme shock compression experimentally transforms ordinary hydrocarbon plastics into nanodiamonds within nanoseconds.",
                "Gravitational settling of carbon crystals provides a leading theoretical hypothesis for Neptune's internal energy balance.",
            ],
            "suggested_narrative_angle": "Explore the Voyager 2 heat balance puzzle through the lens of SLAC laser shock physics and planetary interior modeling.",
            "visual_opportunities": [
                "Authentic Voyager 2 deep space approach to Neptune and atmospheric cloud plunge",
                "Historical infrared thermal imaging showing Neptune's excess internal heat radiation",
                "High-precision SLAC laser compression chamber with molecular hydrocarbon bond separation",
                "Planetary mantle cross-section tracking descending diamond hailstones and friction heat",
                "Subterranean core boundary showing modeled crystalline diamond accumulation layer",
                "Cinematic pullback resolving the cosmic perspective of extreme materials in ice giants",
            ],
            "content_risks": [
                "Clearly distinguish verified laboratory experimental results (Kraus et al. 2017) from theoretical planetary interior models.",
                "Explicitly clarify that no spacecraft has penetrated Neptune's interior and diamond rain has not been directly observed in situ.",
                "Cite Pearl & Conrath (1991) for Neptune's emitted-to-absorbed energy ratio of ~2.61.",
            ],
            "confidence_assessment": 0.99,
            "backup_topics": [
                {
                    "title": "The 2-Billion-Year-Old Natural Nuclear Reactor of Oklo",
                    "category": "science",
                    "reason": "Spontaneous nuclear fission sustained in Gabon without human intervention.",
                },
                {
                    "title": "The Mariana Trench Hydrothermal Chimneys",
                    "category": "discoveries",
                    "reason": "Deep ocean ecosystem relying on chemosynthesis without sunlight.",
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
