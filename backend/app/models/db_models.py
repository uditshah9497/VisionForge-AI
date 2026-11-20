import json
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey, Index
)
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

def utcnow():
    return datetime.now(timezone.utc)

class DatasetModel(Base):
    __tablename__ = "datasets"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    domain = Column(String(100), default="Manufacturing Quality Inspection")
    seed = Column(Integer, default=42)
    difficulty = Column(String(32), default="medium")
    num_scenes = Column(Integer, default=0)
    created_at = Column(DateTime, default=utcnow)
    status = Column(String(32), default="ready")  # generating, ready, failed

    scenes = relationship("SyntheticSceneModel", back_populates="dataset", cascade="all, delete-orphan")
    evaluation_runs = relationship("EvaluationRunModel", back_populates="dataset", cascade="all, delete-orphan")

class SyntheticSceneModel(Base):
    __tablename__ = "synthetic_scenes"

    id = Column(String(64), primary_key=True, index=True)
    dataset_id = Column(String(64), ForeignKey("datasets.id"), nullable=False, index=True)
    scene_number = Column(Integer, default=1)
    seed = Column(Integer, default=42)
    difficulty = Column(String(32), default="medium")
    lighting = Column(String(64), default="standard_5000k")
    defect_types_json = Column(Text, default="[]")
    scene_graph_json = Column(Text, nullable=False)
    width = Column(Integer, default=800)
    height = Column(Integer, default=600)
    created_at = Column(DateTime, default=utcnow)

    dataset = relationship("DatasetModel", back_populates="scenes")
    image = relationship("ImageModel", back_populates="scene", uselist=False, cascade="all, delete-orphan")
    components = relationship("ComponentModel", back_populates="scene", cascade="all, delete-orphan")
    questions = relationship("QuestionModel", back_populates="scene", cascade="all, delete-orphan")
    validation_results = relationship("ValidationResultModel", back_populates="scene", cascade="all, delete-orphan")

    def get_scene_graph(self):
        return json.loads(self.scene_graph_json) if self.scene_graph_json else {}

class ImageModel(Base):
    __tablename__ = "images"

    id = Column(String(64), primary_key=True, index=True)
    scene_id = Column(String(64), ForeignKey("synthetic_scenes.id"), unique=True, nullable=False)
    file_path = Column(String(512), nullable=False)
    format = Column(String(16), default="PNG")
    width = Column(Integer, default=800)
    height = Column(Integer, default=600)
    file_size_bytes = Column(Integer, default=0)
    created_at = Column(DateTime, default=utcnow)

    scene = relationship("SyntheticSceneModel", back_populates="image")

class ComponentModel(Base):
    __tablename__ = "components"

    id = Column(String(64), primary_key=True, index=True)
    scene_id = Column(String(64), ForeignKey("synthetic_scenes.id"), nullable=False, index=True)
    component_type = Column(String(64), nullable=False, index=True)
    name = Column(String(128), nullable=False)
    bbox_json = Column(String(128), nullable=False)  # [x_min, y_min, x_max, y_max]
    center_x = Column(Float, nullable=False)
    center_y = Column(Float, nullable=False)
    rotation_deg = Column(Float, default=0.0)
    is_defective = Column(Boolean, default=False)
    defect_type = Column(String(64), nullable=True)
    visibility_score = Column(Float, default=1.0)
    layer = Column(Integer, default=1)

    scene = relationship("SyntheticSceneModel", back_populates="components")

    def get_bbox(self):
        return json.loads(self.bbox_json) if self.bbox_json else []

class QuestionModel(Base):
    __tablename__ = "questions"

    id = Column(String(64), primary_key=True, index=True)
    scene_id = Column(String(64), ForeignKey("synthetic_scenes.id"), nullable=False, index=True)
    category = Column(String(64), nullable=False, index=True)  # identification, counting, spatial, anomaly, relationship
    difficulty = Column(String(32), default="medium")
    question_text = Column(Text, nullable=False)
    expected_answer = Column(Text, nullable=False)
    answer_type = Column(String(32), default="text")  # integer, boolean, category, text
    supporting_component_ids_json = Column(Text, default="[]")
    derivation_rule = Column(Text, nullable=True)
    validation_status = Column(String(32), default="PENDING")  # PASS, FAIL, PENDING

    scene = relationship("SyntheticSceneModel", back_populates="questions")
    ground_truth = relationship("GroundTruthModel", back_populates="question", uselist=False, cascade="all, delete-orphan")
    validation_result = relationship("ValidationResultModel", back_populates="question", uselist=False, cascade="all, delete-orphan")
    responses = relationship("ModelResponseModel", back_populates="question", cascade="all, delete-orphan")

    def get_supporting_components(self):
        return json.loads(self.supporting_component_ids_json) if self.supporting_component_ids_json else []

class GroundTruthModel(Base):
    __tablename__ = "ground_truth"

    id = Column(String(64), primary_key=True, index=True)
    question_id = Column(String(64), ForeignKey("questions.id"), unique=True, nullable=False)
    answer = Column(Text, nullable=False)
    answer_type = Column(String(32), default="text")
    derivation_rule = Column(Text, nullable=False)
    computed_metadata_json = Column(Text, default="{}")
    computed_at = Column(DateTime, default=utcnow)

    question = relationship("QuestionModel", back_populates="ground_truth")

