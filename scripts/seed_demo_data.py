import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from backend.app.core.database import SessionLocal
from backend.app.api.routes import generate_dataset, run_evaluation, generate_blind_spot
from backend.app.models.schemas import DatasetCreateRequest, EvaluationRunRequest, BlindSpotGenerateRequest

def seed():
    db = SessionLocal()
    print("=" * 60)
    print("Seeding VisionForge AI High-Fidelity Benchmarks across 3 Image Families...")
    print("=" * 60)

    # 1. Smart Retail & Supermarket Shelf Inspection Benchmark (Flagship - Universally Understandable)
    print("\n[1/3] Synthesizing Flagship Smart Retail Supermarket Shelf Benchmark (Universal)...")
    req_retail = DatasetCreateRequest(
        name="Smart Retail Supermarket Shelf Inspection Benchmark",
        description="Universally recognizable everyday consumer goods: soda cans, milk cartons, cereal boxes, fresh apples, water bottles, and mugs on supermarket display shelves with automated out-of-stock and misalignment detection.",
        domain="Smart Retail & Supermarket Shelf Inspection",
        image_family="smart_retail_shelf",
        image_count=5,
        components_per_scene=6,
        difficulty="medium",
        defect_types=["missing", "misplaced", "orientation", "occlusion"],
        lighting="standard_5000k",
        seed=101
    )
    res_retail = generate_dataset(req_retail, db)
    print(f"Generated Smart Retail Dataset: {res_retail['id']}")

    eval_retail = run_evaluation(EvaluationRunRequest(
        dataset_id=res_retail["id"],
        model_name="visionforge-demo-v1",
        provider="demo"
    ), db)
    print(f"Retail Eval Acc: {eval_retail['overall_accuracy']*100:.1f}%, Latency: {eval_retail['avg_latency_ms']}ms")

    # 2. Industrial Mechanical Assembly Benchmark
    print("\n[2/3] Synthesizing Industrial Mechanical Assembly Benchmark...")
    req_mech = DatasetCreateRequest(
        name="Precision Mechanical Workstation Benchmark",
        description="High-fidelity machined mechanical components: gears, hex flange bolts, locking nuts, and hydraulic lines with 3D drop shadows and optical breadboard textures.",
        domain="Manufacturing Quality Inspection",
        image_family="mechanical_assembly",
        image_count=5,
        components_per_scene=6,
        difficulty="medium",
        defect_types=["missing", "misplaced", "orientation", "occlusion"],
        lighting="standard_5000k",
        seed=202
    )
    res_mech = generate_dataset(req_mech, db)
    print(f"Generated Mechanical Dataset: {res_mech['id']}")

    eval_mech = run_evaluation(EvaluationRunRequest(
        dataset_id=res_mech["id"],
        model_name="visionforge-demo-v1",
        provider="demo"
    ), db)
    print(f"Mechanical Eval Acc: {eval_mech['overall_accuracy']*100:.1f}%, Latency: {eval_mech['avg_latency_ms']}ms")

    # 3. SMT PCB Micro-Electronics Benchmark
    print("\n[3/3] Synthesizing SMT PCB Micro-Electronics Benchmark...")
    req_pcb = DatasetCreateRequest(
        name="High-Density SMT PCB Micro-Electronics Benchmark",
        description="Surface-mount electronics on FR4 green solder mask with copper traces, QFP microcontrollers, SMD 0805 passives, diodes, and solder fillet joints.",
        domain="Electronics Surface Mount Quality Inspection",
        image_family="pcb_electronics",
        image_count=5,
        components_per_scene=7,
        difficulty="medium",
        defect_types=["missing", "misplaced", "orientation", "occlusion"],
        lighting="standard_5000k",
        seed=303
    )
    res_pcb = generate_dataset(req_pcb, db)
    print(f"Generated PCB Dataset: {res_pcb['id']}")

    eval_pcb = run_evaluation(EvaluationRunRequest(
        dataset_id=res_pcb["id"],
        model_name="visionforge-demo-v1",
        provider="demo"
    ), db)
    print(f"PCB Eval Acc: {eval_pcb['overall_accuracy']*100:.1f}%, Latency: {eval_pcb['avg_latency_ms']}ms")

    # 4. Generate Blind Spot Discovery Pairs
    print("\nGenerating Adversarial Blind Spot discovery pairs...")
    for pert in ["component_removed", "orientation_inversion", "misplaced", "lighting_change"]:
        bs = generate_blind_spot(BlindSpotGenerateRequest(
            base_seed=101,
            perturbation_type=pert,
            provider="demo",
            model_name="visionforge-demo-v1"
        ), db)
        print(f"Adversarial Pair [{pert}]: ID={bs['id']}, IsBlindSpot={bs['is_blind_spot']}")

    db.close()
    print("\n" + "=" * 60)
    print("Multi-Family High-Fidelity Seeding completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    seed()
