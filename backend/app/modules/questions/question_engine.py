import random
import uuid
from typing import Dict, Any, List, Optional
from backend.app.modules.questions.templates import QUESTION_TEMPLATES
from backend.app.modules.ground_truth.gt_engine import GroundTruthEngine

class QuestionEngine:
    """Generates verifiable visual reasoning questions and computes deterministic

    reference answers from scene graph metadata.
    """

    def __init__(self, seed: Optional[int] = None):
        self.seed = seed if seed is not None else 42

    def generate_questions_for_scene(
        self,
        scene_graph: Dict[str, Any],
        max_questions: int = 5,
        target_categories: Optional[List[str]] = None,
        seed: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Generate a balanced set of verified visual questions for a synthetic scene."""
        effective_seed = seed if seed is not None else scene_graph.get("seed", self.seed)
        rng = random.Random(effective_seed)

        categories = target_categories or list(QUESTION_TEMPLATES.keys())
        rng.shuffle(categories)

        questions = []
        components = scene_graph.get("components", [])
        base_comp = next((c for c in components if c["layer"] == 1), None)
        layer2_comps = [c for c in components if c["layer"] > 1]

        if not layer2_comps:
            return []

        for cat in categories:
            if len(questions) >= max_questions:
                break

            templates = QUESTION_TEMPLATES.get(cat, [])
            if not templates:
                continue

            tmpl = rng.choice(templates)
            q_obj = self._instantiate_template(tmpl, cat, scene_graph, base_comp, layer2_comps, rng)
            if q_obj:
                questions.append(q_obj)

        return questions

    def _instantiate_template(
        self,
        tmpl: Dict[str, Any],
        category: str,
        scene_graph: Dict[str, Any],
        base_comp: Optional[Dict[str, Any]],
        layer2_comps: List[Dict[str, Any]],
        rng: random.Random
    ) -> Optional[Dict[str, Any]]:
        rule = tmpl["rule"]
        qid = f"q_{uuid.UUID(int=rng.getrandbits(128)).hex[:8]}"
        params = {}
        format_args = {}

        if rule == "find_component_at_coord":
            target = rng.choice(layer2_comps)
            # Add slight jitter to coordinate so question doesn't give away exact center
            params["x"] = round(target["center"]["x"] + rng.uniform(-5, 5), 1)
            params["y"] = round(target["center"]["y"] + rng.uniform(-5, 5), 1)
            format_args["x"] = int(params["x"])
            format_args["y"] = int(params["y"])

        elif rule == "check_component_presence":
            target = rng.choice(layer2_comps)
            params["component_type"] = target["type"]
            format_args["component_name"] = target["name"]

        elif rule == "get_component_material":
            target = rng.choice(layer2_comps)
            params["component_id"] = target["id"]
            format_args["component_name"] = target["name"]
            format_args["x"] = int(target["center"]["x"])
            format_args["y"] = int(target["center"]["y"])

        elif rule == "count_visible_by_type":
            target = rng.choice(layer2_comps)
            params["component_type"] = target["type"]
            format_args["component_name"] = target["name"]

        elif rule in ("count_fasteners", "count_defective", "check_missing_socket", "identify_defective_component"):
            pass  # Global scene rules without specific target args

        elif rule in ("get_horizontal_relation", "get_vertical_relation", "get_primary_spatial_relation"):
            if len(layer2_comps) < 2:
                return None
            sampled = rng.sample(layer2_comps, 2)
            sub, obj = sampled[0], sampled[1]
            params["subject_id"] = sub["id"]
            params["object_id"] = obj["id"]
            format_args["subject_name"] = sub["name"]
            format_args["object_name"] = obj["name"]
            format_args["ox"] = int(obj["center"]["x"])
            format_args["oy"] = int(obj["center"]["y"])

        elif rule == "get_closest_to_base":
            if not base_comp:
                return None
            format_args["base_name"] = base_comp["name"]

        elif rule == "check_component_misalignment":
            target = rng.choice(layer2_comps)
            params["component_id"] = target["id"]
            format_args["component_name"] = target["name"]
            format_args["x"] = int(target["center"]["x"])
            format_args["y"] = int(target["center"]["y"])

        elif rule == "check_mounted_on_base":
            if not base_comp:
                return None
            target = rng.choice(layer2_comps)
            params["component_id"] = target["id"]
            format_args["component_name"] = target["name"]
            format_args["base_name"] = base_comp["name"]
            format_args["x"] = int(target["center"]["x"])
            format_args["y"] = int(target["center"]["y"])

        # Calculate authoritative reference ground truth
        ans_str, ans_type, supporting_ids = GroundTruthEngine.calculate_answer(rule, scene_graph, params)

        try:
            q_text = tmpl["template"].format(**format_args)
        except KeyError:
            return None

        return {
            "id": qid,
            "scene_id": scene_graph.get("scene_id", ""),
            "category": category,
            "difficulty": tmpl["difficulty"],
            "question_text": q_text,
            "expected_answer": ans_str,
            "answer_type": ans_type,
            "supporting_component_ids": supporting_ids,
            "derivation_rule": f"{rule}({params})",
            "validation_status": "PENDING"
        }
