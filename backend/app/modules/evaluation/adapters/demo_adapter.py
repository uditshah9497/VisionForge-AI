import random
import time
from typing import Dict, Any, Optional
from backend.app.modules.evaluation.adapters.base import BaseModelAdapter

class DemoAdapter(BaseModelAdapter):
    """Calibrated offline demo adapter for local development and testing without API keys.

    Clearly tagged with is_demo = True. Simulates frontier vision model failure modes:
    - Object identification: high accuracy (~88%)
    - Counting under partial occlusion: lower accuracy (~65%)
    - Anomaly detection: moderate accuracy (~75%)
    - Spatial reasoning: moderate accuracy (~72%)
    """

    def __init__(self, model_name: str = "visionforge-demo-v1"):
        super().__init__(model_name=model_name, api_key=None)
        self.is_demo = True

    def evaluate(self, image_path: str, question_text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        # Realistic latency simulation (120ms to 380ms)
        start_time = time.perf_counter()
        time.sleep(random.uniform(0.08, 0.22))
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        expected_answer = ""
        category = "identification"
        if context:
            expected_answer = str(context.get("expected_answer", ""))
            category = context.get("category", "identification")

        # Category-calibrated accuracy simulation
        category_accuracies = {
            "identification": 0.88,
            "counting": 0.68,
            "spatial": 0.74,
            "anomaly_detection": 0.72,
            "relationship": 0.78
        }
        target_acc = category_accuracies.get(category, 0.75)
        is_success = random.random() < target_acc

        if is_success:
            answer = expected_answer
            reasoning = f"Based on visual analysis of the assembly fixture, {expected_answer} is clearly visible."
        else:
            # Simulate characteristic multimodal failure
            if category == "counting":
                # Off-by-one counting error
                try:
                    val = int(expected_answer)
                    answer = str(val + random.choice([-1, 1]))
                except ValueError:
                    answer = "0"
                reasoning = "I count the visible fasteners, but one appears partially occluded near the edge."
            elif category == "anomaly_detection":
                answer = "no" if expected_answer == "yes" else "yes"
                reasoning = "Visual inspection indicates normal assembly seating with no obvious displacement."
            elif category == "spatial":
                answer = "right" if expected_answer == "left" else "left"
                reasoning = "Checking the coordinates relative to the base fixture."
            else:
                answer = "unspecified"
                reasoning = "The component boundary is indistinct against the workstation table."

        raw_response = f"{reasoning}\nAnswer: {answer}"

        return {
            "raw_response": raw_response,
            "latency_ms": latency_ms,
            "prompt_tokens": random.randint(420, 580),
            "completion_tokens": random.randint(30, 65),
            "estimated_cost_usd": 0.0,
            "is_demo": True
        }
