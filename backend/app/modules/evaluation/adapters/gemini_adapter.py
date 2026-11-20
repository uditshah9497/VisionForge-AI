import base64
import time
import httpx
from typing import Dict, Any, Optional
from backend.app.modules.evaluation.adapters.base import BaseModelAdapter

class GeminiAdapter(BaseModelAdapter):
    """Google Gemini Multimodal API Adapter."""

    def __init__(self, model_name: str = "gemini-1.5-pro", api_key: Optional[str] = None):
        super().__init__(model_name, api_key)
        self.is_demo = False

    def evaluate(self, image_path: str, question_text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not configured.")

        # Read and encode image to base64
        with open(image_path, "rb") as f:
            b64_image = base64.b64encode(f.read()).decode("utf-8")

        prompt = f"""You are evaluating an industrial manufacturing assembly workstation.
Carefully examine the image to answer the question.
Provide a concise, direct answer at the end on a new line prefixed with 'Answer:'.

Question: {question_text}
"""

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": "image/png",
                                "data": b64_image
                            }
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.0,
                "maxOutputTokens": 256
            }
        }

        start_time = time.perf_counter()
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        candidates = data.get("candidates", [])
        raw_text = ""
        if candidates and "content" in candidates[0]:
            parts = candidates[0]["content"].get("parts", [])
            raw_text = "".join(p.get("text", "") for p in parts)

        usage = data.get("usageMetadata", {})
        prompt_tokens = usage.get("promptTokenCount", 0)
        completion_tokens = usage.get("candidatesTokenCount", 0)

        # Estimated Gemini 1.5 Pro pricing ($3.50/1M input, $10.50/1M output)
        cost = (prompt_tokens * 3.5e-6) + (completion_tokens * 10.5e-6)

        return {
            "raw_response": raw_text.strip(),
            "latency_ms": latency_ms,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "estimated_cost_usd": round(cost, 6),
            "is_demo": False
        }
