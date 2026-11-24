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

    # 1. Industrial Mechanical Assembly Benchmark
    print("\n[1/3] Synthesizing Industrial Mechanical Assembly Benchmark...")
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
        seed=101
    )
    res_mech = generate_dataset(req_mech, db)
    print(f"Generated Mechanical Dataset: {res_mech['id']}")

    eval_mech = run_evaluation(EvaluationRunRequest(
        dataset_id=res_mech["id"],
        model_name="visionforge-demo-v1",
        provider="demo"
    ), db)
    print(f"Mechanical Eval Acc: {eval_mech['overall_accuracy']*100:.1f}%, Latency: {eval_mech['avg_latency_ms']}ms")

    # 2. SMT PCB Micro-Electronics Benchmark
    print("\n[2/3] Synthesizing SMT PCB Micro-Electronics Benchmark...")
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
        seed=202
    )
    res_pcb = generate_dataset(req_pcb, db)
    print(f"Generated PCB Dataset: {res_pcb['id']}")

    eval_pcb = run_evaluation(EvaluationRunRequest(
        dataset_id=res_pcb["id"],
        model_name="visionforge-demo-v1",
        provider="demo"
    ), db)
    print(f"PCB Eval Acc: {eval_pcb['overall_accuracy']*100:.1f}%, Latency: {eval_pcb['avg_latency_ms']}ms")

    # 3. Aerospace Structural Fasteners Benchmark
    print("\n[3/3] Synthesizing Aerospace Fasteners & Composite Hardware Benchmark...")
    req_aero = DatasetCreateRequest(
        name="Aerospace Structural Fasteners Benchmark",
        description="Carbon-fiber composite panels with titanium structural brackets, shear rivets, and safety lockwire bolts.",
        domain="Aerospace Airframe Fastener Inspection",
        image_family="aerospace_structural",
        image_count=5,
        components_per_scene=6,
        difficulty="hard",
        defect_types=["missing", "misplaced", "orientation", "occlusion"],
        lighting="standard_5000k",
        seed=303
    )
    res_aero = generate_dataset(req_aero, db)
    print(f"Generated Aerospace Dataset: {res_aero['id']}")

    eval_aero = run_evaluation(EvaluationRunRequest(
        dataset_id=res_aero["id"],
        model_name="visionforge-demo-v1",
        provider="demo"
    ), db)
    print(f"Aerospace Eval Acc: {eval_aero['overall_accuracy']*100:.1f}%, Latency: {eval_aero['avg_latency_ms']}ms")

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
