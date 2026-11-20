export interface Dataset {
  id: string;
  name: string;
  description?: string;
  domain: string;
  seed: number;
  difficulty: string;
  num_scenes: number;
  question_count?: number;
  status: string;
  created_at?: string;
}

export interface ComponentItem {
  id: string;
  type: string;
  name: string;
  center: { x: number; y: number };
  dimensions: Record<string, any>;
  bbox: [number, number, number, number];
  rotation_deg: number;
  material?: string;
  is_defective: boolean;
  defect_type?: string | null;
  visibility_score: number;
  layer: number;
}

export interface SceneGraph {
  scene_id: string;
  dataset_id: string;
  seed: number;
  difficulty: string;
  dimensions: { width: number; height: number };
  workstation: Record<string, any>;
  components: ComponentItem[];
  spatial_relations: Array<{
    subject_id: string;
    relation: string;
    object_id: string;
    distance_px: number;
  }>;
  defect_types: string[];
}

export interface SceneItem {
  id: string;
  scene_number: number;
  seed: number;
  image_url: string;
  scene_graph: SceneGraph;
  questions: QuestionItem[];
}

export interface QuestionItem {
  id: string;
  scene_id: string;
  image_url?: string;
  category: string;
  difficulty: string;
  question_text: string;
  expected_answer: string;
  answer_type: string;
  supporting_component_ids?: string[];
  derivation_rule?: string;
  validation_status: 'PASS' | 'FAIL' | 'PENDING';
}

export interface ValidationSummary {
  total_evaluated: number;
  passed_count: number;
  failed_count: number;
  pass_rate: number;
  quarantined_rejected_tasks: Array<{
    id: string;
    question_id: string;
    scene_id: string;
    score: number;
    rejection_reason: string;
    validated_at: string;
  }>;
}

export interface ModelConfig {
  id: string;
  provider: string;
  name: string;
  is_configured: boolean;
  description: string;
}

export interface EvaluationResponseItem {
  id: string;
  question_id: string;
  category: string;
  difficulty: string;
  question_text: string;
  expected_answer: string;
  model_response: string;
  normalized_answer: string;
  is_correct: boolean;
  latency_ms: number;
  failure_category?: string | null;
}

export interface EvaluationRun {
  id: string;
  dataset_id: string;
  model_name: string;
  model_provider: string;
  status: string;
  total_tasks: number;
  evaluated_tasks?: number;
  overall_accuracy: number;
  avg_latency_ms: number;
  total_cost_usd: number;
  metrics?: Record<string, number>;
  responses?: EvaluationResponseItem[];
  started_at: string;
  completed_at?: string;
}

export interface BlindSpotPair {
  id: string;
  property_changed: string;
  delta_description: string;
  target_component_type?: string;
  question_text: string;
  original_image_url: string;
  modified_image_url: string;
  original_expected_answer: string;
  modified_expected_answer: string;
  model_name?: string;
  original_model_answer?: string;
  modified_model_answer?: string;
  is_blind_spot: boolean;
  failure_category?: string;
}

export interface AnalyticsOverview {
  total_images_generated: number;
  total_questions_generated: number;
  validated_tasks: number;
  rejected_tasks: number;
  validation_pass_rate: number;
  evaluation_runs_count: number;
  average_model_accuracy: number;
  category_distribution: Record<string, number>;
  accuracy_by_category: Record<string, number>;
  blind_spots_found: number;
}

export interface BenchmarkReport {
  id: string;
  evaluation_run_id: string;
  title: string;
  format: string;
  file_name: string;
  created_at: string;
}
