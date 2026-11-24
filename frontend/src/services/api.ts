import {
  Dataset,
  QuestionItem,
  ValidationSummary,
  ModelConfig,
  EvaluationRun,
  BlindSpotPair,
  AnalyticsOverview,
  BenchmarkReport
} from '../types';

const BASE_URL = '/api';

export const api = {
  // Analytics
  async getAnalyticsOverview(): Promise<AnalyticsOverview> {
    const res = await fetch(`${BASE_URL}/analytics/overview`);
    if (!res.ok) throw new Error('Failed to fetch analytics overview');
    return res.json();
  },

  // Datasets
  async getDatasets(): Promise<Dataset[]> {
    const res = await fetch(`${BASE_URL}/datasets`);
    if (!res.ok) throw new Error('Failed to fetch datasets');
    return res.json();
  },

  async getDataset(id: string): Promise<any> {
    const res = await fetch(`${BASE_URL}/datasets/${id}`);
    if (!res.ok) throw new Error(`Failed to fetch dataset ${id}`);
    return res.json();
  },

  async generateDataset(params: {
    name: string;
    description?: string;
    domain?: string;
    image_family?: string;
    image_count: number;
    components_per_scene: number;
    difficulty: string;
    defect_types: string[];
    lighting: string;
    seed: number;
  }): Promise<any> {
    const res = await fetch(`${BASE_URL}/datasets/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params)
    });
    if (!res.ok) throw new Error('Failed to generate dataset');
    return res.json();
  },

  // Questions
  async getQuestions(filters?: { category?: string; difficulty?: string; status?: string }): Promise<QuestionItem[]> {
    const query = new URLSearchParams();
    if (filters?.category) query.append('category', filters.category);
    if (filters?.difficulty) query.append('difficulty', filters.difficulty);
    if (filters?.status) query.append('status', filters.status);
    const res = await fetch(`${BASE_URL}/questions?${query.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch questions');
    return res.json();
  },

  // Validation
  async getValidationSummary(): Promise<ValidationSummary> {
    const res = await fetch(`${BASE_URL}/validation/summary`);
    if (!res.ok) throw new Error('Failed to fetch validation summary');
    return res.json();
  },

  // Models
  async getModels(): Promise<ModelConfig[]> {
    const res = await fetch(`${BASE_URL}/models`);
    if (!res.ok) throw new Error('Failed to fetch model configs');
    return res.json();
  },

  // Evaluations
  async getEvaluations(): Promise<EvaluationRun[]> {
    const res = await fetch(`${BASE_URL}/evaluations`);
    if (!res.ok) throw new Error('Failed to fetch evaluation runs');
    return res.json();
  },

  async getEvaluation(id: string): Promise<EvaluationRun> {
    const res = await fetch(`${BASE_URL}/evaluations/${id}`);
    if (!res.ok) throw new Error(`Failed to fetch evaluation ${id}`);
    return res.json();
  },

  async runEvaluation(params: {
    dataset_id: string;
    model_name: string;
    provider: string;
    max_questions?: number;
  }): Promise<EvaluationRun> {
    const res = await fetch(`${BASE_URL}/evaluations/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Evaluation run failed');
    }
    return res.json();
  },

  // Blind Spot Discovery
  async generateBlindSpot(params: {
    base_seed: number;
    perturbation_type: string;
    provider: string;
    model_name: string;
  }): Promise<BlindSpotPair> {
    const res = await fetch(`${BASE_URL}/blind-spot/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params)
    });
    if (!res.ok) throw new Error('Failed to generate blind spot pair');
    return res.json();
  },

  async getBlindSpotPairs(): Promise<BlindSpotPair[]> {
    const res = await fetch(`${BASE_URL}/blind-spot/pairs`);
    if (!res.ok) throw new Error('Failed to fetch blind spot pairs');
    return res.json();
  },

  // Reports
  async getReports(): Promise<BenchmarkReport[]> {
    const res = await fetch(`${BASE_URL}/reports`);
    if (!res.ok) throw new Error('Failed to fetch reports');
    return res.json();
  },

  getReportDownloadUrl(fileName: string): string {
    return `${BASE_URL}/reports/${fileName}/download`;
  }
};
