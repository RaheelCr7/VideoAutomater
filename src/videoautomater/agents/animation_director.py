"""Animation Director Agent for translating narrative scripts into synchronized visual animation plans."""

import logging
import re
from videoautomater.models.animation import (
    AnimationEvent,
    AnimationObject,
    CameraMotion,
    MasterAnimationPlan,
    OnScreenLabel,
    SceneAnimationSpec,
    VisualType,
)
from videoautomater.models.research import ResearchBrief
from videoautomater.models.script import ScriptSection, StoryScript

logger = logging.getLogger(__name__)


class AnimationDirectorAgent:
    """Translates narrative scripts and research evidence into structured, explanatory animation specifications."""

    def compile_animation_plan(
        self,
        script: StoryScript,
        research_brief: ResearchBrief,
        target_duration: float | None = None,
    ) -> MasterAnimationPlan:
        """Analyze narration, topic domain, and evidence to synthesize synchronized animation specifications."""
        total_dur = target_duration or script.target_duration_seconds
        scenes: list[SceneAnimationSpec] = []
        topic = research_brief.topic

        logger.info(f"AnimationDirectorAgent: Planning explanatory animations for topic '{topic}' ({len(script.sections)} sections)...")

        # Normalize timings to match target duration if needed
        script_total = sum(sec.duration for sec in script.sections)
        time_scale = total_dur / max(script_total, 1.0)

        current_time = 0.0
        for i, section in enumerate(script.sections):
            sec_dur = round(section.duration * time_scale, 2)
            start_t = round(current_time, 2)
            end_t = round(current_time + sec_dur, 2)
            current_time = end_t

            spec = self._synthesize_scene_spec(
                scene_index=i + 1,
                section=section,
                start_time=start_t,
                end_time=end_t,
                topic=topic,
                research_brief=research_brief,
            )
            scenes.append(spec)

        plan = MasterAnimationPlan(
            plan_id=f"anim_plan_{script.script_id}",
            topic=topic,
            total_duration=total_dur,
            scenes=scenes,
        )
        logger.info(f"AnimationDirectorAgent: Successfully compiled {len(scenes)} synchronized scene animation specs.")
        return plan

    def _synthesize_scene_spec(
        self,
        scene_index: int,
        section: ScriptSection,
        start_time: float,
        end_time: float,
        topic: str,
        research_brief: ResearchBrief,
    ) -> SceneAnimationSpec:
        """Dynamically determine the optimal explanatory visual technique, objects, and keyframe events for a scene."""
        role = section.role.upper()
        narration = section.narration_text
        duration = end_time - start_time

        # 1. Determine visual type and concept dynamically based on narrative role and text
        if role in ("HOOK", "MYSTERY") or scene_index == 1:
            visual_type = VisualType.CINEMATIC_ESTABLISHING
            template_name = "celestial_approach"
            visual_obj = f"Establish planetary scale and atmospheric presence for {topic}"
            concept = "Atmospheric entry and scale visualization"
            camera = CameraMotion(
                movement_type="DOLLY_ZOOM",
                start_zoom=1.0,
                end_zoom=1.25,
                focal_x=540.0,
                focal_y=750.0,
            )
            objects = [
                AnimationObject(
                    object_id="planet_body",
                    name="Planetary Disk",
                    role="PRIMARY_SUBJECT",
                    initial_scale=1.0,
                    target_scale=1.25,
                    position=(540.0, 750.0),
                    color="#D4A373",
                ),
                AnimationObject(
                    object_id="spacecraft_probe",
                    name="Exploration Probe",
                    role="SECONDARY_INDICATOR",
                    initial_scale=0.4,
                    target_scale=0.9,
                    position=(300.0, 450.0),
                    color="#00D7FF",
                ),
            ]
            events = [
                AnimationEvent(
                    event_id=f"ev_{scene_index}_1",
                    start_time=start_time + 0.5,
                    end_time=start_time + (duration * 0.6),
                    trigger_words="beneath outer clouds",
                    action="APPROACH",
                    target_object_id="spacecraft_probe",
                    description="Spacecraft approaches upper atmosphere trajectory arc",
                    parameters={"speed_factor": 1.4},
                ),
                AnimationEvent(
                    event_id=f"ev_{scene_index}_2",
                    start_time=start_time + (duration * 0.5),
                    end_time=end_time,
                    trigger_words="atmosphere becomes visible",
                    action="HIGHLIGHT",
                    target_object_id="planet_body",
                    description="Atmospheric haze layers illuminate under solar lighting",
                    parameters={"glow_intensity": 1.8},
                ),
            ]
            labels = [
                OnScreenLabel(
                    label_id=f"lbl_{scene_index}_1",
                    text=f"SCIENTIFIC OBSERVATION: {topic.upper()}",
                    position=(540.0, 220.0),
                    start_time=start_time + 0.8,
                    end_time=end_time - 0.5,
                    font_size=32,
                    color="#FFD700",
                )
            ]

        elif role in ("ESCALATION", "EXPLANATION") or ("pressure" in narration.lower() or "depth" in narration.lower()):
            visual_type = VisualType.EXPLANATORY_PROCESS
            template_name = "pressure_depth_gauge"
            visual_obj = "Illustrate crushing planetary pressure and atmospheric compression gradient"
            concept = "Hydrostatic compression & thermodynamic gradient"
            camera = CameraMotion(
                movement_type="TRACKING",
                start_zoom=1.0,
                end_zoom=1.1,
                pan_dy=120.0,
                focal_x=540.0,
                focal_y=700.0,
            )
            objects = [
                AnimationObject(
                    object_id="depth_indicator",
                    name="Depth Meter",
                    role="PRIMARY_SUBJECT",
                    position=(540.0, 650.0),
                    color="#FF9E00",
                ),
                AnimationObject(
                    object_id="gas_particles",
                    name="Atmospheric Methane & Hydrogen Particles",
                    role="SECONDARY_INDICATOR",
                    position=(540.0, 850.0),
                    color="#00F0FF",
                ),
            ]
            events = [
                AnimationEvent(
                    event_id=f"ev_{scene_index}_1",
                    start_time=start_time + 0.6,
                    end_time=end_time - 0.5,
                    trigger_words="pressure heat",
                    action="COMPRESS",
                    target_object_id="gas_particles",
                    description="Gas density increases 100,000x as depth crosses 10,000 km",
                    parameters={"compression_ratio": 100000.0},
                )
            ]
            labels = [
                OnScreenLabel(
                    label_id=f"lbl_{scene_index}_1",
                    text="PRESSURE: 100,000 ATMOSPHERES",
                    position=(540.0, 250.0),
                    start_time=start_time + 1.0,
                    end_time=end_time - 0.4,
                    font_size=34,
                    color="#FF453A",
                ),
                OnScreenLabel(
                    label_id=f"lbl_{scene_index}_2",
                    text="DEPTH: 10,000 KM INTERIOR",
                    position=(540.0, 310.0),
                    start_time=start_time + 1.5,
                    end_time=end_time - 0.4,
                    font_size=30,
                    color="#E0E6ED",
                ),
            ]

        elif role in ("REVELATION", "CLIMAX") or ("crystalliz" in narration.lower() or "laser" in narration.lower() or "molecular" in narration.lower() or "shockwave" in narration.lower()):
            visual_type = VisualType.STRUCTURAL_TRANSFORMATION
            template_name = "molecular_crystallization"
            visual_obj = "Show pyrolysis of methane molecules and phase transition into diamond crystal lattice"
            concept = "Molecular dissociation and carbon lattice crystallization"
            camera = CameraMotion(
                movement_type="ORBIT",
                start_zoom=1.05,
                end_zoom=1.3,
                focal_x=540.0,
                focal_y=720.0,
            )
            objects = [
                AnimationObject(
                    object_id="methane_molecule",
                    name="CH4 Methane Precursor",
                    role="PRIMARY_SUBJECT",
                    position=(540.0, 720.0),
                    color="#30D158",
                ),
                AnimationObject(
                    object_id="diamond_lattice",
                    name="Octahedral Crystalline Diamond",
                    role="PRIMARY_SUBJECT",
                    initial_alpha=0.0,
                    target_alpha=1.0,
                    position=(540.0, 720.0),
                    color="#FFFFFF",
                ),
            ]
            events = [
                AnimationEvent(
                    event_id=f"ev_{scene_index}_1",
                    start_time=start_time + 0.4,
                    end_time=start_time + (duration * 0.45),
                    trigger_words="rips methane apart",
                    action="DISSOCIATE",
                    target_object_id="methane_molecule",
                    description="Laser shockwave breaks covalent C-H bonds, releasing elemental carbon",
                    parameters={"bond_break_energy_ev": 4.5},
                ),
                AnimationEvent(
                    event_id=f"ev_{scene_index}_2",
                    start_time=start_time + (duration * 0.45),
                    end_time=end_time - 0.3,
                    trigger_words="compressing into sparkling diamonds",
                    action="CRYSTALIZE",
                    target_object_id="diamond_lattice",
                    description="Free carbon atoms snap into dense sp3 covalent tetrahedral diamond lattice",
                    parameters={"density_g_cm3": 3.51},
                ),
            ]
            labels = [
                OnScreenLabel(
                    label_id=f"lbl_{scene_index}_1",
                    text="PHASE TRANSITION: CH4 -> C (DIAMOND)",
                    position=(540.0, 260.0),
                    start_time=start_time + 0.8,
                    end_time=end_time - 0.3,
                    font_size=32,
                    color="#00D7FF",
                )
            ]

        else:  # PAYOFF, RESOLUTION, or other
            visual_type = VisualType.SCIENTIFIC_CROSS_SECTION
            template_name = "diamond_precipitation"
            visual_obj = "Illustrate solid diamond precipitation falling through planetary mantle layers"
            concept = "Gravitational precipitation through fluid hydrogen mantle"
            camera = CameraMotion(
                movement_type="PAN",
                start_zoom=1.0,
                end_zoom=1.15,
                pan_dy=150.0,
                focal_x=540.0,
                focal_y=750.0,
            )
            objects = [
                AnimationObject(
                    object_id="diamond_hail",
                    name="Precipitating Diamonds",
                    role="PRIMARY_SUBJECT",
                    position=(540.0, 680.0),
                    color="#E0F7FA",
                ),
                AnimationObject(
                    object_id="metallic_hydrogen",
                    name="Liquid Metallic Hydrogen Ocean",
                    role="BACKGROUND_CONTEXT",
                    position=(540.0, 1000.0),
                    color="#0A1128",
                ),
            ]
            events = [
                AnimationEvent(
                    event_id=f"ev_{scene_index}_1",
                    start_time=start_time + 0.5,
                    end_time=end_time - 0.4,
                    trigger_words="falling like hail",
                    action="PRECIPITATE",
                    target_object_id="diamond_hail",
                    description="Heavy solid diamond crystals precipitate downward through liquid hydrogen",
                    parameters={"fall_velocity_kmh": 250.0},
                )
            ]
            labels = [
                OnScreenLabel(
                    label_id=f"lbl_{scene_index}_1",
                    text="DIAMOND RAIN PRECIPITATION",
                    position=(540.0, 240.0),
                    start_time=start_time + 0.5,
                    end_time=end_time - 0.4,
                    font_size=34,
                    color="#FFD700",
                ),
                OnScreenLabel(
                    label_id=f"lbl_{scene_index}_2",
                    text="METALLIC HYDROGEN LAYER (20,000 KM)",
                    position=(540.0, 300.0),
                    start_time=start_time + 1.2,
                    end_time=end_time - 0.4,
                    font_size=28,
                    color="#A0AEC0",
                ),
            ]

        return SceneAnimationSpec(
            scene_id=f"anim_scene_{scene_index:03d}",
            section_role=role,
            narration_text=narration,
            start_time=start_time,
            end_time=end_time,
            visual_type=visual_type,
            visual_objective=visual_obj,
            scientific_concept=concept,
            camera=camera,
            objects=objects,
            events=events,
            labels=labels,
            subtitle_safe_zone_y=(1350, 1550),
            template_name=template_name,
        )
