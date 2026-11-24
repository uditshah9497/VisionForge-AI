import os
import json
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.core.database import get_db
from backend.app.core.config import (
    ARTIFACTS_DIR, REPORTS_DIR,
    GEMINI_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY
)
from backend.app.models.db_models import (
    DatasetModel, SyntheticSceneModel, ImageModel, ComponentModel,
    QuestionModel, GroundTruthModel, ValidationResultModel,
    EvaluationRunModel, ModelResponseModel, EvaluationMetricModel,
    BlindSpotPairModel, BenchmarkReportModel
)
from backend.app.models.schemas import (
    DatasetCreateRequest, EvaluationRunRequest, BlindSpotGenerateRequest
)
from backend.app.modules.synthetic.generator import SceneGenerator
from backend.app.modules.synthetic.renderer import SyntheticRenderer
from backend.app.modules.questions.question_engine import QuestionEngine
from backend.app.modules.validation.task_validator import TaskValidator
from backend.app.modules.evaluation.eval_engine import EvaluationEngine
from backend.app.modules.adversarial.blind_spot import BlindSpotEngine
from backend.app.modules.analytics.reporting import ReportingEngine

router = APIRouter(prefix="/api")

# HEALTH CHECK
@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "VisionForge AI Multimodal Benchmark Factory",
        "version": "1.0.0"
    }

# MODEL CONFIGURATIONS
@router.get("/models")
def get_available_models():
    """List supported frontier multimodal models and their configuration status."""
    return [
        {
            "id": "gemini-1.5-pro",
            "provider": "gemini",
            "name": "Google Gemini 1.5 Pro",
            "is_configured": bool(GEMINI_API_KEY),
            "description": "Frontier multimodal foundation model with 2M token context window."
        },
        {
            "id": "gemini-2.0-flash",
            "provider": "gemini",
            "name": "Google Gemini 2.0 Flash",
            "is_configured": bool(GEMINI_API_KEY),
            "description": "High-speed multimodal model with real-time reasoning capabilities."
        },
        {
            "id": "gpt-4o",
            "provider": "openai",
            "name": "OpenAI GPT-4o",
            "is_configured": bool(OPENAI_API_KEY),
            "description": "Omni-modal visual reasoning foundation model."
        },
        {
            "id": "claude-3-5-sonnet-20241022",
            "provider": "anthropic",
            "name": "Anthropic Claude 3.5 Sonnet",
            "is_configured": bool(ANTHROPIC_API_KEY),
            "description": "State-of-the-art vision and code reasoning model."
        },
        {
            "id": "visionforge-demo-v1",
            "provider": "demo",
            "name": "VisionForge Calibrated Simulator (Demo)",
            "is_configured": True,
            "description": "Offline calibrated model simulator for local hackathon testing and reproducibility."
        }
    ]

