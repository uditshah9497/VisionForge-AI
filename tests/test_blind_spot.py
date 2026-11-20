import os
import pytest
from backend.app.modules.adversarial.blind_spot import BlindSpotEngine

def test_blind_spot_generation():
    engine = BlindSpotEngine()
    result = engine.generate_blind_spot_test(
        base_seed=100,
        perturbation_type="component_removed",
        provider="demo"
    )

    assert result is not None
    assert "id" in result
    assert result["property_changed"] == "component_removed"
    assert "original_image_path" in result
    assert "modified_image_path" in result
    assert os.path.exists(result["original_image_path"])
    assert os.path.exists(result["modified_image_path"])
    assert result["original_expected_answer"] != result["modified_expected_answer"]
    assert "is_blind_spot" in result
