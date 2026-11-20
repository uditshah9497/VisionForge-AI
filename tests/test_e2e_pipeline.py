import os
import pytest
from backend.app.modules.synthetic.generator import SceneGenerator
from backend.app.modules.synthetic.renderer import SyntheticRenderer
from backend.app.modules.questions.question_engine import QuestionEngine
from backend.app.modules.ground_truth.gt_engine import GroundTruthEngine
from backend.app.modules.validation.task_validator import TaskValidator
from backend.app.modules.evaluation.eval_engine import EvaluationEngine

def test_complete_end_to_end_benchmark_pipeline(tmp_path):
    """End-to-End Pipeline Test:

    1. Generates synthetic scene.
    2. Renders image.
    3. Generates questions.
    4. Calculates ground-truth reference answers.
    5. Validates tasks (checks pass/fail gating).
    6. Executes multimodal evaluation.
    7. Verifies benchmark metrics.
    """
    seed = 999
    # 1. Generate Scene
    generator = SceneGenerator(seed=seed)
    sg = generator.generate_scene(
        scene_id="sc_e2e_01",
        difficulty="medium",
        component_count=5,
        defect_types=["missing", "misplaced"],
        seed=seed
    )
    assert sg["scene_id"] == "sc_e2e_01"
    assert len(sg["components"]) >= 5

    # 2. Render Image
    renderer = SyntheticRenderer(width=800, height=600)
    img_path = str(tmp_path / "e2e_scene.png")
    render_res = renderer.render_scene(sg, img_path)
    assert os.path.exists(img_path)
    assert render_res["file_size_bytes"] > 1000

    # 3. Generate Questions
    qe = QuestionEngine(seed=seed)
    questions = qe.generate_questions_for_scene(sg, max_questions=3, seed=seed)
    assert len(questions) > 0

    # 4. Verify Ground Truth Answers are Deterministic and Valid
    for q in questions:
        assert q["expected_answer"] != ""
        assert q["derivation_rule"] is not None

    # 5. Validate Tasks
    validator = TaskValidator()
    validated_tasks = []
    for q in questions:
        val_res = validator.validate_task(q, sg, image_path=img_path)
        assert val_res["score"] >= 0.8
        if val_res["status"] == "PASS":
            validated_tasks.append({
                "question_id": q["id"],
                "category": q["category"],
                "difficulty": q["difficulty"],
                "question_text": q["question_text"],
                "expected_answer": q["expected_answer"],
                "answer_type": q["answer_type"],
                "image_path": img_path
            })

    assert len(validated_tasks) > 0

    # 6. Evaluate Multimodal Model (using calibrated Demo simulator)
    bench_result = EvaluationEngine.run_benchmark(
        tasks=validated_tasks,
        provider="demo",
        model_name="visionforge-demo-v1"
    )

    # 7. Check Benchmark Metrics
    assert bench_result["status"] == "completed"
    assert bench_result["total_tasks"] == len(validated_tasks)
    assert 0.0 <= bench_result["overall_accuracy"] <= 1.0
    assert bench_result["avg_latency_ms"] > 0
    assert "metrics" in bench_result
