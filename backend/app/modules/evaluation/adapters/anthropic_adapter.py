import base64
import time
import httpx
from typing import Dict, Any, Optional
from backend.app.modules.evaluation.adapters.base import BaseModelAdapter

class AnthropicAdapter(BaseModelAdapter):
    """Anthropic Claude 3.5 Sonnet Vision Adapter."""

    def __init__(self, model_name: str = "claude-3-5-sonnet-20241022", api_key: Optional[str] = None):
        super().__init__(model_name, api_key)
        self.is_demo = False

    def evaluate(self, image_path: str, question_text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY is not configured.")

        with open(image_path, "rb") as f:
            b64_image = base64.b64encode(f.read()).decode("utf-8")

        prompt = f"""Examine this industrial workstation image carefully and answer the question.
Provide a concise, direct answer at the end on a new line prefixed with 'Answer:'.

Question: {question_text}
"""

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        payload = {
            "model": self.model_name,
            "max_tokens": 256,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": b64_image
                            }
                        },
                        {"type": "text", "text": prompt}
                    ]
                }
            ]
        }

        start_time = time.perf_counter()
        with httpx.Client(timeout=30.0) as client:
            resp = client.post("https://api.anthropic.com/v1/messages", json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        raw_text = "".join(b.get("text", "") for b in data.get("content", []))
        usage = data.get("usage", {})
        prompt_tokens = usage.get("input_tokens", 0)
        completion_tokens = usage.get("output_tokens", 0)

        # Claude 3.5 Sonnet pricing: $3.00/1M input, $15.00/1M output
        cost = (prompt_tokens * 3.0e-6) + (completion_tokens * 15.0e-6)

        return {
            "raw_response": raw_text.strip(),
            "latency_ms": latency_ms,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "estimated_cost_usd": round(cost, 6),
            "is_demo": False
        }
