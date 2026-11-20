import os
import json
import csv
from typing import Dict, Any, List
from datetime import datetime, timezone
from backend.app.core.config import REPORTS_DIR

class ReportingEngine:
    """Generates comprehensive industrial benchmark reports and export artifacts."""

    @staticmethod
    def generate_json_report(evaluation_run: Dict[str, Any], output_filename: str) -> str:
        """Export full benchmark evaluation results as structured JSON."""
        file_path = REPORTS_DIR / output_filename
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(evaluation_run, f, indent=2)
        return str(file_path)

    @staticmethod
    def generate_csv_report(responses: List[Dict[str, Any]], output_filename: str) -> str:
        """Export tabular task evaluations to CSV format."""
        file_path = REPORTS_DIR / output_filename
        fieldnames = [
            "question_id", "category", "difficulty", "question_text",
            "expected_answer", "normalized_answer", "is_correct",
            "latency_ms", "estimated_cost_usd", "failure_category"
        ]
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for r in responses:
                writer.writerow(r)
        return str(file_path)

    @staticmethod
    def generate_markdown_report(evaluation_run: Dict[str, Any], output_filename: str) -> str:
        """Generate executive benchmark assessment summary in Markdown."""
        file_path = REPORTS_DIR / output_filename
        model = evaluation_run.get("model_name", "Unknown Model")
        acc = evaluation_run.get("overall_accuracy", 0.0) * 100
        lat = evaluation_run.get("avg_latency_ms", 0.0)
        cost = evaluation_run.get("total_cost_usd", 0.0)
        total = evaluation_run.get("total_tasks", 0)
        metrics = evaluation_run.get("metrics", {})

        md = f"""# VisionForge AI: Industrial Multimodal Benchmark Report
**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}  
**Model Under Test:** {model}  
**Evaluation Status:** Completed  

---

## 1. Executive Summary
- **Overall Accuracy:** {acc:.2f}% ({int(acc * total / 100)} / {total} tasks passed)
- **Mean Latency:** {lat:.2f} ms
- **Total Compute Cost:** ${cost:.6f} USD

## 2. Capability Breakdown by Question Category
| Visual Capability | Accuracy (%) | Evaluation Rigor |
|---|---|---|
| Object Identification | {metrics.get('acc_identification', 0.0) * 100:.1f}% | High |
| Component Counting | {metrics.get('acc_counting', 0.0) * 100:.1f}% | High |
| Spatial Reasoning | {metrics.get('acc_spatial', 0.0) * 100:.1f}% | High |
| Anomaly Detection | {metrics.get('acc_anomaly_detection', 0.0) * 100:.1f}% | Critical |
| Structural Relationship | {metrics.get('acc_relationship', 0.0) * 100:.1f}% | High |

## 3. Performance by Task Difficulty
| Difficulty Tier | Accuracy (%) |
|---|---|
| Easy | {metrics.get('acc_diff_easy', 0.0) * 100:.1f}% |
| Medium | {metrics.get('acc_diff_medium', 0.0) * 100:.1f}% |
| Hard | {metrics.get('acc_diff_hard', 0.0) * 100:.1f}% |

---
*Report certified by VisionForge Automated Task Validation & Benchmark Factory.*
"""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(md)
        return str(file_path)
