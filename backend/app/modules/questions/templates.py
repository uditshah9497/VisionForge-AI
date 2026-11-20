from typing import Dict, Any, List

QUESTION_TEMPLATES = {
    "identification": [
        {
            "id": "ident_type_at_pos",
            "difficulty": "easy",
            "template": "What type of industrial component is positioned near ({x}, {y})?",
            "answer_type": "category",
            "rule": "find_component_at_coord"
        },
        {
            "id": "ident_presence",
            "difficulty": "easy",
            "template": "Is there a {component_name} present and visible on the assembly workstation?",
            "answer_type": "boolean",
            "rule": "check_component_presence"
        },
        {
            "id": "ident_material",
            "difficulty": "medium",
            "template": "What material finish or finish type does the {component_name} at ({x}, {y}) appear to have?",
            "answer_type": "category",
            "rule": "get_component_material"
        }
    ],
    "counting": [
        {
            "id": "count_specific_type",
            "difficulty": "easy",
            "template": "How many {component_name}s are visible on the assembly workstation?",
            "answer_type": "integer",
            "rule": "count_visible_by_type"
        },
        {
            "id": "count_fasteners_total",
            "difficulty": "medium",
            "template": "How many total fasteners (hex bolts, hex nuts, and circlips) are visible on the workstation?",
            "answer_type": "integer",
            "rule": "count_fasteners"
        },
        {
            "id": "count_defective_components",
            "difficulty": "hard",
            "template": "How many components on the workstation exhibit defects (missing, displaced, or rotated)?",
            "answer_type": "integer",
            "rule": "count_defective"
        }
    ],
    "spatial": [
        {
            "id": "spatial_relative_dir",
            "difficulty": "easy",
            "template": "In relation to the {object_name} at ({ox}, {oy}), is the {subject_name} located to its left or to its right?",
            "answer_type": "category",
            "rule": "get_horizontal_relation"
        },
        {
            "id": "spatial_vertical_dir",
            "difficulty": "easy",
            "template": "Is the {subject_name} located above or below the {object_name}?",
            "answer_type": "category",
            "rule": "get_vertical_relation"
        },
        {
            "id": "spatial_nearest_to_fixture",
            "difficulty": "medium",
            "template": "Which component is positioned closest to the center of the base {base_name}?",
            "answer_type": "category",
            "rule": "get_closest_to_base"
        }
    ],
    "anomaly_detection": [
        {
            "id": "anomaly_missing_present",
            "difficulty": "medium",
            "template": "Is there any missing component socket or unpopulated mounting hole visible on the workstation?",
            "answer_type": "boolean",
            "rule": "check_missing_socket"
        },
        {
            "id": "anomaly_identify_defective",
            "difficulty": "hard",
            "template": "Which component exhibits an assembly defect (misplaced, missing, or incorrect orientation)?",
            "answer_type": "category",
            "rule": "identify_defective_component"
        },
        {
            "id": "anomaly_check_specific_seat",
            "difficulty": "medium",
            "template": "Is the {component_name} located at ({x}, {y}) properly positioned without misalignment?",
            "answer_type": "boolean",
            "rule": "check_component_misalignment"
        }
    ],
    "relationship": [
        {
            "id": "rel_mounted_on_base",
            "difficulty": "easy",
            "template": "Is the {component_name} at ({x}, {y}) positioned within the boundary of the base {base_name}?",
            "answer_type": "boolean",
            "rule": "check_mounted_on_base"
        },
        {
            "id": "rel_cardinal_relation",
            "difficulty": "medium",
            "template": "What is the primary spatial orientation of {subject_name} relative to {object_name} (left_of, right_of, above, below)?",
            "answer_type": "category",
            "rule": "get_primary_spatial_relation"
        }
    ]
}
