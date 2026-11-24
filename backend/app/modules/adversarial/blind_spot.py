import copy
import uuid
from typing import Dict, Any, Optional
from backend.app.modules.synthetic.generator import SceneGenerator
from backend.app.modules.synthetic.renderer import SyntheticRenderer
from backend.app.modules.evaluation.eval_engine import get_adapter_for_model
from backend.app.modules.evaluation.normalizer import normalize_model_response
from backend.app.core.config import ARTIFACTS_DIR

class BlindSpotEngine:
    """Generates controlled adversarial image pairs with single-variable perturbations

    to discover frontier multimodal visual blind spots.
    """

    def __init__(self):
        self.generator = SceneGenerator()
        self.renderer = SyntheticRenderer()

    def generate_blind_spot_test(
        self,
        base_seed: int = 42,
        perturbation_type: str = "component_removed",
        provider: str = "demo",
        model_name: str = "visionforge-demo-v1"
    ) -> Dict[str, Any]:
        """Generate adversarial pair, evaluate model on both, and analyze discrepancies."""
        pair_id = f"bsp_{uuid.uuid4().hex[:8]}"
        scene_gen = SceneGenerator(seed=base_seed)

        # 1. Generate Base Scene A (Defect-free baseline)
        scene_a = scene_gen.generate_scene(
            scene_id=f"sc_base_{pair_id}",
            difficulty="medium",
            component_count=5,
            defect_types=[],  # Clean baseline
            lighting="standard_5000k",
            seed=base_seed
        )

        # 2. Clone Scene A and inject exactly ONE controlled perturbation for Scene B
        scene_b = copy.deepcopy(scene_a)
        scene_b["scene_id"] = f"sc_mod_{pair_id}"

        components_b = scene_b.get("components", [])
        layer2_b = [c for c in components_b if c["layer"] > 1]
        target_comp = layer2_b[0] if layer2_b else None

        delta_desc = ""
        question_text = ""
        ans_a = ""
        ans_b = ""
        ans_type = "text"
        target_type = target_comp["type"] if target_comp else "component"

        if perturbation_type == "component_removed" and target_comp:
            # Change target to missing socket / empty slot
            target_comp["defect_type"] = "missing"
            target_comp["is_defective"] = True
            target_comp["visibility_score"] = 0.0
            delta_desc = f"Removed {target_comp['name']} from shelf, leaving empty out-of-stock slot."
            question_text = f"Is there any missing item or out-of-stock empty slot visible on the display?"
            ans_a = "no"
            ans_b = "yes"
            ans_type = "boolean"

        elif perturbation_type == "misplaced" and target_comp:
            target_comp["center"]["x"] += 45
            target_comp["center"]["y"] += 35
            target_comp["bbox"] = [
                target_comp["bbox"][0] + 45,
                target_comp["bbox"][1] + 35,
                target_comp["bbox"][2] + 45,
                target_comp["bbox"][3] + 35
            ]
            target_comp["is_defective"] = True
            target_comp["defect_type"] = "misplaced"
            delta_desc = f"Shifted {target_comp['name']} by 45px outside designated display position."
            question_text = f"Is the {target_comp['name']} properly aligned without spatial displacement?"
            ans_a = "yes"
            ans_b = "no"
            ans_type = "boolean"

        elif perturbation_type == "orientation_inversion" and target_comp:
            target_comp["rotation_deg"] = 180.0
            target_comp["is_defective"] = True
            target_comp["defect_type"] = "orientation"
            delta_desc = f"Inverted {target_comp['name']} by 180 degrees (upside down)."
            question_text = f"Is the {target_comp['name']} mounted in upright normal orientation (not inverted)?"
            ans_a = "yes"
            ans_b = "no"
            ans_type = "boolean"

        elif perturbation_type == "lighting_change":
            scene_b["workstation"]["lighting"]["ambient"] = 0.35
            scene_b["workstation"]["lighting"]["lighting_profile"] = "low_light"
            delta_desc = "Reduced ambient display illuminance from 82% to 35% (dim lighting testing)."
            target_name = target_comp["name"] if target_comp else "items"
            question_text = f"Is the {target_name} clearly visible on the display?"
            ans_a = "yes"
            ans_b = "yes"
            ans_type = "boolean"

        elif perturbation_type == "occlusion" and target_comp:
            cx, cy = target_comp["center"]["x"], target_comp["center"]["y"]
            occ_type = "basket_handle" if scene_a.get("image_family") == "smart_retail_shelf" else "wire_harness"
            scene_b["occlusions"] = [{
                "id": f"occ_{pair_id}",
                "type": occ_type,
                "points": [(cx - 150, cy + 30), (cx, cy), (cx + 150, cy - 20)]
            }]
            target_comp["visibility_score"] = 0.60
            delta_desc = f"Introduced foreground occlusion obscuring 40% of {target_comp['name']}."
            question_text = f"Is the {target_comp['name']} completely unobstructed with zero occlusion?"
            ans_a = "yes"
            ans_b = "no"
            ans_type = "boolean"

        # 3. Render both images to disk
        img_a_path = str(ARTIFACTS_DIR / f"pair_{pair_id}_orig.png")
        img_b_path = str(ARTIFACTS_DIR / f"pair_{pair_id}_mod.png")

        self.renderer.render_scene(scene_a, img_a_path)
        self.renderer.render_scene(scene_b, img_b_path)

        # 4. Evaluate chosen model adapter on both images
        adapter = get_adapter_for_model(provider, model_name)

        try:
            res_a = adapter.evaluate(img_a_path, question_text, context={"expected_answer": ans_a, "category": "anomaly_detection"})
            raw_a = res_a["raw_response"]
        except Exception as e:
            raw_a = f"Error: {str(e)}"

        try:
            res_b = adapter.evaluate(img_b_path, question_text, context={"expected_answer": ans_b, "category": "anomaly_detection"})
            raw_b = res_b["raw_response"]
        except Exception as e:
            raw_b = f"Error: {str(e)}"

        norm_a, ok_a, fail_a = normalize_model_response(raw_a, ans_a, ans_type)
        norm_b, ok_b, fail_b = normalize_model_response(raw_b, ans_b, ans_type)

        # Detect Blind Spot:
        # A blind spot occurs if the model failed to detect the controlled change in B
        # or gave the identical answer for B as A when ground truths differed!
        is_blind_spot = False
        failure_category = "none"

        if (ans_a != ans_b) and (norm_a == norm_b):
            is_blind_spot = True
            failure_category = "invariance_hallucination"
        elif not ok_b:
            is_blind_spot = True
            failure_category = f"blind_spot_{perturbation_type}"

        return {
            "id": pair_id,
            "property_changed": perturbation_type,
            "delta_description": delta_desc,
            "target_component_type": target_type,
            "question_text": question_text,
            "original_image_path": img_a_path,
            "modified_image_path": img_b_path,
            "original_image_url": f"/data/artifacts/pair_{pair_id}_orig.png",
            "modified_image_url": f"/data/artifacts/pair_{pair_id}_mod.png",
            "original_expected_answer": ans_a,
            "modified_expected_answer": ans_b,
            "model_name": adapter.model_name,
            "original_model_answer": norm_a,
            "modified_model_answer": norm_b,
            "original_raw_response": raw_a,
            "modified_raw_response": raw_b,
            "is_blind_spot": is_blind_spot,
            "failure_category": failure_category
        }
