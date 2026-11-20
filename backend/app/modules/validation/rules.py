import os
import re
from typing import Dict, Any, List, Tuple
from PIL import Image

def validate_image_readable(image_path: str, expected_w: int = 800, expected_h: int = 600) -> Tuple[bool, str]:
    if not image_path or not os.path.exists(image_path):
        return False, f"Image file does not exist on disk: {image_path}"
    if os.path.getsize(image_path) < 100:
        return False, "Image file is empty or corrupted (size < 100 bytes)"
    try:
        with Image.open(image_path) as img:
            img.verify()
        with Image.open(image_path) as img:
            w, h = img.size
            if w != expected_w or h != expected_h:
                return False, f"Image dimension mismatch: got ({w}, {h}), expected ({expected_w}, {expected_h})"
    except Exception as e:
        return False, f"Pillow failed to decode image: {str(e)}"
    return True, "Image is readable and valid"

def validate_scene_graph_consistency(scene_graph: Dict[str, Any]) -> Tuple[bool, str]:
    if not isinstance(scene_graph, dict):
        return False, "Scene graph is not a valid dictionary"
    components = scene_graph.get("components", [])
    if not components or len(components) < 2:
        return False, f"Scene graph contains insufficient components ({len(components)})"

    ids = [c.get("id") for c in components]
    if len(ids) != len(set(ids)):
        return False, "Duplicate component IDs found in scene graph"

    for c in components:
        if not c.get("id") or not c.get("type"):
            return False, "Component missing required 'id' or 'type'"
        if "center" not in c or "bbox" not in c:
            return False, f"Component {c.get('id')} missing 'center' or 'bbox'"
    return True, "Scene graph is structurally consistent"

def validate_bounding_boxes(scene_graph: Dict[str, Any], width: int = 800, height: int = 600) -> Tuple[bool, str]:
    components = scene_graph.get("components", [])
    for c in components:
        bbox = c.get("bbox", [])
        if len(bbox) != 4:
            return False, f"Component {c.get('id')} has invalid bbox length {len(bbox)}"
        x1, y1, x2, y2 = bbox
        if x2 <= x1 or y2 <= y1:
            return False, f"Component {c.get('id')} has non-positive area bbox: [{x1}, {y1}, {x2}, {y2}]"
        if x1 < 0 or y1 < 0 or x2 > width + 10 or y2 > height + 10:
            return False, f"Component {c.get('id')} bbox [{x1}, {y1}, {x2}, {y2}] exceeds canvas bounds ({width}x{height})"
    return True, "All bounding boxes are valid and within canvas"

def validate_visual_evidence(question: Dict[str, Any], scene_graph: Dict[str, Any]) -> Tuple[bool, str]:
    supporting_ids = question.get("supporting_component_ids", [])
    components = {c["id"]: c for c in scene_graph.get("components", [])}

    for cid in supporting_ids:
        if cid not in components:
            return False, f"Supporting component '{cid}' not found in scene graph"
        comp = components[cid]
        # If component is missing defect, its expected socket is visible, so that's valid evidence
        if comp.get("defect_type") == "missing":
            continue
        # Otherwise verify visibility score and minimum area
        vis = comp.get("visibility_score", 1.0)
        if vis < 0.25:
            return False, f"Component '{cid}' has insufficient visibility ({vis:.2f}) to reliably answer question"
        bbox = comp.get("bbox", [0, 0, 0, 0])
        area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
        if area < 100:
            return False, f"Component '{cid}' pixel area ({area:.1f} px) is too small for visual inspection"
    return True, "Visual evidence is sufficient for question resolution"

def validate_answer_determinism(question: Dict[str, Any]) -> Tuple[bool, str]:
    ans = question.get("expected_answer")
    atype = question.get("answer_type", "text")
    if ans is None or str(ans).strip() in ("", "unknown", "none_found"):
        return False, "Expected answer is undefined or empty"
    if atype == "integer":
        try:
            int(ans)
        except ValueError:
            return False, f"Expected answer '{ans}' does not parse as integer"
    elif atype == "boolean":
        if str(ans).lower() not in ("yes", "no", "true", "false"):
            return False, f"Expected boolean answer '{ans}' is invalid"
    return True, "Answer is deterministic and conforms to declared type"

def validate_question_clarity(question: Dict[str, Any]) -> Tuple[bool, str]:
    text = question.get("question_text", "")
    if len(text.strip()) < 15:
        return False, "Question text is too short (< 15 characters)"
    if re.search(r"\{[a-zA-Z0-9_]+\}", text):
        return False, f"Question text contains unpopulated template variable: {text}"
    return True, "Question text is clear and unambiguous"
