# VisionForge AI: Synthetic Visual Intelligence & Multimodal Benchmark Factory

[![Pytest Tests](https://img.shields.io/badge/pytest-24%20passed-emerald?style=flat-square)](./tests)
[![Domain](https://img.shields.io/badge/domain-Industrial%20Manufacturing-cyan?style=flat-square)]()
[![Stack](https://img.shields.io/badge/stack-FastAPI%20%7C%20React%20%7C%20Tailwind-blue?style=flat-square)]()
[![Ground Truth](https://img.shields.io/badge/ground--truth-Deterministic%20Zero--LLM-emerald?style=flat-square)]()

**VisionForge AI** is an automated Visual Task Factory designed to reliably evaluate whether frontier multimodal AI foundation models (Gemini 1.5/2.0, GPT-4o, Claude 3.5 Sonnet) possess true physical and spatial visual intelligence.

---

## 1. Problem Formulation & Industrial Application

### The Real-World Challenge: Manufacturing Quality Inspection
In high-precision manufacturing (aerospace machining, automotive powertrain sub-assembly, electronics fabrication), visual inspection is the first and most critical defense against catastrophic mechanical and electrical failures:
- **Missing fasteners or retaining clips** result in structural fatigue under vibrational load.
- **Micro-displaced gears** (misaligned by just 15px / 2mm) cause gear tooth shear and transmission lockup.
- **Inverted brackets or reverse-polarity connectors** trigger electrical short-circuits.
- **Partial occlusion** by industrial wire harnesses or pneumatic lines obscures critical locking nuts.

### Why Multimodal Benchmarks Need Synthetic Task Generation
Evaluating frontier vision models on real factory photographs suffers from four fundamental problems:
1. **Lack of Provable Ground Truth:** Human labelers disagree on millimeter-scale displacements and occlusions.
2. **Data Leakage & Pre-Training Contamination:** Web-scraped photos frequently leak into frontier model training sets.
3. **Circularity & Hallucination:** Using LLMs to both establish reference answers and grade model responses creates confirmation bias.
4. **Impossibility of Controlled Adversarial Delta Testing:** Factory lines cannot reliably generate 1,000 paired image variations where exactly one bolt is removed or lighting is dimmed by 30%.

### VisionForge AI Solution
VisionForge AI establishes an end-to-end parametric factory:
```
Parametric Scene Generator (Controlled Defect Injection)
        ↓
Strict Geometric Scene Graph (Components, Positions, BBoxes, Defect Metadata)
        ↓
High-Fidelity Rendering Engine (Pillow/SVG: Specular highlights, shadows, optical breadboard grid)
        ↓
Deterministic Question & Ground Truth Engine (Zero-LLM Authority, pure metadata deduction)
        ↓
Automated Multi-Factor Task Validation Engine (Pass/Fail Gating, Visual Evidence Sufficiency)
        ↓
Multimodal Model Arena (Gemini, OpenAI, Anthropic, Calibrated Demo Simulator)
        ↓
Adversarial Visual Blind Spot Discovery (Controlled Delta-Pair Testing)
        ↓
Certified Industrial Benchmark Reports (JSON, CSV, Markdown)
```

---

## 2. Core Modules Architecture

- **Module A: Synthetic Image Generator & Renderer**
  - Parametric generation of 10+ industrial manufacturing components: Spur Gears, Hex Bolts, Hex Nuts, Base Mounting Plates, Industrial Multi-Pin Connectors, DIN Terminal Blocks, Hydraulic Pipes, 90° Gusseted Brackets, Circlip Fasteners, and CNC Assembly Fixtures.
  - Injects controlled defects: Missing components (empty tapped sockets), Misplaced components (Cartesian offsets), Inverted orientation (180° rotation), Partial occlusion (industrial wire harnesses), and ambient lighting profiles (5000K daylight, 3200K tungsten, low-lux stress).
  - High-precision Pillow renderer generates realistic drop shadows, specular bevels, and optical breadboard tapped hole grids.

- **Module B: Question Generation Engine**
  - Generates verifiable visual reasoning questions across 5 core capabilities:
    1. *Object Identification*
    2. *Object Counting*
    3. *Spatial Reasoning*
    4. *Anomaly Detection*
    5. *Component Relationship Reasoning*
  - Supported across Easy, Medium, and Hard difficulty tiers.

- **Module C: Deterministic Ground-Truth Engine**
  - **Zero-LLM Independence:** Reference answers are computed exclusively by functional deduction over the geometric and semantic scene graph metadata.

- **Module D: Automated Task Validation Engine**
  - 6 multi-factor validation gates: Image decodability, Bounding box canvas integrity, Visual evidence sufficiency (rejects questions targeting objects with visibility < 0.25), Answer determinism, Question template clarity, and Cross-scene deduplication.
  - Quarantines invalid tasks into an isolated store with diagnostic failure codes.

- **Module E: Multimodal Model Evaluation Engine**
  - Pluggable provider adapters: Google Gemini 1.5/2.0 API, OpenAI GPT-4o API, Anthropic Claude 3.5 API, and a calibrated offline Demo Simulator.
  - Deterministic answer normalization extracts clean tokens from verbose reasoning.
  - Records latency (ms), token usage, cost ($ USD), accuracy by capability, and failure categories (`incorrect_value`, `unparseable`, `hallucination`).

- **Module F: Adversarial Visual Testing ("Visual Blind Spot Discovery")**
  - Synthesizes pairs of nearly identical images where exactly ONE controlled property is perturbed.
  - Evaluates models on both images to discover visual blind spots such as **invariance hallucination** (model predicts identical answers despite component removal or rotation).

- **Module G: Industrial Analytics & Exportable Reports**
  - Multi-dimensional analytics charts and one-click downloadable benchmark reports (JSON, CSV, Markdown).

---

## 3. Technology Stack

- **Backend:** Python 3.14, FastAPI, SQLAlchemy ORM, Pydantic, Pillow, Uvicorn, Pytest.
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, Lucide React, Recharts.
- **Database:** SQLite (default zero-barrier portable dev) / PostgreSQL (production configurable via `DATABASE_URL`).
- **AI Integrations:** Google Gemini API, OpenAI API, Anthropic API, Calibrated Simulator.

---

## 4. Quickstart & Installation

### Prerequisites
- Python 3.10+
- Node.js 18+

### Setup & Launch
1. Clone the repository and navigate to the directory:
   ```bash
   cd Visual
   ```

2. Run the automated full-stack application:
   ```bash
   .\.venv\Scripts\python.exe run.py
   ```
   Or on Unix/macOS:
   ```bash
   python run.py
   ```

3. Open your browser:
   - **Enterprise Dashboard:** [http://localhost:8000](http://localhost:8000)
   - **Interactive API Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
   - **Health Check Endpoint:** [http://localhost:8000/api/health](http://localhost:8000/api/health)

---

## 5. Running Automated Tests

VisionForge AI includes 24 comprehensive unit and end-to-end integration tests:
```bash
.\.venv\Scripts\pytest.exe -v
```
Test coverage includes:
- Parametric scene generation and seed reproducibility
- Pillow image rendering and dimension verification
- 5 question reasoning categories and deterministic ground truth deduction
- Automated validation rules (ensuring invalid, ambiguous, or visually unsupported questions fail validation)
- Duplicate question rejection
- Answer normalizer (integer, boolean, category, unparseable distinction)
- Adversarial blind-spot generation
- Complete end-to-end benchmark pipeline test

---

## 6. Seed Demo Data Script

To populate or re-seed the platform with benchmark scenes, model evaluations, and adversarial blind-spot pairs:
```bash
.\.venv\Scripts\python.exe scripts/seed_demo_data.py
```
