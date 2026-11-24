from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

# Component and Geometry Schemas
class BoundingBox(BaseModel):
    x_min: float
    y_min: float
    x_max: float
    y_max: float

class ComponentSchema(BaseModel):
    id: str
    type: str
    name: str
    center: Dict[str, float]  # {"x": ..., "y": ...}
    dimensions: Dict[str, float]  # {"width": ..., "height": ..., "radius": ...}
    bbox: List[float]  # [x_min, y_min, x_max, y_max]
    rotation_deg: float = 0.0
    color: str = "#94a3b8"
    expected_position: Dict[str, Any]
    is_defective: bool = False
    defect_type: Optional[str] = None
    occlusion_ratio: float = 0.0
    visibility_score: float = 1.0
    layer: int = 1

class SpatialRelation(BaseModel):
    subject_id: str
    relation: str  # left_of, right_of, above, below, aligned_with, adjacent_to
    object_id: str
    distance_px: float

class WorkstationConfig(BaseModel):
    fixture_type: str = "optical_breadboard_grid"
    surface_color: str = "#0f172a"
    grid_spacing: int = 40
    lighting: Dict[str, Any] = Field(default_factory=lambda: {
        "ambient": 0.75,
        "direction": "top_left",
        "shadows_enabled": True,
        "specular_highlights": True,
        "color_temp": "5000K"
    })

class SceneGraph(BaseModel):
    scene_id: str
    dataset_id: str
    seed: int
    difficulty: str
    dimensions: Dict[str, int] = Field(default_factory=lambda: {"width": 800, "height": 600})
    workstation: WorkstationConfig = Field(default_factory=WorkstationConfig)
    components: List[ComponentSchema] = Field(default_factory=list)
    spatial_relations: List[SpatialRelation] = Field(default_factory=list)
    defect_types: List[str] = Field(default_factory=list)

# Dataset Schemas
class DatasetCreateRequest(BaseModel):
    name: str = "Smart Retail Supermarket Shelf Inspection Bench"
    description: Optional[str] = "Everyday consumer goods (soda cans, milk cartons, cereal boxes, apples, water bottles) on supermarket display shelves with automated out-of-stock and misalignment detection."
    domain: str = "Smart Retail & Supermarket Shelf Inspection"
    image_family: str = "smart_retail_shelf"  # smart_retail_shelf, mechanical_assembly, pcb_electronics, aerospace_structural
    image_count: int = 5
    components_per_scene: int = 6
    difficulty: str = "medium"  # easy, medium, hard
    defect_types: List[str] = Field(default_factory=lambda: ["missing", "misplaced", "orientation", "occlusion"])
    lighting: str = "standard_5000k"
    camera_perspective: str = "top_down"
    seed: int = 42

class DatasetResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    domain: str
    image_family: str = "smart_retail_shelf"
    seed: int
    difficulty: str
    num_scenes: int
    created_at: str
    status: str

# Question Schemas
class QuestionResponse(BaseModel):
    id: str
    scene_id: str
    category: str
    difficulty: str
    question_text: str
    expected_answer: str
    answer_type: str
    supporting_component_ids: List[str]
    derivation_rule: Optional[str]
    validation_status: str

# Validation Schemas
class ValidationResultResponse(BaseModel):
    id: str
    question_id: str
    scene_id: str
    status: str  # PASS, FAIL
    score: float
    checks: Dict[str, Any]
    rejection_reason: Optional[str]
    validated_at: str

class ValidationSummary(BaseModel):
    total_evaluated: int
    passed_count: int
    failed_count: int
    pass_rate: float
    rejection_reasons: Dict[str, int]

# Evaluation Schemas
class EvaluationRunRequest(BaseModel):
    dataset_id: str
    model_name: str = "gemini-1.5-pro"  # or gpt-4o, claude-3-5-sonnet, visionforge-demo-v1
    provider: str = "demo"  # gemini, openai, anthropic, demo
    max_questions: Optional[int] = None

class ModelResponseItem(BaseModel):
    id: str
    question_id: str
    category: str
    difficulty: str
    question_text: str
    expected_answer: str
    model_response: str
    normalized_answer: str
    is_correct: bool
    latency_ms: float
    estimated_cost_usd: float
    failure_category: Optional[str]

class EvaluationRunResponse(BaseModel):
    id: str
    dataset_id: str
    model_name: str
    model_provider: str
    status: str
    total_tasks: int
    evaluated_tasks: int
    overall_accuracy: float
    avg_latency_ms: float
    total_cost_usd: float
    metrics: Dict[str, float]
    started_at: str
    completed_at: Optional[str]

# Adversarial Blind Spot Schemas
class BlindSpotGenerateRequest(BaseModel):
    base_seed: int = 42
    perturbation_type: str = "component_removed"  # component_removed, misplaced, orientation_inversion, lighting_change, occlusion
    model_name: str = "visionforge-demo-v1"
    provider: str = "demo"

class BlindSpotPairResponse(BaseModel):
    id: str
    property_changed: str
    delta_description: str
    target_component_type: Optional[str]
    question_text: str
    original_image_url: str
    modified_image_url: str
    original_expected_answer: str
    modified_expected_answer: str
    original_model_answer: Optional[str]
    modified_model_answer: Optional[str]
    is_blind_spot: bool
    failure_category: Optional[str]

# Analytics Schemas
class AnalyticsOverviewResponse(BaseModel):
    total_images_generated: int
    total_questions_generated: int
    validated_tasks: int
    rejected_tasks: int
    validation_pass_rate: float
    evaluation_runs_count: int
    models_evaluated_count: int
    average_model_accuracy: float
    recent_runs: List[Dict[str, Any]]
    category_distribution: Dict[str, int]
    accuracy_by_category: Dict[str, float]
    accuracy_by_difficulty: Dict[str, float]
    blind_spots_found: int
