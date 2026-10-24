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

        # 1. Determine domain and category dynamically
        cat = getattr(research_brief, "category", "general").lower()
        topic_lower = topic.lower()

        is_space = cat == "space" or any(w in topic_lower for w in ["neptune", "jupiter", "planet", "ice giant", "galaxy", "orbit", "solar"])
        is_nuclear = cat == "science" or any(w in topic_lower for w in ["oklo", "nuclear", "reactor", "fission", "uranium", "atom", "quantum"])
        is_deepsea = cat == "discoveries" or any(w in topic_lower for w in ["mariana", "trench", "ocean", "chimney", "abyss", "hydrothermal"])

        if is_space:
            # Domain: Space & Planetary Physics
            if (role in ("HOOK", "MYSTERY") or scene_index == 1) and "pressure" not in narration.lower():
                visual_type = VisualType.CINEMATIC_ESTABLISHING
                template_name = "celestial_approach"
                visual_obj = f"Establish planetary scale and atmospheric entry for {topic}"
                concept = "Planetary atmospheric plunge and high-orbit scale"
                camera = CameraMotion(movement_type="DOLLY_ZOOM", start_zoom=1.0, end_zoom=1.25, focal_x=540.0, focal_y=750.0)
                objects = [
                    AnimationObject(object_id="planet_disk", name="Planetary Disk", role="PRIMARY_SUBJECT", initial_scale=1.0, target_scale=1.25, position=(540.0, 750.0), color="#1E90FF"),
                    AnimationObject(object_id="spacecraft_voyager", name="NASA Voyager 2 Probe", role="SECONDARY_INDICATOR", initial_scale=0.5, target_scale=0.9, position=(280.0, 420.0), color="#E0E6ED"),
                ]
                events = [
                    AnimationEvent(event_id=f"ev_{scene_index}_1", start_time=start_time + 0.5, end_time=end_time, trigger_words="violent storms", action="APPROACH", target_object_id="spacecraft_voyager", description="Spacecraft camera dives into cloud deck bands", parameters={"speed": 1.3}),
                ]
                labels = [
                    OnScreenLabel(label_id=f"lbl_{scene_index}_1", text="NASA VOYAGER 2 // ICE GIANT ENCOUNTER", position=(540.0, 220.0), start_time=start_time + 0.8, end_time=end_time - 0.4, font_size=28, color="#00D7FF"),
                ]
            elif role in ("ESCALATION", "EXPLANATION") or ("pressure" in narration.lower() or "depth" in narration.lower()):
                visual_type = VisualType.EXPLANATORY_PROCESS
                template_name = "pressure_depth_gauge"
                visual_obj = "Illustrate crushing planetary pressure and atmospheric compression gradient"
                concept = "Hydrostatic compression & thermodynamic gradient"
                camera = CameraMotion(movement_type="TRACKING", start_zoom=1.0, end_zoom=1.1, pan_dy=120.0, focal_x=540.0, focal_y=700.0)
                objects = [
                    AnimationObject(object_id="depth_indicator", name="Depth Meter", role="PRIMARY_SUBJECT", position=(540.0, 650.0), color="#FF9E00"),
                    AnimationObject(object_id="gas_particles", name="Atmospheric Methane & Hydrogen Particles", role="SECONDARY_INDICATOR", position=(540.0, 850.0), color="#00F0FF"),
                ]
                events = [
                    AnimationEvent(event_id=f"ev_{scene_index}_1", start_time=start_time + 0.6, end_time=end_time - 0.5, trigger_words="pressure heat", action="COMPRESS", target_object_id="gas_particles", description="Gas density increases 100,000x as depth crosses 10,000 km", parameters={"compression_ratio": 100000.0}),
                ]
                labels = [
                    OnScreenLabel(label_id=f"lbl_{scene_index}_1", text="PRESSURE: 100,000 ATMOSPHERES", position=(540.0, 250.0), start_time=start_time + 1.0, end_time=end_time - 0.4, font_size=34, color="#FF453A"),
                    OnScreenLabel(label_id=f"lbl_{scene_index}_2", text="DEPTH: 10,000 KM INTERIOR", position=(540.0, 310.0), start_time=start_time + 1.5, end_time=end_time - 0.4, font_size=30, color="#E0E6ED"),
                ]
            elif role in ("REVELATION", "CLIMAX") or ("crystalliz" in narration.lower() or "laser" in narration.lower() or "molecular" in narration.lower() or "shockwave" in narration.lower()):
                visual_type = VisualType.STRUCTURAL_TRANSFORMATION
                template_name = "molecular_crystallization"
                visual_obj = "Show pyrolysis of methane molecules and phase transition into diamond crystal lattice"
                concept = "Molecular dissociation and carbon lattice crystallization"
                camera = CameraMotion(movement_type="ORBIT", start_zoom=1.05, end_zoom=1.3, focal_x=540.0, focal_y=720.0)
                objects = [
                    AnimationObject(object_id="hydrocarbon_molecule", name="CH4 Hydrocarbon Precursor", role="PRIMARY_SUBJECT", position=(540.0, 720.0), color="#30D158"),
                    AnimationObject(object_id="diamond_lattice", name="Tetrahedral Diamond Crystal Unit Cell", role="PRIMARY_SUBJECT", initial_alpha=0.0, target_alpha=1.0, position=(540.0, 720.0), color="#FFFFFF"),
                ]
                events = [
                    AnimationEvent(event_id=f"ev_{scene_index}_1", start_time=start_time + 0.4, end_time=start_time + (duration * 0.45), trigger_words="molecules shattered", action="DISSOCIATE", target_object_id="hydrocarbon_molecule", description="Laser shockwave breaks covalent C-H bonds", parameters={"bond_energy_ev": 4.5}),
                    AnimationEvent(event_id=f"ev_{scene_index}_2", start_time=start_time + (duration * 0.45), end_time=end_time - 0.3, trigger_words="diamond crystals", action="CRYSTALIZE", target_object_id="diamond_lattice", description="Carbon atoms lock into tetrahedral diamond lattice", parameters={"pressure_gpa": 150.0}),
                ]
                labels = [
                    OnScreenLabel(label_id=f"lbl_{scene_index}_1", text="SLAC EXPERIMENT // 150 GPa LASER SHOCKWAVE", position=(540.0, 250.0), start_time=start_time + 0.8, end_time=end_time - 0.4, font_size=28, color="#00D7FF"),
                ]
            else:
                visual_type = VisualType.SCIENTIFIC_CROSS_SECTION
                template_name = "diamond_precipitation"
                visual_obj = "Illustrate solid diamond hail sinking through supercritical fluid mantle"
                concept = "Gravitational precipitation and friction heating"
                camera = CameraMotion(movement_type="PAN", start_zoom=1.0, end_zoom=1.15, pan_dy=140.0, focal_x=540.0, focal_y=750.0)
                objects = [
                    AnimationObject(object_id="diamond_hail", name="Descending Diamond Hailstones", role="PRIMARY_SUBJECT", position=(540.0, 680.0), color="#E0F7FA"),
                    AnimationObject(object_id="supercritical_mantle", name="Supercritical Water & Ammonia Mantle", role="BACKGROUND_CONTEXT", position=(540.0, 1000.0), color="#0A1128"),
                ]
                events = [
                    AnimationEvent(event_id=f"ev_{scene_index}_1", start_time=start_time + 0.5, end_time=end_time - 0.4, trigger_words="falling like hail", action="PRECIPITATE", target_object_id="diamond_hail", description="Diamond crystals sink releasing gravitational thermal energy", parameters={"velocity_kms": 12.0}),
                ]
                labels = [
                    OnScreenLabel(label_id=f"lbl_{scene_index}_1", text="SUPERCRITICAL MANTLE // THERMAL CONVECTION", position=(540.0, 240.0), start_time=start_time + 0.5, end_time=end_time - 0.4, font_size=28, color="#FFD700"),
                ]

        elif is_nuclear:
            # Domain: Nuclear Physics & Geology (e.g. Oklo Natural Reactor)
            if role in ("HOOK", "MYSTERY") or scene_index == 1:
                visual_type = VisualType.CINEMATIC_ESTABLISHING
                template_name = "geological_descent"
                visual_obj = f"Establish ancient geological formation and location for {topic}"
                concept = "Precambrian stratigraphy and isotopic discovery"
                camera = CameraMotion(movement_type="TRACKING", start_zoom=1.0, end_zoom=1.2, pan_dy=100.0, focal_x=540.0, focal_y=750.0)
                objects = [
                    AnimationObject(object_id="geological_bedrock", name="Precambrian Francevillian Basin", role="PRIMARY_SUBJECT", position=(540.0, 750.0), color="#8B4513"),
                    AnimationObject(object_id="uranium_deposit", name="Pitchblende Uranium Ore Vein", role="SECONDARY_INDICATOR", position=(540.0, 850.0), color="#32CD32"),
                ]
                events = [
                    AnimationEvent(event_id=f"ev_{scene_index}_1", start_time=start_time + 0.5, end_time=end_time, trigger_words="nuclear reactor", action="ZOOM_TO_STRATA", target_object_id="uranium_deposit", description="Descent into subterranean pitchblende strata", parameters={"depth_meters": 120.0}),
                ]
                labels = [
                    OnScreenLabel(label_id=f"lbl_{scene_index}_1", text="OKLO, GABON // 2 BILLION YEARS AGO", position=(540.0, 220.0), start_time=start_time + 0.8, end_time=end_time - 0.4, font_size=28, color="#00D7FF"),
                ]
            elif role in ("REVELATION", "ESCALATION"):
                visual_type = VisualType.STRUCTURAL_TRANSFORMATION
                template_name = "subatomic_fission"
                visual_obj = "Show neutron moderation by groundwater and self-sustaining U-235 fission chain reaction"
                concept = "Subatomic neutron moderation and controlled fission"
                camera = CameraMotion(movement_type="ORBIT", start_zoom=1.1, end_zoom=1.35, focal_x=540.0, focal_y=720.0)
                objects = [
                    AnimationObject(object_id="u235_nucleus", name="Uranium-235 Nucleus", role="PRIMARY_SUBJECT", position=(540.0, 700.0), color="#00FF7F"),
                    AnimationObject(object_id="water_moderator", name="Groundwater Molecule Moderator", role="SECONDARY_INDICATOR", position=(420.0, 680.0), color="#00BFFF"),
                ]
                events = [
                    AnimationEvent(event_id=f"ev_{scene_index}_1", start_time=start_time + 0.4, end_time=start_time + (duration * 0.5), trigger_words="slowed neutrons down", action="MODERATE", target_object_id="water_moderator", description="Thermal neutrons slowed by hydrogen collisions", parameters={"energy_loss_pct": 98.0}),
                    AnimationEvent(event_id=f"ev_{scene_index}_2", start_time=start_time + (duration * 0.5), end_time=end_time - 0.3, trigger_words="chain reactions", action="FISSION", target_object_id="u235_nucleus", description="Sustained induced nuclear fission split", parameters={"energy_release_mev": 200.0}),
                ]
                labels = [
                    OnScreenLabel(label_id=f"lbl_{scene_index}_1", text="NATURAL U-235 FISSION // GROUNDWATER MODERATION", position=(540.0, 250.0), start_time=start_time + 0.8, end_time=end_time - 0.4, font_size=28, color="#32CD32"),
                ]
            else:
                visual_type = VisualType.EXPLANATORY_PROCESS
                template_name = "hydrothermal_cycle"
                visual_obj = "Illustrate cyclic hydrothermal pulsing preventing nuclear meltdown"
                concept = "Thermal geyser feedback loop and self-regulating shutdown"
                camera = CameraMotion(movement_type="PAN", start_zoom=1.0, end_zoom=1.15, pan_dy=120.0, focal_x=540.0, focal_y=750.0)
                objects = [
                    AnimationObject(object_id="reactor_core", name="Natural Fossil Fission Zone", role="PRIMARY_SUBJECT", position=(540.0, 720.0), color="#FFD700"),
                    AnimationObject(object_id="steam_plume", name="Hydrothermal Steam Venting", role="SECONDARY_INDICATOR", position=(540.0, 480.0), color="#F0F8FF"),
                ]
                events = [
                    AnimationEvent(event_id=f"ev_{scene_index}_1", start_time=start_time + 0.5, end_time=end_time - 0.4, trigger_words="steam pushed the water out", action="VENT_STEAM", target_object_id="steam_plume", description="Steam expulsion safely shuts down reactor for 3 hours", parameters={"cycle_minutes": 180.0}),
                ]
                labels = [
                    OnScreenLabel(label_id=f"lbl_{scene_index}_1", text="CYCLIC HYDROTHERMAL REGULATION // 150,000 YEARS", position=(540.0, 240.0), start_time=start_time + 0.5, end_time=end_time - 0.4, font_size=28, color="#FFD700"),
                ]

        else:
            # Universal Domain Fallback
            visual_type = VisualType.EXPLANATORY_PROCESS
            template_name = "empirical_investigation"
            visual_obj = f"Demonstrate physical mechanism of {topic}"
            concept = f"Scientific mechanism underlying {section.role.lower()}"
            camera = CameraMotion(movement_type="PAN", start_zoom=1.0, end_zoom=1.15, pan_dy=100.0, focal_x=540.0, focal_y=750.0)
            objects = [
                AnimationObject(object_id="core_subject", name=topic, role="PRIMARY_SUBJECT", position=(540.0, 720.0), color="#00D7FF"),
            ]
            events = [
                AnimationEvent(event_id=f"ev_{scene_index}_1", start_time=start_time + 0.5, end_time=end_time - 0.4, trigger_words="discovery", action="ANALYZE", target_object_id="core_subject", description="Empirical examination of subject", parameters={}),
            ]
            labels = [
                OnScreenLabel(label_id=f"lbl_{scene_index}_1", text=f"EMPIRICAL INVESTIGATION: {topic.upper()}", position=(540.0, 240.0), start_time=start_time + 0.5, end_time=end_time - 0.4, font_size=28, color="#FFD700"),
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
