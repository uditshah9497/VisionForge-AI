import pytest
from backend.app.modules.synthetic.generator import SceneGenerator
from backend.app.modules.synthetic.renderer import SyntheticRenderer
from backend.app.modules.questions.question_engine import QuestionEngine
from backend.app.modules.validation.task_validator import TaskValidator

def test_valid_task_passes_validation(tmp_path):
    gen = SceneGenerator(seed=42)
    sg = gen.generate_scene(seed=42)
    renderer = SyntheticRenderer()
    img_path = str(tmp_path / "valid_task.png")
    renderer.render_scene(sg, img_path)

    qe = QuestionEngine(seed=42)
    questions = qe.generate_questions_for_scene(sg, max_questions=2)
    assert len(questions) > 0

    validator = TaskValidator()
    val_res = validator.validate_task(questions[0], sg, image_path=img_path)

    assert val_res["status"] == "PASS"
    assert val_res["score"] == 1.0
    assert val_res["rejection_reason"] is None

def test_incorrect_ground_truth_fails_validation():
    """CRITICAL: Tasks with invalid or corrupt expected answer must FAIL validation."""
    gen = SceneGenerator(seed=42)
    sg = gen.generate_scene(seed=42)
    validator = TaskValidator()

    # Question with corrupt answer for an integer type
    corrupt_q = {
        "id": "q_corrupt_1",
        "scene_id": sg["scene_id"],
        "category": "counting",
        "difficulty": "medium",
        "question_text": "How many hex bolts are on the table?",
        "expected_answer": "NOT_AN_INTEGER",
        "answer_type": "integer",
        "supporting_component_ids": []
    }
    res = validator.validate_task(corrupt_q, sg)
    assert res["status"] == "FAIL"
    assert "does not parse as integer" in res["rejection_reason"]

def test_ambiguous_question_rejected():
    """CRITICAL: Ambiguous or unpopulated template questions must be REJECTED."""
    gen = SceneGenerator(seed=42)
    sg = gen.generate_scene(seed=42)
    validator = TaskValidator()

    # Question with unpopulated {placeholder}
    ambiguous_q = {
        "id": "q_ambig_1",
        "scene_id": sg["scene_id"],
        "category": "identification",
        "difficulty": "easy",
        "question_text": "What component is located at {unknown_var}?",
        "expected_answer": "Spur Gear",
        "answer_type": "category",
        "supporting_component_ids": []
    }
    res = validator.validate_task(ambiguous_q, sg)
    assert res["status"] == "FAIL"
    assert "unpopulated template variable" in res["rejection_reason"]

def test_visually_unsupported_question_rejected():
    """CRITICAL: Questions relying on occluded/invisible components (< 0.25 visibility) must be REJECTED."""
    sg = {
        "scene_id": "sc_test",
        "dimensions": {"width": 800, "height": 600},
        "components": [
            {
                "id": "comp_base",
                "type": "mounting_plate",
                "name": "Base Plate",
                "center": {"x": 400, "y": 300},
                "bbox": [200, 200, 600, 400],
                "layer": 1
            },
            {
                "id": "comp_hidden",
                "type": "hex_bolt",
                "name": "Hidden Bolt",
                "center": {"x": 400, "y": 300},
                "bbox": [390, 290, 410, 310],
                "layer": 2,
                "visibility_score": 0.10,  # 90% occluded!
                "defect_type": "occlusion"
            }
        ]
    }
    validator = TaskValidator()
    q = {
        "id": "q_occluded_1",
        "scene_id": "sc_test",
        "category": "identification",
        "difficulty": "hard",
        "question_text": "What is the finish of the hidden bolt at (400, 300)?",
        "expected_answer": "machined steel",
        "answer_type": "category",
        "supporting_component_ids": ["comp_hidden"]
    }
    res = validator.validate_task(q, sg)
    assert res["status"] == "FAIL"
    assert "insufficient visibility" in res["rejection_reason"]

def test_duplicate_question_rejected():
    """CRITICAL: Duplicate questions targeting the same scene must be rejected."""
    gen = SceneGenerator(seed=42)
    sg = gen.generate_scene(seed=42)
    validator = TaskValidator()

    q = {
        "id": "q_dup_1",
        "scene_id": sg["scene_id"],
        "category": "counting",
        "difficulty": "easy",
        "question_text": "How many total fasteners are visible on the workstation?",
        "expected_answer": "3",
        "answer_type": "integer",
        "supporting_component_ids": []
    }
    # First validation passes
    res1 = validator.validate_task(q, sg)
    assert res1["status"] == "PASS"

    # Second validation of identical question for same scene fails
    res2 = validator.validate_task(q, sg)
    assert res2["status"] == "FAIL"
    assert "Duplicate question detected" in res2["rejection_reason"]
