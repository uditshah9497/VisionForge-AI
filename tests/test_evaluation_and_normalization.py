import pytest
from backend.app.modules.evaluation.normalizer import normalize_model_response
from backend.app.modules.evaluation.adapters.demo_adapter import DemoAdapter

def test_normalizer_integer_extraction():
    ans, ok, fail = normalize_model_response("The total count of bolts is 3.", "3", "integer")
    assert ans == "3"
    assert ok is True
    assert fail is None

    # Word number extraction
    ans_word, ok_word, _ = normalize_model_response("There are two fasteners present.", "2", "integer")
    assert ans_word == "2"
    assert ok_word is True

def test_normalizer_boolean_extraction():
    ans, ok, fail = normalize_model_response("Yes, the bracket is mounted properly.", "yes", "boolean")
    assert ans == "yes"
    assert ok is True
    assert fail is None

    ans_no, ok_no, _ = normalize_model_response("No, the component appears displaced.", "no", "boolean")
    assert ans_no == "no"
    assert ok_no is True

def test_normalizer_unparseable_distinction():
    """Verify that an unparseable response is distinguished from an incorrect value."""
    ans, ok, fail = normalize_model_response("I cannot determine anything from this image.", "4", "integer")
    assert ok is False
    assert fail == "unparseable"

    ans2, ok2, fail2 = normalize_model_response("Answer: 5", "3", "integer")
    assert ok2 is False
    assert fail2 == "incorrect_value"

def test_demo_adapter_evaluation():
    adapter = DemoAdapter()
    res = adapter.evaluate(
        image_path="",
        question_text="How many hex bolts are on the workstation?",
        context={"expected_answer": "3", "category": "counting"}
    )
    assert res["is_demo"] is True
    assert "raw_response" in res
    assert res["latency_ms"] > 0
    assert "Answer:" in res["raw_response"]