# DATASET GENERATION & RETRIEVAL
@router.post("/datasets/generate")
def generate_dataset(req: DatasetCreateRequest, db: Session = Depends(get_db)):
    """Generate a full synthetic benchmark dataset with scene graphs, rendered images,

    deterministic questions, ground truth, and automated validation.
    """
    dataset_id = f"ds_{uuid.uuid4().hex[:8]}"
    db_dataset = DatasetModel(
        id=dataset_id,
        name=req.name,
        description=req.description,
        domain=req.domain,
        seed=req.seed,
        difficulty=req.difficulty,
        num_scenes=req.image_count,
        status="generating"
    )
    db.add(db_dataset)
    db.commit()

    generator = SceneGenerator(seed=req.seed)
    renderer = SyntheticRenderer()
    question_engine = QuestionEngine(seed=req.seed)
    validator = TaskValidator()

    for idx in range(req.image_count):
        scene_seed = req.seed + idx * 7919
        scene_id = f"sc_{dataset_id}_{idx + 1}"

        # 1. Generate Scene Graph
        sg = generator.generate_scene(
            scene_id=scene_id,
            dataset_id=dataset_id,
            image_family=getattr(req, "image_family", "mechanical_assembly"),
            difficulty=req.difficulty,
            component_count=req.components_per_scene,
            defect_types=req.defect_types,
            lighting=req.lighting,
            camera_perspective=req.camera_perspective,
            seed=scene_seed
        )

        # 2. Render Image
        img_filename = f"{scene_id}.png"
        img_path = str(ARTIFACTS_DIR / img_filename)
        render_info = renderer.render_scene(sg, img_path)

        # 3. Save Scene & Image records
        db_scene = SyntheticSceneModel(
            id=scene_id,
            dataset_id=dataset_id,
            scene_number=idx + 1,
            seed=scene_seed,
            difficulty=req.difficulty,
            lighting=req.lighting,
            defect_types_json=json.dumps(req.defect_types),
            scene_graph_json=json.dumps(sg),
            width=render_info["width"],
            height=render_info["height"]
        )
        db.add(db_scene)

        db_image = ImageModel(
            id=f"img_{scene_id}",
            scene_id=scene_id,
            file_path=img_path,
            format="PNG",
            width=render_info["width"],
            height=render_info["height"],
            file_size_bytes=render_info["file_size_bytes"]
        )
        db.add(db_image)

        # 4. Save Components
        for comp in sg.get("components", []):
            db_comp = ComponentModel(
                id=f"{scene_id}_{comp['id']}",
                scene_id=scene_id,
                component_type=comp["type"],
                name=comp["name"],
                bbox_json=json.dumps(comp["bbox"]),
                center_x=comp["center"]["x"],
                center_y=comp["center"]["y"],
                rotation_deg=comp.get("rotation_deg", 0.0),
                is_defective=comp.get("is_defective", False),
                defect_type=comp.get("defect_type"),
                visibility_score=comp.get("visibility_score", 1.0),
                layer=comp.get("layer", 1)
            )
            db.add(db_comp)

        # 5. Generate Questions & Ground Truth
        questions = question_engine.generate_questions_for_scene(sg, max_questions=4, seed=scene_seed)
        for q in questions:
            db_q = QuestionModel(
                id=q["id"],
                scene_id=scene_id,
                category=q["category"],
                difficulty=q["difficulty"],
                question_text=q["question_text"],
                expected_answer=q["expected_answer"],
                answer_type=q["answer_type"],
                supporting_component_ids_json=json.dumps(q["supporting_component_ids"]),
                derivation_rule=q.get("derivation_rule"),
                validation_status="PENDING"
            )
            db.add(db_q)

            db_gt = GroundTruthModel(
                id=f"gt_{q['id']}",
                question_id=q["id"],
                answer=q["expected_answer"],
                answer_type=q["answer_type"],
                derivation_rule=q.get("derivation_rule", "scene_graph_eval")
            )
            db.add(db_gt)

            # 6. Validate Task
            val_res = validator.validate_task(q, sg, image_path=img_path)
            db_q.validation_status = val_res["status"]

            db_val = ValidationResultModel(
                id=f"val_{q['id']}",
                question_id=q["id"],
                scene_id=scene_id,
                status=val_res["status"],
                score=val_res["score"],
                checks_json=json.dumps(val_res["checks"]),
                rejection_reason=val_res["rejection_reason"]
            )
            db.add(db_val)

    db_dataset.status = "ready"
    db.commit()

    return {
        "id": dataset_id,
        "name": req.name,
        "scenes_generated": req.image_count,
        "status": "ready"
    }

@router.get("/datasets")
def list_datasets(db: Session = Depends(get_db)):
    datasets = db.query(DatasetModel).order_by(DatasetModel.created_at.desc()).all()
    res = []
    for d in datasets:
        q_count = db.query(func.count(QuestionModel.id)).join(SyntheticSceneModel).filter(SyntheticSceneModel.dataset_id == d.id).scalar() or 0
        res.append({
            "id": d.id,
            "name": d.name,
            "description": d.description,
            "domain": d.domain,
            "seed": d.seed,
            "difficulty": d.difficulty,
            "num_scenes": d.num_scenes,
            "question_count": q_count,
            "status": d.status,
            "created_at": d.created_at.isoformat() if d.created_at else None
        })
    return res

