from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from backend.app.modules.validation.rules import (
    validate_image_readable,
    validate_scene_graph_consistency,
    validate_bounding_boxes,
    validate_visual_evidence,
    validate_answer_determinism,
    validate_question_clarity,
)

class TaskValidator:
    """Automated multi-factor validation engine for synthetic benchmark tasks."""

    def __init__(self):
        self.seen_questions: set = set()

    def validate_task(
        self,
        question: Dict[str, Any],
        scene_graph: Dict[str, Any],
        image_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Validate a single visual reasoning task against all criteria.

        Returns validation result dictionary with status ('PASS' or 'FAIL'),
        score (0.0 to 1.0), individual check statuses, and rejection reason if applicable.
        """
        checks: Dict[str, Dict[str, Any]] = {}
        failures: List[str] = []

        # 1. Scene graph consistency
        sg_ok, sg_msg = validate_scene_graph_consistency(scene_graph)
        checks["scene_graph_consistency"] = {"passed": sg_ok, "message": sg_msg}
        if not sg_ok:
            failures.append(sg_msg)

        # 2. Bounding boxes validity
        dims = scene_graph.get("dimensions", {"width": 800, "height": 600})
        bb_ok, bb_msg = validate_bounding_boxes(scene_graph, dims.get("width", 800), dims.get("height", 600))
        checks["bounding_boxes_valid"] = {"passed": bb_ok, "message": bb_msg}
        if not bb_ok:
            failures.append(bb_msg)

        # 3. Question clarity
        qc_ok, qc_msg = validate_question_clarity(question)
        checks["question_clarity"] = {"passed": qc_ok, "message": qc_msg}
        if not qc_ok:
            failures.append(qc_msg)

        # 4. Answer determinism
        ad_ok, ad_msg = validate_answer_determinism(question)
        checks["answer_determinism"] = {"passed": ad_ok, "message": ad_msg}
        if not ad_ok:
            failures.append(ad_msg)

        # 5. Visual evidence sufficiency
        ve_ok, ve_msg = validate_visual_evidence(question, scene_graph)
        checks["visual_evidence_sufficiency"] = {"passed": ve_ok, "message": ve_msg}
        if not ve_ok:
            failures.append(ve_msg)

        # 6. Duplicate check
        q_text = question.get("question_text", "").strip().lower()
        scene_id = question.get("scene_id", "")
        dedup_key = f"{scene_id}::{q_text}"
        dup_ok = dedup_key not in self.seen_questions
        dup_msg = "Duplicate question detected for this scene" if not dup_ok else "Question is unique in scene"
        checks["no_duplicate"] = {"passed": dup_ok, "message": dup_msg}
        if not dup_ok:
            failures.append(dup_msg)
        else:
            self.seen_questions.add(dedup_key)

        # 7. Image file readability (if image_path provided)
        if image_path:
            img_ok, img_msg = validate_image_readable(image_path, dims.get("width", 800), dims.get("height", 600))
            checks["image_readable"] = {"passed": img_ok, "message": img_msg}
            if not img_ok:
                failures.append(img_msg)

        total_checks = len(checks)
        passed_checks = sum(1 for c in checks.values() if c["passed"])
        score = round(passed_checks / total_checks, 3) if total_checks > 0 else 0.0
        status = "PASS" if len(failures) == 0 else "FAIL"

        return {
            "question_id": question.get("id"),
            "scene_id": scene_id,
            "status": status,
            "score": score,
            "checks": checks,
            "rejection_reason": "; ".join(failures) if failures else None,
            "validated_at": datetime.now(timezone.utc).isoformat()
        }

    def reset_dedup(self):
        """Reset seen questions set for a new dataset run."""
        self.seen_questions.clear()
