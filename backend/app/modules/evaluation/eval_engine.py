import uuid
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from backend.app.modules.evaluation.adapters.base import BaseModelAdapter
from backend.app.modules.evaluation.adapters.gemini_adapter import GeminiAdapter
from backend.app.modules.evaluation.adapters.openai_adapter import OpenAIAdapter
from backend.app.modules.evaluation.adapters.anthropic_adapter import AnthropicAdapter
from backend.app.modules.evaluation.adapters.demo_adapter import DemoAdapter
from backend.app.modules.evaluation.normalizer import normalize_model_response
from backend.app.core.config import GEMINI_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY

def get_adapter_for_model(provider: str, model_name: str) -> BaseModelAdapter:
    """Factory to instantiate the appropriate multimodal model adapter."""
    p = provider.lower()
    if p == "gemini":
        if not GEMINI_API_KEY:
            # Fall back to demo with clear labeling
            return DemoAdapter(model_name=f"demo-{model_name} (No API key)")
        return GeminiAdapter(model_name=model_name, api_key=GEMINI_API_KEY)
    elif p == "openai":
        if not OPENAI_API_KEY:
            return DemoAdapter(model_name=f"demo-{model_name} (No API key)")
        return OpenAIAdapter(model_name=model_name, api_key=OPENAI_API_KEY)
    elif p == "anthropic":
        if not ANTHROPIC_API_KEY:
            return DemoAdapter(model_name=f"demo-{model_name} (No API key)")
        return AnthropicAdapter(model_name=model_name, api_key=ANTHROPIC_API_KEY)
    else:
        return DemoAdapter(model_name=model_name or "visionforge-demo-v1")

class EvaluationEngine:
    """Orchestrates benchmark evaluation runs across multimodal models."""

    @staticmethod
    def run_benchmark(
        tasks: List[Dict[str, Any]],
        provider: str = "demo",
        model_name: str = "visionforge-demo-v1"
    ) -> Dict[str, Any]:
        """Execute evaluation for a list of validated tasks.

        tasks: List of dicts, each with keys:
          - question_id
          - category
          - difficulty
          - question_text
          - expected_answer
          - answer_type
          - image_path
        """
        adapter = get_adapter_for_model(provider, model_name)
        run_id = f"run_{uuid.uuid4().hex[:8]}"
        started_at = datetime.now(timezone.utc).isoformat()

        responses = []
        total_latency = 0.0
        total_cost = 0.0

        for task in tasks:
            img_path = task.get("image_path", "")
            q_text = task.get("question_text", "")
            expected = task.get("expected_answer", "")
            atype = task.get("answer_type", "text")
            cat = task.get("category", "identification")

            context = {
                "expected_answer": expected,
                "category": cat,
                "difficulty": task.get("difficulty", "medium")
            }

            try:
                eval_res = adapter.evaluate(img_path, q_text, context=context)
                raw = eval_res["raw_response"]
                lat = eval_res["latency_ms"]
                cost = eval_res["estimated_cost_usd"]
                p_tokens = eval_res["prompt_tokens"]
                c_tokens = eval_res["completion_tokens"]
            except Exception as e:
                raw = f"API Evaluation Error: {str(e)}"
                lat = 0.0
                cost = 0.0
                p_tokens = 0
                c_tokens = 0

            norm_ans, is_correct, failure = normalize_model_response(raw, expected, atype)

            total_latency += lat
            total_cost += cost

            responses.append({
                "question_id": task.get("question_id"),
                "category": cat,
                "difficulty": task.get("difficulty", "medium"),
                "question_text": q_text,
                "expected_answer": expected,
                "raw_response": raw,
                "normalized_answer": norm_ans,
                "is_correct": is_correct,
                "latency_ms": lat,
                "prompt_tokens": p_tokens,
                "completion_tokens": c_tokens,
                "estimated_cost_usd": cost,
                "failure_category": failure
            })

        # Calculate Aggregate Metrics
        total_tasks = len(responses)
        correct_tasks = sum(1 for r in responses if r["is_correct"])
        overall_acc = round(correct_tasks / total_tasks, 4) if total_tasks > 0 else 0.0
        avg_lat = round(total_latency / total_tasks, 2) if total_tasks > 0 else 0.0

        # Category breakdowns
        metrics: Dict[str, float] = {
            "overall_accuracy": overall_acc,
            "average_latency_ms": avg_lat,
            "total_cost_usd": round(total_cost, 6)
        }

        # Metrics by category
        categories = set(r["category"] for r in responses)
        for c in categories:
            cat_res = [r for r in responses if r["category"] == c]
            c_acc = sum(1 for r in cat_res if r["is_correct"]) / len(cat_res) if cat_res else 0.0
            metrics[f"acc_{c}"] = round(c_acc, 4)

        # Metrics by difficulty
        difficulties = set(r["difficulty"] for r in responses)
        for d in difficulties:
            diff_res = [r for r in responses if r["difficulty"] == d]
            d_acc = sum(1 for r in diff_res if r["is_correct"]) / len(diff_res) if diff_res else 0.0
            metrics[f"acc_diff_{d}"] = round(d_acc, 4)

        completed_at = datetime.now(timezone.utc).isoformat()

        return {
            "run_id": run_id,
            "model_name": adapter.model_name,
            "model_provider": provider,
            "is_demo": adapter.is_demo,
            "total_tasks": total_tasks,
            "evaluated_tasks": total_tasks,
            "overall_accuracy": overall_acc,
            "avg_latency_ms": avg_lat,
            "total_cost_usd": round(total_cost, 6),
            "metrics": metrics,
            "responses": responses,
            "started_at": started_at,
            "completed_at": completed_at,
            "status": "completed"
        }
