import re
from typing import Tuple, Optional

NUMBER_WORDS = {
    "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
    "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10"
}

def normalize_model_response(
    raw_response: str,
    expected_answer: str,
    answer_type: str = "text"
) -> Tuple[str, bool, Optional[str]]:
    """Normalize raw multimodal text output and evaluate correctness against expected ground truth.

    Returns: (normalized_answer, is_correct, failure_category)
    """
    if not raw_response or not raw_response.strip():
        return "", False, "unparseable"

    text = raw_response.strip()

    # 1. Search for explicit "Answer:" or "The answer is" prefix
    answer_match = re.search(r"(?:answer|result)\s*(?::|is)\s*(.*)", text, re.IGNORECASE)
    if answer_match:
        extracted = answer_match.group(1).strip()
    else:
        # Fallback to the last line of response
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        extracted = lines[-1] if lines else text

    # Strip markdown bolding, backticks, quotes, and punctuation
    cleaned = re.sub(r"[\*`\"'\_]", "", extracted).strip()
    cleaned = re.sub(r"[\.\,\;]$", "", cleaned).strip().lower()

    norm_expected = str(expected_answer).strip().lower()

    if answer_type == "integer":
        # Extract first number or word number
        # Check word numbers first
        for word, digit in NUMBER_WORDS.items():
            if re.search(rf"\b{word}\b", cleaned):
                cleaned = digit
                break
        digits = re.findall(r"\d+", cleaned)
        if digits:
            norm_ans = digits[0]
            is_correct = (norm_ans == norm_expected)
            failure = None if is_correct else "incorrect_value"
            return norm_ans, is_correct, failure
        else:
            return cleaned, False, "unparseable"

    elif answer_type == "boolean":
        if re.search(r"\b(yes|true|correct|present)\b", cleaned):
            norm_ans = "yes"
        elif re.search(r"\b(no|false|incorrect|absent)\b", cleaned):
            norm_ans = "no"
        else:
            return cleaned, False, "unparseable"

        is_correct = (norm_ans == norm_expected)
        failure = None if is_correct else "incorrect_value"
        return norm_ans, is_correct, failure

    elif answer_type == "category":
        # Check substring match or word boundary match
        is_correct = (norm_expected in cleaned) or (cleaned in norm_expected)
        failure = None if is_correct else "incorrect_value"
        return cleaned, is_correct, failure

    # Default text comparison
    is_correct = (cleaned == norm_expected)
    failure = None if is_correct else "incorrect_value"
    return cleaned, is_correct, failure
