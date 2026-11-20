import math
import random
import uuid
from typing import Dict, Any, List, Optional
from backend.app.modules.synthetic.components import (
    COMPONENT_TYPES,
    COMPONENT_NAMES,
    DEFAULT_DIMENSIONS,
    compute_polygon_bounds
)

class SceneGenerator:
    """Parametric industrial assembly scene graph generator with deterministic seeding."""

    def __init__(self, seed: Optional[int] = None):
        self.seed = seed if seed is not None else 42

    def generate_scene(
        self,
        scene_id: Optional[str] = None,
        dataset_id: str = "ds_default",
        difficulty: str = "medium",
        component_count: int = 6,
        defect_types: Optional[List[str]] = None,
        lighting: str = "standard_5000k",
        camera_perspective: str = "top_down",
        width: int = 800,
        height: int = 600,
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate a complete deterministic SceneGraph."""
        effective_seed = seed if seed is not None else self.seed
        rng = random.Random(effective_seed)

        if scene_id is None:
            scene_id = f"sc_{uuid.UUID(int=rng.getrandbits(128)).hex[:8]}"

        if defect_types is None:
            defect_types = ["missing", "misplaced", "orientation", "occlusion"]

        # Adjust component count by difficulty if default requested
        if difficulty == "easy":
            count = min(component_count, 4)
            num_defects = 1 if defect_types else 0
        elif difficulty == "hard":
            count = max(component_count, 8)
            num_defects = min(len(defect_types), rng.randint(2, 3))
        else:  # medium
            count = component_count
            num_defects = 1 if defect_types else 0

        # Workstation environment config
        ambient_map = {
            "standard_5000k": 0.80,
            "tungsten_3200k": 0.70,
            "low_light": 0.45,
            "harsh_shadows": 0.85
        }
        ambient = ambient_map.get(lighting, 0.75)
        lighting_dir = rng.choice(["top_left", "top_right", "direct"])

        workstation = {
            "fixture_type": "optical_breadboard_grid",
            "surface_color": "#141a24",
            "grid_spacing": 40,
            "lighting": {
                "ambient": ambient,
                "direction": lighting_dir,
                "shadows_enabled": True,
                "specular_highlights": True,
                "lighting_profile": lighting
            }
        }

        # 1. Always place a central foundation plate or fixture (Layer 1)
        components = []
        base_cx = rng.randint(350, 450)
        base_cy = rng.randint(260, 340)
        base_type = "mounting_plate" if rng.random() > 0.3 else "assembly_fixture"
        base_dims = dict(DEFAULT_DIMENSIONS[base_type])

        base_id = f"comp_{base_type}_0"
        base_bbox = [
            base_cx - base_dims["width"] / 2,
            base_cy - base_dims["height"] / 2,
            base_cx + base_dims["width"] / 2,
            base_cy + base_dims["height"] / 2,
        ]

        components.append({
            "id": base_id,
            "type": base_type,
            "name": COMPONENT_NAMES[base_type],
            "center": {"x": float(base_cx), "y": float(base_cy)},
            "dimensions": base_dims,
            "bbox": [round(b, 1) for b in base_bbox],
            "rotation_deg": 0.0,
            "material": "anodized_aluminum",
            "expected_position": {"x": float(base_cx), "y": float(base_cy), "rotation_deg": 0.0},
            "is_defective": False,
            "defect_type": None,
            "occlusion_ratio": 0.0,
            "visibility_score": 1.0,
            "layer": 1
        })

        # 2. Place assembly components (Layer 2)
        candidate_types = [t for t in COMPONENT_TYPES if t not in ("mounting_plate", "assembly_fixture")]
        # Ensure a diverse selection of components
        selected_types = []
        for i in range(count - 1):
            selected_types.append(candidate_types[i % len(candidate_types)])
        rng.shuffle(selected_types)

        # Decide which components will have defects
        defective_indices = set(rng.sample(range(len(selected_types)), min(num_defects, len(selected_types))))

        # Define grid slots on and around the base plate
        slots = []
        plate_w = base_dims["width"]
        plate_h = base_dims["height"]
        # Inset slots on the plate
        slots.append((base_cx - plate_w * 0.28, base_cy - plate_h * 0.25))
        slots.append((base_cx + plate_w * 0.28, base_cy - plate_h * 0.25))
        slots.append((base_cx - plate_w * 0.28, base_cy + plate_h * 0.25))
        slots.append((base_cx + plate_w * 0.28, base_cy + plate_h * 0.25))
        slots.append((base_cx, base_cy))
        # Outer workstation slots
        slots.append((base_cx - plate_w * 0.65, base_cy))
        slots.append((base_cx + plate_w * 0.65, base_cy))
        slots.append((base_cx, base_cy - plate_h * 0.70))
        slots.append((base_cx, base_cy + plate_h * 0.70))
        slots.append((base_cx - plate_w * 0.65, base_cy - plate_h * 0.55))
        slots.append((base_cx + plate_w * 0.65, base_cy + plate_h * 0.55))

        materials = ["machined_steel", "brass", "black_oxide", "anodized_aluminum", "copper"]

        for idx, ctype in enumerate(selected_types):
            slot_x, slot_y = slots[idx % len(slots)]
            dims = dict(DEFAULT_DIMENSIONS[ctype])
            comp_id = f"comp_{ctype}_{idx + 1}"

            expected_x = float(slot_x)
            expected_y = float(slot_y)
            expected_rot = 0.0

            actual_x = expected_x
            actual_y = expected_y
            actual_rot = expected_rot
            is_defective = idx in defective_indices
            defect_type = None

            if is_defective and defect_types:
                chosen_defect = rng.choice(defect_types)
                defect_type = chosen_defect
                if chosen_defect == "missing":
                    # Component is absent; expected socket exists
                    pass
                elif chosen_defect == "misplaced":
                    # Displaced by 35-55px
                    offset_angle = rng.uniform(0, 2 * math.pi)
                    offset_dist = rng.uniform(35, 55)
                    actual_x += offset_dist * math.cos(offset_angle)
                    actual_y += offset_dist * math.sin(offset_angle)
                elif chosen_defect == "orientation":
                    # Inverted or 90/180 degrees rotated
                    actual_rot = float(rng.choice([90, 180, 270]))
                elif chosen_defect == "occlusion":
                    # Handled via occlusion overlay
                    pass

            # Calculate Bounding Box
            if ctype in ("spur_gear", "hex_nut", "fastener"):
                r = dims.get("radius", 40)
                bbox = [actual_x - r, actual_y - r, actual_x + r, actual_y + r]
            elif ctype == "hex_bolt":
                r = dims.get("flange_radius", 24)
                bbox = [actual_x - r, actual_y - r, actual_x + r, actual_y + r]
            elif ctype == "pipe":
                l = dims.get("length", 160)
                d = dims.get("diameter", 26)
                bbox = [actual_x - l / 2, actual_y - d / 2, actual_x + l / 2, actual_y + d / 2]
            elif ctype == "bracket":
                w = dims.get("width", 70)
                h = dims.get("height", 70)
                bbox = [actual_x - w / 2, actual_y - h / 2, actual_x + w / 2, actual_y + h / 2]
            else:
                w = dims.get("width", 90)
                h = dims.get("height", 50)
                bbox = [actual_x - w / 2, actual_y - h / 2, actual_x + w / 2, actual_y + h / 2]

            # Clamp bbox to image canvas
            bbox = [
                max(0.0, min(float(width), bbox[0])),
                max(0.0, min(float(height), bbox[1])),
                max(0.0, min(float(width), bbox[2])),
                max(0.0, min(float(height), bbox[3])),
            ]

            visibility = 0.0 if defect_type == "missing" else (0.65 if defect_type == "occlusion" else 1.0)
            occlusion_ratio = 1.0 if defect_type == "missing" else (0.35 if defect_type == "occlusion" else 0.0)

            components.append({
                "id": comp_id,
                "type": ctype,
                "name": COMPONENT_NAMES[ctype],
                "center": {"x": round(actual_x, 1), "y": round(actual_y, 1)},
                "dimensions": dims,
                "bbox": [round(b, 1) for b in bbox],
                "rotation_deg": round(actual_rot, 1),
                "material": rng.choice(materials),
                "expected_position": {"x": round(expected_x, 1), "y": round(expected_y, 1), "rotation_deg": expected_rot},
                "is_defective": is_defective,
                "defect_type": defect_type,
                "occlusion_ratio": occlusion_ratio,
                "visibility_score": visibility,
                "layer": 2
            })

        # 3. Add Occlusions if difficulty is hard or occlusion defect injected
        occlusions = []
        has_occlusion_defect = any(c.get("defect_type") == "occlusion" for c in components)
        if difficulty == "hard" or has_occlusion_defect:
            # Wire harness crossing across components
            occluded_comp = next((c for c in components if c.get("defect_type") == "occlusion"), None)
            if occluded_comp:
                ox = occluded_comp["center"]["x"]
                oy = occluded_comp["center"]["y"]
                wire_points = [(ox - 180, oy + 40), (ox, oy), (ox + 180, oy - 30)]
            else:
                wire_points = [(150, 420), (400, 390), (680, 410)]

            occlusions.append({
                "id": "occ_wire_1",
                "type": "wire_harness",
                "points": wire_points
            })

        # 4. Add Background Clutter if medium or hard
        clutter = []
        if difficulty in ("medium", "hard"):
            num_clutter = rng.randint(1, 3 if difficulty == "hard" else 2)
            clutter_types = ["washer", "hex_key", "metal_chip"]
            for c_i in range(num_clutter):
                clutter.append({
                    "id": f"clutter_{c_i}",
                    "type": rng.choice(clutter_types),
                    "x": rng.randint(60, width - 60),
                    "y": rng.randint(60, height - 60)
                })

        # 5. Compute Spatial Relations between components
        spatial_relations = self._compute_spatial_relations(components)

        return {
            "scene_id": scene_id,
            "dataset_id": dataset_id,
            "seed": effective_seed,
            "difficulty": difficulty,
            "dimensions": {"width": width, "height": height},
            "workstation": workstation,
            "components": components,
            "spatial_relations": spatial_relations,
            "defect_types": defect_types,
            "occlusions": occlusions,
            "clutter": clutter
        }

    def _compute_spatial_relations(self, components: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Compute relative pairwise spatial relationships between components."""
        relations = []
        for i, comp_a in enumerate(components):
            for j, comp_b in enumerate(components):
                if i >= j or comp_a["id"] == comp_b["id"]:
                    continue

                ax, ay = comp_a["center"]["x"], comp_a["center"]["y"]
                bx, by = comp_b["center"]["x"], comp_b["center"]["y"]
                dx = bx - ax
                dy = by - ay
                dist = round(math.sqrt(dx * dx + dy * dy), 1)

                # Skip distant relationships (> 350px) to keep graph meaningful
                if dist > 350:
                    continue

                if abs(dx) > abs(dy):
                    rel = "left_of" if dx > 0 else "right_of"
                else:
                    rel = "above" if dy > 0 else "below"

                relations.append({
                    "subject_id": comp_a["id"],
                    "relation": rel,
                    "object_id": comp_b["id"],
                    "distance_px": dist
                })
        return relations
