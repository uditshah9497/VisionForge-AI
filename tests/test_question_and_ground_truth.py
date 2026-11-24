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
    """Verify ground-truth counting is exact and deterministic for both retail and mechanical."""
    gen = SceneGenerator(seed=34)

    # 1. Retail Shelf Beverage Counting
    sg_retail = gen.generate_scene(image_family="smart_retail_shelf", component_count=6, seed=34)
    beverages = [
        c for c in sg_retail["components"]
        if c["type"] in ("soda_can", "water_bottle", "juice_box", "coffee_mug") and c.get("visibility_score", 1.0) > 0.3
    ]
    ans_ret, atype_ret, ids_ret = GroundTruthEngine.calculate_answer("count_fasteners", sg_retail, {})
    assert ans_ret == str(len(beverages))
    assert atype_ret == "integer"
    assert len(ids_ret) == len(beverages)

    # 2. Industrial Workstation Fastener Counting
    sg_mech = gen.generate_scene(image_family="mechanical_assembly", component_count=6, seed=34)
    fasteners = [
        c for c in sg_mech["components"]
        if c["type"] in ("hex_bolt", "hex_nut", "fastener") and c.get("visibility_score", 1.0) > 0.3
    ]
    ans_mech, atype_mech, ids_mech = GroundTruthEngine.calculate_answer("count_fasteners", sg_mech, {})
    assert ans_mech == str(len(fasteners))
    assert atype_mech == "integer"
    assert len(ids_mech) == len(fasteners)

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
