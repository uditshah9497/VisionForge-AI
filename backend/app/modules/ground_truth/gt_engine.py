import math
from typing import Dict, Any, List, Optional, Tuple

class GroundTruthEngine:
    """Pure deterministic ground-truth engine that computes verifiable reference answers

    from scene graph metadata independently of any evaluated AI model.
    """

    @staticmethod
    def calculate_answer(rule: str, scene_graph: Dict[str, Any], params: Dict[str, Any]) -> Tuple[str, str, List[str]]:
        """Calculate ground-truth reference answer based on functional derivation rule.

        Returns: (answer_string, answer_type, supporting_component_ids)
        """
        components = scene_graph.get("components", [])

        if rule == "find_component_at_coord":
            tx = params["x"]
            ty = params["y"]
            closest = None
            min_dist = float("inf")
            for comp in components:
                cx, cy = comp["center"]["x"], comp["center"]["y"]
                d = math.hypot(cx - tx, cy - ty)
                if d < min_dist:
                    min_dist = d
                    closest = comp
            if closest and min_dist < 80:
                return closest["name"], "category", [closest["id"]]
            return "none", "category", []

        elif rule == "check_component_presence":
            target_type = params["component_type"]
            visible = [c for c in components if c["type"] == target_type and c.get("visibility_score", 1.0) > 0.3]
            ans = "yes" if len(visible) > 0 else "no"
            return ans, "boolean", [c["id"] for c in visible]

        elif rule == "get_component_material":
            comp_id = params["component_id"]
            comp = next((c for c in components if c["id"] == comp_id), None)
            if comp:
                mat = comp.get("material", "machined_steel").replace("_", " ")
                return mat, "category", [comp_id]
            return "unknown", "category", []

        elif rule == "count_visible_by_type":
            target_type = params["component_type"]
            matches = [c for c in components if c["type"] == target_type and c.get("visibility_score", 1.0) > 0.3]
            return str(len(matches)), "integer", [c["id"] for c in matches]

        elif rule == "count_fasteners":
            fasteners = [
                c for c in components
                if c["type"] in ("hex_bolt", "hex_nut", "fastener", "countersunk_rivet", "lockwire_fastener", "torque_seal_bolt") and c.get("visibility_score", 1.0) > 0.3
            ]
            return str(len(fasteners)), "integer", [c["id"] for c in fasteners]

        elif rule == "count_defective":
            defective = [c for c in components if c.get("is_defective", False)]
            return str(len(defective)), "integer", [c["id"] for c in defective]

        elif rule == "get_horizontal_relation":
            sub_id = params["subject_id"]
            obj_id = params["object_id"]
            sub = next((c for c in components if c["id"] == sub_id), None)
            obj = next((c for c in components if c["id"] == obj_id), None)
            if sub and obj:
                rel = "left" if sub["center"]["x"] < obj["center"]["x"] else "right"
                return rel, "category", [sub_id, obj_id]
            return "unknown", "category", []

        elif rule == "get_vertical_relation":
            sub_id = params["subject_id"]
            obj_id = params["object_id"]
            sub = next((c for c in components if c["id"] == sub_id), None)
            obj = next((c for c in components if c["id"] == obj_id), None)
            if sub and obj:
                rel = "above" if sub["center"]["y"] < obj["center"]["y"] else "below"
                return rel, "category", [sub_id, obj_id]
            return "unknown", "category", []

        elif rule == "get_closest_to_base":
            base = next((c for c in components if c["layer"] == 1), None)
            if not base:
                return "none", "category", []
            bx, by = base["center"]["x"], base["center"]["y"]
            candidates = [c for c in components if c["layer"] > 1 and c.get("visibility_score", 1.0) > 0.3]
            if not candidates:
                return "none", "category", []
            closest = min(candidates, key=lambda c: math.hypot(c["center"]["x"] - bx, c["center"]["y"] - by))
            return closest["name"], "category", [closest["id"]]

        elif rule == "check_missing_socket":
            missing = [c for c in components if c.get("defect_type") == "missing"]
            ans = "yes" if len(missing) > 0 else "no"
            return ans, "boolean", [c["id"] for c in missing]

        elif rule == "identify_defective_component":
            defective = [c for c in components if c.get("is_defective", False)]
            if defective:
                return defective[0]["name"], "category", [defective[0]["id"]]
            return "none", "category", []

        elif rule == "check_component_misalignment":
            comp_id = params["component_id"]
            comp = next((c for c in components if c["id"] == comp_id), None)
            if comp:
                # Properly positioned = NOT defective
                ans = "no" if comp.get("is_defective", False) else "yes"
                return ans, "boolean", [comp_id]
            return "no", "boolean", []

        elif rule == "check_mounted_on_base":
            comp_id = params["component_id"]
            base = next((c for c in components if c["layer"] == 1), None)
            comp = next((c for c in components if c["id"] == comp_id), None)
            if comp and base:
                cx, cy = comp["center"]["x"], comp["center"]["y"]
                bb = base["bbox"]
                inside = (bb[0] <= cx <= bb[2]) and (bb[1] <= cy <= bb[3])
                return "yes" if inside else "no", "boolean", [comp_id, base["id"]]
            return "no", "boolean", []

        elif rule == "get_primary_spatial_relation":
            sub_id = params["subject_id"]
            obj_id = params["object_id"]
            sub = next((c for c in components if c["id"] == sub_id), None)
            obj = next((c for c in components if c["id"] == obj_id), None)
            if sub and obj:
                dx = sub["center"]["x"] - obj["center"]["x"]
                dy = sub["center"]["y"] - obj["center"]["y"]
                if abs(dx) > abs(dy):
                    rel = "left_of" if dx < 0 else "right_of"
                else:
                    rel = "above" if dy < 0 else "below"
                return rel, "category", [sub_id, obj_id]
            return "adjacent_to", "category", []

        return "unknown", "text", []
