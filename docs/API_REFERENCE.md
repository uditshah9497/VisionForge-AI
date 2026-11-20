# VisionForge AI: REST API Reference

The VisionForge AI backend is built with FastAPI and fully documented via interactive OpenAPI / Swagger specifications available at `/docs`.

## Base URL
`http://localhost:8000/api`

---

## 1. System & Models
- `GET /api/health`: Service health check and version info.
- `GET /api/models`: Returns list of supported multimodal models and their API credential configuration status (Gemini, GPT-4o, Claude 3.5, and Calibrated Demo Simulator).

---

## 2. Synthetic Dataset Generation
- `POST /api/datasets/generate`: Generates synthetic benchmark dataset.
  - **Payload:**
    ```json
    {
      "name": "Precision Assembly Benchmark",
      "image_count": 6,
      "components_per_scene": 6,
      "difficulty": "medium",
      "defect_types": ["missing", "misplaced", "orientation", "occlusion"],
      "lighting": "standard_5000k",
      "seed": 42
    }
    ```
- `GET /api/datasets`: Lists all generated datasets with scene and question counts.
- `GET /api/datasets/{id}`: Returns complete dataset details including scene graphs, component bounding boxes, and questions.

---

## 3. Question Factory & Ground Truth
- `GET /api/questions`: Lists generated visual reasoning tasks.
  - **Query Parameters:** `category`, `difficulty`, `status`.
  - **Response:** Array of questions with question text, expected ground truth answer, answer type, derivation rule, and validation status.

---

## 4. Automated Task Validation Center
- `GET /api/validation/summary`: Returns validation pass rate, passed task count, quarantined task count, and itemized failure rejection reasons.

---

## 5. Multimodal Model Arena
- `POST /api/evaluations/run`: Evaluates a multimodal model against validated dataset tasks.
  - **Payload:**
    ```json
    {
      "dataset_id": "ds_c76d6e0d",
      "model_name": "visionforge-demo-v1",
      "provider": "demo",
      "max_questions": 10
    }
    ```
  - **Response:** Overall accuracy, latency per task, cost estimate, and task-by-task normalized model answers.
- `GET /api/evaluations`: Lists historical evaluation runs.
- `GET /api/evaluations/{id}`: Returns complete run details and failure category breakdowns.

---

## 6. Adversarial Blind Spot Discovery
- `POST /api/blind-spot/generate`: Synthesizes an adversarial image pair with single-variable perturbation and evaluates model sensitivity.
  - **Perturbation Types:** `component_removed`, `misplaced`, `orientation_inversion`, `lighting_change`, `occlusion`.
- `GET /api/blind-spot/pairs`: Lists all tested adversarial pairs and identified visual blind spots.

---

## 7. Reports & Analytics
- `GET /api/analytics/overview`: High-level benchmark metrics and capability distributions.
- `GET /api/reports`: Lists generated benchmark reports.
- `GET /api/reports/{filename}/download`: One-click download for JSON, CSV, and Markdown report files.