@router.get("/datasets/{dataset_id}")
def get_dataset(dataset_id: str, db: Session = Depends(get_db)):
    d = db.query(DatasetModel).filter(DatasetModel.id == dataset_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Dataset not found")

    scenes = db.query(SyntheticSceneModel).filter(SyntheticSceneModel.dataset_id == dataset_id).all()
    scene_list = []
    for s in scenes:
        q_items = db.query(QuestionModel).filter(QuestionModel.scene_id == s.id).all()
        scene_list.append({
            "id": s.id,
            "scene_number": s.scene_number,
            "seed": s.seed,
            "image_url": f"/data/artifacts/{s.id}.png",
            "scene_graph": s.get_scene_graph(),
            "questions": [
                {
                    "id": q.id,
                    "category": q.category,
                    "difficulty": q.difficulty,
                    "question_text": q.question_text,
                    "expected_answer": q.expected_answer,
                    "answer_type": q.answer_type,
                    "validation_status": q.validation_status
                }
                for q in q_items
            ]
        })

    return {
        "id": d.id,
        "name": d.name,
        "description": d.description,
        "domain": d.domain,
        "seed": d.seed,
        "difficulty": d.difficulty,
        "num_scenes": d.num_scenes,
        "status": d.status,
        "scenes": scene_list
    }

# QUESTIONS
@router.get("/questions")
def list_questions(
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(QuestionModel)
    if category:
        query = query.filter(QuestionModel.category == category)
    if difficulty:
        query = query.filter(QuestionModel.difficulty == difficulty)
    if status:
        query = query.filter(QuestionModel.validation_status == status)

    questions = query.limit(100).all()
    return [
        {
            "id": q.id,
            "scene_id": q.scene_id,
            "image_url": f"/data/artifacts/{q.scene_id}.png",
            "category": q.category,
            "difficulty": q.difficulty,
            "question_text": q.question_text,
            "expected_answer": q.expected_answer,
            "answer_type": q.answer_type,
            "validation_status": q.validation_status,
            "supporting_component_ids": q.get_supporting_components(),
            "derivation_rule": q.derivation_rule
        }
        for q in questions
    ]

# VALIDATION CENTER
@router.get("/validation/summary")
def get_validation_summary(db: Session = Depends(get_db)):
    total = db.query(func.count(ValidationResultModel.id)).scalar() or 0
    passed = db.query(func.count(ValidationResultModel.id)).filter(ValidationResultModel.status == "PASS").scalar() or 0
    failed = db.query(func.count(ValidationResultModel.id)).filter(ValidationResultModel.status == "FAIL").scalar() or 0
    pass_rate = round((passed / total) * 100, 1) if total > 0 else 0.0

    rejected_results = db.query(ValidationResultModel).filter(ValidationResultModel.status == "FAIL").all()
    rejections = [
        {
            "id": r.id,
            "question_id": r.question_id,
            "scene_id": r.scene_id,
            "score": r.score,
            "rejection_reason": r.rejection_reason,
            "validated_at": r.validated_at.isoformat() if r.validated_at else None
        }
        for r in rejected_results
    ]

    return {
        "total_evaluated": total,
        "passed_count": passed,
        "failed_count": failed,
        "pass_rate": pass_rate,
        "quarantined_rejected_tasks": rejections
    }

# MODEL EVALUATION ARENA
@router.post("/evaluations/run")
def run_evaluation(req: EvaluationRunRequest, db: Session = Depends(get_db)):
    # Gather validated tasks for dataset
    questions_query = (
        db.query(QuestionModel, SyntheticSceneModel, ImageModel)
        .join(SyntheticSceneModel, QuestionModel.scene_id == SyntheticSceneModel.id)
        .join(ImageModel, SyntheticSceneModel.id == ImageModel.scene_id)
        .filter(SyntheticSceneModel.dataset_id == req.dataset_id)
        .filter(QuestionModel.validation_status == "PASS")
    )
    if req.max_questions:
        questions_query = questions_query.limit(req.max_questions)

    records = questions_query.all()
    if not records:
        raise HTTPException(status_code=400, detail="No validated tasks found for this dataset.")

    tasks = []
    for q, s, img in records:
        tasks.append({
            "question_id": q.id,
            "category": q.category,
            "difficulty": q.difficulty,
            "question_text": q.question_text,
            "expected_answer": q.expected_answer,
            "answer_type": q.answer_type,
            "image_path": img.file_path
        })

    # Run Benchmark
    bench_result = EvaluationEngine.run_benchmark(
        tasks=tasks,
        provider=req.provider,
        model_name=req.model_name
    )

    run_id = bench_result["run_id"]
    db_run = EvaluationRunModel(
        id=run_id,
        dataset_id=req.dataset_id,
        model_name=bench_result["model_name"],
        model_provider=bench_result["model_provider"],
        status="completed",
        total_tasks=bench_result["total_tasks"],
        evaluated_tasks=bench_result["evaluated_tasks"],
        overall_accuracy=bench_result["overall_accuracy"],
        avg_latency_ms=bench_result["avg_latency_ms"],
        total_cost_usd=bench_result["total_cost_usd"]
    )
    db.add(db_run)

    for r in bench_result["responses"]:
        db_resp = ModelResponseModel(
            id=f"mr_{uuid.uuid4().hex[:8]}",
            evaluation_run_id=run_id,
            question_id=r["question_id"],
            model_name=bench_result["model_name"],
            raw_response=r["raw_response"],
            normalized_answer=r["normalized_answer"],
            expected_answer=r["expected_answer"],
            is_correct=r["is_correct"],
            latency_ms=r["latency_ms"],
            prompt_tokens=r["prompt_tokens"],
            completion_tokens=r["completion_tokens"],
            estimated_cost_usd=r["estimated_cost_usd"],
            failure_category=r["failure_category"]
        )
        db.add(db_resp)

    # Save metrics
    for m_name, m_val in bench_result["metrics"].items():
        db_metric = EvaluationMetricModel(
            id=f"m_{uuid.uuid4().hex[:8]}",
            evaluation_run_id=run_id,
            category="summary",
            metric_name=m_name,
            value=m_val
        )
        db.add(db_metric)

    # Automatically generate downloadable reports
    json_path = ReportingEngine.generate_json_report(bench_result, f"report_{run_id}.json")
    csv_path = ReportingEngine.generate_csv_report(bench_result["responses"], f"report_{run_id}.csv")
    md_path = ReportingEngine.generate_markdown_report(bench_result, f"report_{run_id}.md")

    db_report = BenchmarkReportModel(
        id=f"rep_{run_id}",
        evaluation_run_id=run_id,
        title=f"Benchmark Report - {bench_result['model_name']}",
        format="JSON",
        file_path=json_path,
        summary_json=json.dumps(bench_result["metrics"])
    )
    db.add(db_report)
    db.commit()

    return bench_result

@router.get("/evaluations")
def list_evaluations(db: Session = Depends(get_db)):
    runs = db.query(EvaluationRunModel).order_by(EvaluationRunModel.started_at.desc()).all()
    return [
        {
            "id": r.id,
            "dataset_id": r.dataset_id,
            "model_name": r.model_name,
            "model_provider": r.model_provider,
            "status": r.status,
            "total_tasks": r.total_tasks,
            "evaluated_tasks": r.evaluated_tasks,
            "overall_accuracy": r.overall_accuracy,
            "avg_latency_ms": r.avg_latency_ms,
            "total_cost_usd": r.total_cost_usd,
            "started_at": r.started_at.isoformat() if r.started_at else None
        }
        for r in runs
    ]

@router.get("/evaluations/{run_id}")
def get_evaluation(run_id: str, db: Session = Depends(get_db)):
    r = db.query(EvaluationRunModel).filter(EvaluationRunModel.id == run_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Evaluation run not found")

    responses = (
        db.query(ModelResponseModel, QuestionModel)
        .join(QuestionModel, ModelResponseModel.question_id == QuestionModel.id)
        .filter(ModelResponseModel.evaluation_run_id == run_id)
        .all()
    )

    metrics = db.query(EvaluationMetricModel).filter(EvaluationMetricModel.evaluation_run_id == run_id).all()
    metric_map = {m.metric_name: m.value for m in metrics}

    return {
        "id": r.id,
        "dataset_id": r.dataset_id,
        "model_name": r.model_name,
        "model_provider": r.model_provider,
        "status": r.status,
        "total_tasks": r.total_tasks,
        "overall_accuracy": r.overall_accuracy,
        "avg_latency_ms": r.avg_latency_ms,
        "total_cost_usd": r.total_cost_usd,
        "metrics": metric_map,
        "responses": [
            {
                "id": mr.id,
                "question_id": mr.question_id,
                "category": q.category,
                "difficulty": q.difficulty,
                "question_text": q.question_text,
                "expected_answer": mr.expected_answer,
                "model_response": mr.raw_response,
                "normalized_answer": mr.normalized_answer,
                "is_correct": mr.is_correct,
                "latency_ms": mr.latency_ms,
                "failure_category": mr.failure_category
            }
            for mr, q in responses
        ]
    }

# ADVERSARIAL BLIND SPOT DISCOVERY
@router.post("/blind-spot/generate")
def generate_blind_spot(req: BlindSpotGenerateRequest, db: Session = Depends(get_db)):
    engine = BlindSpotEngine()
    result = engine.generate_blind_spot_test(
        base_seed=req.base_seed,
        perturbation_type=req.perturbation_type,
        provider=req.provider,
        model_name=req.model_name
    )

    db_pair = BlindSpotPairModel(
        id=result["id"],
        original_scene_id=f"sc_base_{result['id']}",
        modified_scene_id=f"sc_mod_{result['id']}",
        property_changed=result["property_changed"],
        delta_description=result["delta_description"],
        target_component_type=result["target_component_type"],
        question_text=result["question_text"],
        original_expected_answer=result["original_expected_answer"],
        modified_expected_answer=result["modified_expected_answer"],
        model_name=result["model_name"],
        original_model_answer=result["original_model_answer"],
        modified_model_answer=result["modified_model_answer"],
        is_blind_spot=result["is_blind_spot"],
        failure_category=result["failure_category"]
    )
    db.add(db_pair)
    db.commit()

    return result

@router.get("/blind-spot/pairs")
def list_blind_spot_pairs(db: Session = Depends(get_db)):
    pairs = db.query(BlindSpotPairModel).order_by(BlindSpotPairModel.created_at.desc()).all()
    return [
        {
            "id": p.id,
            "property_changed": p.property_changed,
            "delta_description": p.delta_description,
            "target_component_type": p.target_component_type,
            "question_text": p.question_text,
            "original_image_url": f"/data/artifacts/pair_{p.id}_orig.png",
            "modified_image_url": f"/data/artifacts/pair_{p.id}_mod.png",
            "original_expected_answer": p.original_expected_answer,
            "modified_expected_answer": p.modified_expected_answer,
            "model_name": p.model_name,
            "original_model_answer": p.original_model_answer,
            "modified_model_answer": p.modified_model_answer,
            "is_blind_spot": p.is_blind_spot,
            "failure_category": p.failure_category
        }
        for p in pairs
    ]

# OVERVIEW & ANALYTICS
@router.get("/analytics/overview")
def get_analytics_overview(db: Session = Depends(get_db)):
    total_imgs = db.query(func.count(ImageModel.id)).scalar() or 0
    total_qs = db.query(func.count(QuestionModel.id)).scalar() or 0
    passed_tasks = db.query(func.count(ValidationResultModel.id)).filter(ValidationResultModel.status == "PASS").scalar() or 0
    rejected_tasks = db.query(func.count(ValidationResultModel.id)).filter(ValidationResultModel.status == "FAIL").scalar() or 0
    val_rate = round((passed_tasks / (passed_tasks + rejected_tasks)) * 100, 1) if (passed_tasks + rejected_tasks) > 0 else 0.0

    runs = db.query(EvaluationRunModel).all()
    eval_count = len(runs)
    avg_acc = round(sum(r.overall_accuracy for r in runs) / eval_count * 100, 1) if eval_count > 0 else 0.0

    # Questions category distribution
    cats = db.query(QuestionModel.category, func.count(QuestionModel.id)).group_by(QuestionModel.category).all()
    cat_dist = {c: count for c, count in cats}

    # Accuracy by category across all evaluations
    cat_acc_query = (
        db.query(QuestionModel.category, func.avg(ModelResponseModel.is_correct))
        .join(QuestionModel, ModelResponseModel.question_id == QuestionModel.id)
        .group_by(QuestionModel.category)
        .all()
    )
    accuracy_by_cat = {c: round(float(avg_val or 0.0) * 100, 1) for c, avg_val in cat_acc_query}

    # Blind spots count
    blind_spots_found = db.query(func.count(BlindSpotPairModel.id)).filter(BlindSpotPairModel.is_blind_spot == True).scalar() or 0

    return {
        "total_images_generated": total_imgs,
        "total_questions_generated": total_qs,
        "validated_tasks": passed_tasks,
        "rejected_tasks": rejected_tasks,
        "validation_pass_rate": val_rate,
        "evaluation_runs_count": eval_count,
        "average_model_accuracy": avg_acc,
        "category_distribution": cat_dist,
        "accuracy_by_category": accuracy_by_cat,
        "blind_spots_found": blind_spots_found
    }

# REPORTS
@router.get("/reports")
def list_reports(db: Session = Depends(get_db)):
    reports = db.query(BenchmarkReportModel).order_by(BenchmarkReportModel.created_at.desc()).all()
    return [
        {
            "id": rep.id,
            "evaluation_run_id": rep.evaluation_run_id,
            "title": rep.title,
            "format": rep.format,
            "file_name": os.path.basename(rep.file_path),
            "created_at": rep.created_at.isoformat() if rep.created_at else None
        }
        for rep in reports
    ]

@router.get("/reports/{filename}/download")
def download_report(filename: str):
    path = REPORTS_DIR / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="Report file not found")
    return FileResponse(str(path), filename=filename)
