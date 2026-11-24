import math
import random
import uuid
from typing import Dict, Any, List, Optional
from backend.app.modules.synthetic.components import (
    IMAGE_FAMILIES,
    RETAIL_COMPONENTS,
    MECHANICAL_COMPONENTS,
    PCB_COMPONENTS,
    AEROSPACE_COMPONENTS,
    COMPONENT_NAMES,
    DEFAULT_DIMENSIONS,
    compute_polygon_bounds
)

class SceneGenerator:
    """Parametric industrial assembly & electronics scene graph generator with deterministic seeding."""

    def __init__(self, seed: Optional[int] = None):
        self.seed = seed if seed is not None else 42

    def generate_scene(
        self,
        scene_id: Optional[str] = None,
        dataset_id: str = "ds_default",
        image_family: str = "smart_retail_shelf",
        difficulty: str = "medium",
        component_count: int = 6,
        defect_types: Optional[List[str]] = None,
        lighting: str = "standard_5000k",
        camera_perspective: str = "top_down",
        width: int = 800,
        height: int = 600,
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate a complete deterministic SceneGraph supporting multiple image families."""
        effective_seed = seed if seed is not None else self.seed
        rng = random.Random(effective_seed)

        if scene_id is None:
            scene_id = f"sc_{uuid.UUID(int=rng.getrandbits(128)).hex[:8]}"

        if defect_types is None:
            defect_types = ["missing", "misplaced", "orientation", "occlusion"]

        # Adjust component count by difficulty
        if difficulty == "easy":
            count = min(component_count, 4)
            num_defects = 1 if defect_types else 0
        elif difficulty == "hard":
            count = max(component_count, 8)
            num_defects = min(len(defect_types), rng.randint(2, 3))
        else:
            count = component_count
            num_defects = 1 if defect_types else 0

        # Workstation lighting profile
        ambient_map = {
            "standard_5000k": 0.82,
            "tungsten_3200k": 0.72,
            "low_light": 0.45,
            "harsh_shadows": 0.88
        }
        ambient = ambient_map.get(lighting, 0.78)
        lighting_dir = rng.choice(["top_left", "top_right", "direct"])

        surface_color = (
            "#1c1917" if image_family == "smart_retail_shelf"
            else ("#121822" if image_family == "mechanical_assembly"
            else ("#0f4b2a" if image_family == "pcb_electronics" else "#181a20"))
        )

        workstation = {
            "fixture_type": f"{image_family}_substrate",
            "surface_color": surface_color,
            "grid_spacing": 40,
            "lighting": {
                "ambient": ambient,
                "direction": lighting_dir,
                "shadows_enabled": True,
                "specular_highlights": True,
                "lighting_profile": lighting
            }
        }

        # 1. Base Foundation Component (Layer 1)
        components = []
        base_cx = rng.randint(380, 420)
        base_cy = rng.randint(280, 320)

        if image_family == "smart_retail_shelf":
            base_type = "retail_shelf"
            base_name = "Supermarket Display Shelf"
            base_dims = {"width": 640, "height": 380}
            candidate_types = [t for t in RETAIL_COMPONENTS]
            base_material = "retail_shelf"
        elif image_family == "pcb_electronics":
            base_type = "mounting_plate"
            base_name = "FR4 Precision PCB Board"
            base_dims = {"width": 320, "height": 220, "hole_radius": 5}
            candidate_types = [t for t in PCB_COMPONENTS]
            base_material = "pcb_solder_mask"
        elif image_family == "aerospace_structural":
            base_type = "composite_panel"
            base_name = "Carbon-Fiber Composite Substrate"
            base_dims = {"width": 300, "height": 210}
            candidate_types = [t for t in AEROSPACE_COMPONENTS if t != "composite_panel"]
            base_material = "composite_weave"
        else:
            base_type = "mounting_plate" if rng.random() > 0.3 else "assembly_fixture"
            base_name = COMPONENT_NAMES.get(base_type, "Machined Mounting Plate")
            base_dims = dict(DEFAULT_DIMENSIONS[base_type])
            candidate_types = [t for t in MECHANICAL_COMPONENTS if t not in ("mounting_plate", "assembly_fixture")]
            base_material = "anodized_aluminum"

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
            "name": base_name,
            "center": {"x": float(base_cx), "y": float(base_cy)},
            "dimensions": base_dims,
            "bbox": [round(b, 1) for b in base_bbox],
            "rotation_deg": 0.0,
            "material": base_material,
            "expected_position": {"x": float(base_cx), "y": float(base_cy), "rotation_deg": 0.0},
            "is_defective": False,
            "defect_type": None,
            "occlusion_ratio": 0.0,
            "visibility_score": 1.0,
            "layer": 1
        })

        # 2. Place assembly components (Layer 2)
        selected_types = []
        for i in range(count - 1):
            selected_types.append(candidate_types[i % len(candidate_types)])
        rng.shuffle(selected_types)

        defective_indices = set(rng.sample(range(len(selected_types)), min(num_defects, len(selected_types))))

        # Define grid slots on and around the base fixture
        slots = []
        plate_w = base_dims["width"]
        plate_h = base_dims["height"]

        if image_family == "smart_retail_shelf":
            # Realistic 2-Tier Supermarket Shelf with 4 slots per tier
            top_y = base_cy - 85
            bot_y = base_cy + 85
            xs = [base_cx - 210, base_cx - 70, base_cx + 70, base_cx + 210]
            for x in xs:
                slots.append((x, top_y))
            for x in xs:
                slots.append((x, bot_y))
        else:
            slots.append((base_cx - plate_w * 0.28, base_cy - plate_h * 0.25))
            slots.append((base_cx + plate_w * 0.28, base_cy - plate_h * 0.25))
            slots.append((base_cx - plate_w * 0.28, base_cy + plate_h * 0.25))
            slots.append((base_cx + plate_w * 0.28, base_cy + plate_h * 0.25))
            slots.append((base_cx, base_cy))
            slots.append((base_cx - plate_w * 0.65, base_cy))
            slots.append((base_cx + plate_w * 0.65, base_cy))
            slots.append((base_cx, base_cy - plate_h * 0.70))
            slots.append((base_cx, base_cy + plate_h * 0.70))
            slots.append((base_cx - plate_w * 0.65, base_cy - plate_h * 0.55))
            slots.append((base_cx + plate_w * 0.65, base_cy + plate_h * 0.55))

        materials = ["machined_steel", "brass", "black_oxide", "anodized_aluminum", "copper"]
        retail_material_map = {
            "soda_can": "retail_cola",
            "milk_carton": "retail_milk",
            "cereal_box": "retail_cereal",
            "fresh_apple": "retail_apple",
            "water_bottle": "retail_water",
            "coffee_mug": "retail_mug",
            "snack_chips": "retail_chips",
            "chocolate_bar": "retail_chocolate",
            "juice_box": "retail_juice"
        }

        for idx, ctype in enumerate(selected_types):
            slot_x, slot_y = slots[idx % len(slots)]
            dims = dict(DEFAULT_DIMENSIONS.get(ctype, {"width": 50, "height": 40}))
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
                    pass
                elif chosen_defect == "misplaced":
                    offset_angle = rng.uniform(0, 2 * math.pi)
                    offset_dist = rng.uniform(35, 55)
                    actual_x += offset_dist * math.cos(offset_angle)
                    actual_y += offset_dist * math.sin(offset_angle)
                elif chosen_defect == "orientation":
                    actual_rot = float(rng.choice([90, 180, 270]))
                elif chosen_defect == "occlusion":
                    pass

            # Calculate Bounding Box
            if ctype in ("spur_gear", "hex_nut", "fastener", "electrolytic_cap", "countersunk_rivet"):
                r = dims.get("radius", 40)
                bbox = [actual_x - r, actual_y - r, actual_x + r, actual_y + r]
            elif ctype == "fresh_apple":
                r = dims.get("radius", 26)
                bbox = [actual_x - r, actual_y - r, actual_x + r, actual_y + r]
            elif ctype == "soda_can":
                w = dims.get("width", 48)
                h = dims.get("height", 66)
                bbox = [actual_x - w / 2, actual_y - h / 2, actual_x + w / 2, actual_y + h / 2]
            elif ctype in ("milk_carton", "cereal_box", "snack_chips", "juice_box", "water_bottle", "chocolate_bar", "coffee_mug"):
                w = dims.get("width", 56)
                h = dims.get("height", 75)
                bbox = [actual_x - w / 2, actual_y - h / 2, actual_x + w / 2, actual_y + h / 2]
            elif ctype in ("hex_bolt", "lockwire_fastener", "torque_seal_bolt"):
                r = dims.get("flange_radius", 24)
                bbox = [actual_x - r, actual_y - r, actual_x + r, actual_y + r]
            elif ctype == "pipe":
                l = dims.get("length", 160)
                d = dims.get("diameter", 28)
                bbox = [actual_x - l / 2, actual_y - d / 2, actual_x + l / 2, actual_y + d / 2]
            else:
                w = dims.get("width", 60)
                h = dims.get("height", 40)
                bbox = [actual_x - w / 2, actual_y - h / 2, actual_x + w / 2, actual_y + h / 2]

            bbox = [
                max(0.0, min(float(width), bbox[0])),
                max(0.0, min(float(height), bbox[1])),
                max(0.0, min(float(width), bbox[2])),
                max(0.0, min(float(height), bbox[3])),
            ]

            visibility = 0.0 if defect_type == "missing" else (0.65 if defect_type == "occlusion" else 1.0)
            occlusion_ratio = 1.0 if defect_type == "missing" else (0.35 if defect_type == "occlusion" else 0.0)

            if image_family == "smart_retail_shelf":
                comp_mat = retail_material_map.get(ctype, "retail_cola")
            else:
                comp_mat = rng.choice(materials)

            components.append({
                "id": comp_id,
                "type": ctype,
                "name": COMPONENT_NAMES.get(ctype, ctype.replace('_', ' ').title()),
                "center": {"x": round(actual_x, 1), "y": round(actual_y, 1)},
                "dimensions": dims,
                "bbox": [round(b, 1) for b in bbox],
                "rotation_deg": round(actual_rot, 1),
                "material": comp_mat,
                "expected_position": {"x": round(expected_x, 1), "y": round(expected_y, 1), "rotation_deg": expected_rot},
                "is_defective": is_defective,
                "defect_type": defect_type,
                "occlusion_ratio": occlusion_ratio,
                "visibility_score": visibility,
                "layer": 2
            })

        # 3. Add Occlusions
        occlusions = []
        has_occlusion_defect = any(c.get("defect_type") == "occlusion" for c in components)
        if difficulty == "hard" or has_occlusion_defect:
            occluded_comp = next((c for c in components if c.get("defect_type") == "occlusion"), None)
            if occluded_comp:
                ox = occluded_comp["center"]["x"]
                oy = occluded_comp["center"]["y"]
                wire_points = [(ox - 180, oy + 40), (ox, oy), (ox + 180, oy - 30)]
            else:
                wire_points = [(150, 420), (400, 390), (680, 410)]

            occ_type = "basket_handle" if image_family == "smart_retail_shelf" else "wire_harness"
            occlusions.append({
                "id": "occ_wire_1",
                "type": occ_type,
                "points": wire_points
            })

        # 4. Background Clutter
        clutter = []
        if difficulty in ("medium", "hard"):
            num_clutter = rng.randint(1, 3 if difficulty == "hard" else 2)
            if image_family == "smart_retail_shelf":
                clutter_types = ["price_tag_slip", "barcode_sticker", "receipt_slip"]
            else:
                clutter_types = ["washer", "hex_key", "metal_chip"]
            for c_i in range(num_clutter):
                clutter.append({
                    "id": f"clutter_{c_i}",
                    "type": rng.choice(clutter_types),
                    "x": rng.randint(60, width - 60),
                    "y": rng.randint(60, height - 60)
                })

        # 5. Spatial Relations
        spatial_relations = self._compute_spatial_relations(components)

        return {
            "scene_id": scene_id,
            "dataset_id": dataset_id,
            "image_family": image_family,
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