class ValidationResultModel(Base):
    __tablename__ = "validation_results"

    id = Column(String(64), primary_key=True, index=True)
    question_id = Column(String(64), ForeignKey("questions.id"), unique=True, nullable=False)
    scene_id = Column(String(64), ForeignKey("synthetic_scenes.id"), nullable=False, index=True)
    status = Column(String(32), default="PASS")  # PASS, FAIL
    score = Column(Float, default=1.0)
    checks_json = Column(Text, default="{}")
    rejection_reason = Column(Text, nullable=True)
    validated_at = Column(DateTime, default=utcnow)

    question = relationship("QuestionModel", back_populates="validation_result")
    scene = relationship("SyntheticSceneModel", back_populates="validation_results")

    def get_checks(self):
        return json.loads(self.checks_json) if self.checks_json else {}

class ModelConfigModel(Base):
    __tablename__ = "model_configurations"

    id = Column(String(64), primary_key=True, index=True)
    provider = Column(String(64), nullable=False)  # gemini, openai, anthropic, demo
    model_name = Column(String(128), nullable=False)
    api_version = Column(String(64), nullable=True)
    is_active = Column(Boolean, default=True)
    supports_vision = Column(Boolean, default=True)
    cost_per_1k_input_tokens = Column(Float, default=0.001)
    cost_per_1k_output_tokens = Column(Float, default=0.002)
    created_at = Column(DateTime, default=utcnow)

class EvaluationRunModel(Base):
    __tablename__ = "evaluation_runs"

    id = Column(String(64), primary_key=True, index=True)
    dataset_id = Column(String(64), ForeignKey("datasets.id"), nullable=False, index=True)
    model_name = Column(String(128), nullable=False, index=True)
    model_provider = Column(String(64), default="demo")
    status = Column(String(32), default="running")  # running, completed, failed
    total_tasks = Column(Integer, default=0)
    evaluated_tasks = Column(Integer, default=0)
    overall_accuracy = Column(Float, default=0.0)
    avg_latency_ms = Column(Float, default=0.0)
    total_cost_usd = Column(Float, default=0.0)
    started_at = Column(DateTime, default=utcnow)
    completed_at = Column(DateTime, nullable=True)

    dataset = relationship("DatasetModel", back_populates="evaluation_runs")
    responses = relationship("ModelResponseModel", back_populates="evaluation_run", cascade="all, delete-orphan")
    metrics = relationship("EvaluationMetricModel", back_populates="evaluation_run", cascade="all, delete-orphan")
    reports = relationship("BenchmarkReportModel", back_populates="evaluation_run", cascade="all, delete-orphan")

class ModelResponseModel(Base):
    __tablename__ = "model_responses"

    id = Column(String(64), primary_key=True, index=True)
    evaluation_run_id = Column(String(64), ForeignKey("evaluation_runs.id"), nullable=False, index=True)
    question_id = Column(String(64), ForeignKey("questions.id"), nullable=False, index=True)
    model_name = Column(String(128), nullable=False)
    raw_response = Column(Text, nullable=False)
    normalized_answer = Column(Text, nullable=False)
    expected_answer = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False)
    latency_ms = Column(Float, default=0.0)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    estimated_cost_usd = Column(Float, default=0.0)
    failure_category = Column(String(64), nullable=True)  # incorrect_value, unparseable, hallucination, timeout, none
    evaluated_at = Column(DateTime, default=utcnow)

    evaluation_run = relationship("EvaluationRunModel", back_populates="responses")
    question = relationship("QuestionModel", back_populates="responses")

class EvaluationMetricModel(Base):
    __tablename__ = "evaluation_metrics"

    id = Column(String(64), primary_key=True, index=True)
    evaluation_run_id = Column(String(64), ForeignKey("evaluation_runs.id"), nullable=False, index=True)
    category = Column(String(64), nullable=False)  # overall, counting, spatial, anomaly, identification, relationship, easy, medium, hard
    metric_name = Column(String(64), nullable=False)  # accuracy, precision, recall, f1, hallucination_rate, latency
    value = Column(Float, nullable=False)

    evaluation_run = relationship("EvaluationRunModel", back_populates="metrics")

class BlindSpotPairModel(Base):
    __tablename__ = "blind_spot_pairs"

    id = Column(String(64), primary_key=True, index=True)
    original_scene_id = Column(String(64), nullable=False)
    modified_scene_id = Column(String(64), nullable=False)
    property_changed = Column(String(64), nullable=False)  # component_removed, misplaced, orientation_inversion, lighting_change, occlusion
    delta_description = Column(Text, nullable=False)
    target_component_type = Column(String(64), nullable=True)
    question_text = Column(Text, nullable=False)
    original_expected_answer = Column(Text, nullable=False)
    modified_expected_answer = Column(Text, nullable=False)
    model_name = Column(String(128), nullable=True)
    original_model_answer = Column(Text, nullable=True)
    modified_model_answer = Column(Text, nullable=True)
    is_blind_spot = Column(Boolean, default=False)
    failure_category = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=utcnow)

class BenchmarkReportModel(Base):
    __tablename__ = "benchmark_reports"

    id = Column(String(64), primary_key=True, index=True)
    evaluation_run_id = Column(String(64), ForeignKey("evaluation_runs.id"), nullable=False)
    title = Column(String(255), nullable=False)
    format = Column(String(16), default="JSON")  # JSON, PDF, CSV
    file_path = Column(String(512), nullable=False)
    summary_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=utcnow)

    evaluation_run = relationship("EvaluationRunModel", back_populates="reports")
