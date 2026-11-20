import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from backend.app.core.database import SessionLocal
from backend.app.api.routes import generate_dataset, run_evaluation, generate_blind_spot
from backend.app.models.schemas import DatasetCreateRequest, EvaluationRunRequest, BlindSpotGenerateRequest

def seed():
    db = SessionLocal()
    print("Seeding initial VisionForge AI benchmark dataset...")
    req = DatasetCreateRequest(
        name="Precision Industrial Assembly Benchmark v1",
        description="Core manufacturing benchmark evaluating mechanical components, assembly defects, spatial alignments, and occlusion robustness.",
        domain="Manufacturing Quality Inspection",
        image_count=6,
        components_per_scene=6,
        difficulty="medium",
        defect_types=["missing", "misplaced", "orientation", "occlusion"],
        lighting="standard_5000k",
        seed=42
    )
    dataset_res = generate_dataset(req, db)
    print(f"Generated Dataset: {dataset_res['id']}")

    print("Running initial benchmark evaluation with Calibrated Simulator...")
    eval_req = EvaluationRunRequest(
        dataset_id=dataset_res["id"],
        model_name="visionforge-demo-v1",
        provider="demo"
    )
    eval_res = run_evaluation(eval_req, db)
    print(f"Evaluation Run complete: Acc={eval_res['overall_accuracy']*100:.1f}%, Latency={eval_res['avg_latency_ms']}ms")

    print("Generating initial Adversarial Blind Spot discovery pair...")
    bs_req = BlindSpotGenerateRequest(
        base_seed=42,
        perturbation_type="component_removed",
        provider="demo",
        model_name="visionforge-demo-v1"
    )
    bs_res = generate_blind_spot(bs_req, db)
    print(f"Blind Spot Pair generated: ID={bs_res['id']}, IsBlindSpot={bs_res['is_blind_spot']}")

    db.close()
    print("Seeding complete successfully!")

if __name__ == "__main__":
    seed()
