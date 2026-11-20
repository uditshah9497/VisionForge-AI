import base64
import time
import httpx
from typing import Dict, Any, Optional
from backend.app.modules.evaluation.adapters.base import BaseModelAdapter

class OpenAIAdapter(BaseModelAdapter):
    """OpenAI GPT-4o Vision API Adapter."""

    def __init__(self, model_name: str = "gpt-4o", api_key: Optional[str] = None):
        super().__init__(model_name, api_key)
        self.is_demo = False

    def evaluate(self, image_path: str, question_text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not configured.")

        with open(image_path, "rb") as f:
            b64_image = base64.b64encode(f.read()).decode("utf-8")

        prompt = f"""You are evaluating an industrial manufacturing assembly workstation.
Examine the image carefully and answer the question.
Provide a concise, direct answer at the end on a new line prefixed with 'Answer:'.

Question: {question_text}
"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{b64_image}"}
                        }
                    ]
                }
            ],
            "temperature": 0.0,
            "max_tokens": 256
        }

        start_time = time.perf_counter()
        with httpx.Client(timeout=30.0) as client:
            resp = client.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        raw_text = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)

        # GPT-4o pricing: $5.00/1M input, $15.00/1M output
        cost = (prompt_tokens * 5.0e-6) + (completion_tokens * 15.0e-6)

        return {
            "raw_response": raw_text.strip(),
            "latency_ms": latency_ms,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "estimated_cost_usd": round(cost, 6),
            "is_demo": False
        }
