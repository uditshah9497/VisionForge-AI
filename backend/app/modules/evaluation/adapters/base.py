from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseModelAdapter(ABC):
    """Abstract base class for multimodal model adapters."""

    def __init__(self, model_name: str, api_key: Optional[str] = None):
        self.model_name = model_name
        self.api_key = api_key
        self.is_demo = False

    @abstractmethod
    def evaluate(self, image_path: str, question_text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Evaluate a multimodal query.

        Returns dict containing:
        - raw_response: str
        - latency_ms: float
        - prompt_tokens: int
        - completion_tokens: int
        - estimated_cost_usd: float
        - is_demo: bool
        """
        pass
