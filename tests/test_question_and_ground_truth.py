import pytest
from backend.app.modules.synthetic.generator import SceneGenerator
from backend.app.modules.questions.question_engine import QuestionEngine
from backend.app.modules.ground_truth.gt_engine import GroundTruthEngine

def test_question_generation_categories():
    gen = SceneGenerator(seed=12)
    sg = gen.generate_scene(seed=12)

    qe = QuestionEngine(seed=12)
    questions = qe.generate_questions_for_scene(sg, max_questions=5)

    assert len(questions) > 0
    for q in questions:
        assert "id" in q
        assert "question_text" in q
        assert len(q["question_text"]) > 15
        assert "expected_answer" in q
        assert q["expected_answer"] != ""
        assert q["expected_answer"] != "unknown"
        assert q["answer_type"] in ("integer", "boolean", "category", "text")

def test_deterministic_ground_truth_counting():
    """Verify ground-truth counting is exact and deterministic."""
    gen = SceneGenerator(seed=34)
    sg = gen.generate_scene(component_count=6, seed=34)

    fasteners = [
        c for c in sg["components"]
        if c["type"] in ("hex_bolt", "hex_nut", "fastener") and c.get("visibility_score", 1.0) > 0.3
    ]
    expected_count = str(len(fasteners))

    ans, atype, ids = GroundTruthEngine.calculate_answer("count_fasteners", sg, {})
    assert ans == expected_count
    assert atype == "integer"
    assert len(ids) == len(fasteners)

def test_spatial_relationship_ground_truth():
    """Verify spatial calculation between two explicit coordinates."""
    sg = {
        "components": [
            {"id": "comp_a", "name": "Gear A", "center": {"x": 100, "y": 200}, "layer": 2},
            {"id": "comp_b", "name": "Bolt B", "center": {"x": 300, "y": 200}, "layer": 2}
        ]
    }
    ans, atype, ids = GroundTruthEngine.calculate_answer(
        "get_horizontal_relation", sg, {"subject_id": "comp_a", "object_id": "comp_b"}
    )
    assert ans == "left"
    assert atype == "category"
