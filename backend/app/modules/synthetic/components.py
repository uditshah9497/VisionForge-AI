import math
from typing import Dict, Any, List, Tuple

# Industrial Component Type Definitions & Geometries

COMPONENT_TYPES = [
    "spur_gear",
    "hex_bolt",
    "hex_nut",
    "mounting_plate",
    "industrial_connector",
    "electrical_connector",
    "pipe",
    "bracket",
    "fastener",
    "assembly_fixture",
]

COMPONENT_NAMES = {
    "spur_gear": "Drive Spur Gear",
    "hex_bolt": "M8 Hex Flange Bolt",
    "hex_nut": "M8 Hex Locking Nut",
    "mounting_plate": "Machined Base Plate",
    "industrial_connector": "Multi-Pin Industrial Connector",
    "electrical_connector": "DIN Rail Electrical Terminal",
    "pipe": "Hydraulic Pressure Pipe",
    "bracket": "90-Degree Gusseted Bracket",
    "fastener": "Retaining Circlip Fastener",
    "assembly_fixture": "Precision Holding Fixture",
}

# Standard dimensions in pixels
DEFAULT_DIMENSIONS = {
    "spur_gear": {"radius": 55, "teeth": 16, "bore_radius": 15},
    "hex_bolt": {"radius": 18, "head_radius": 18, "flange_radius": 24},
    "hex_nut": {"radius": 20, "bore_radius": 11},
    "mounting_plate": {"width": 260, "height": 180, "hole_radius": 8},
    "industrial_connector": {"width": 110, "height": 60, "pins": 8},
    "electrical_connector": {"width": 90, "height": 50, "slots": 6},
    "pipe": {"length": 180, "diameter": 26, "flange_width": 40},
    "bracket": {"width": 70, "height": 70, "thickness": 18},
    "fastener": {"radius": 22, "gap_angle_deg": 40},
    "assembly_fixture": {"width": 140, "height": 90, "slot_width": 50},
}

# Color palettes (realistic industrial metals & polymers)
MATERIAL_PALETTES = {
    "machined_steel": {
        "base": (160, 174, 192),
        "highlight": (226, 232, 240),
        "shadow": (100, 116, 139),
        "outline": (51, 65, 85)
    },
    "brass": {
        "base": (217, 168, 62),
        "highlight": (250, 218, 122),
        "shadow": (161, 117, 32),
        "outline": (107, 76, 18)
    },
    "black_oxide": {
        "base": (55, 65, 81),
        "highlight": (107, 114, 128),
        "shadow": (31, 41, 55),
        "outline": (17, 24, 39)
    },
    "anodized_aluminum": {
        "base": (148, 163, 184),
        "highlight": (241, 245, 249),
        "shadow": (71, 85, 105),
        "outline": (30, 41, 59)
    },
    "copper": {
        "base": (217, 119, 6),
        "highlight": (251, 191, 36),
        "shadow": (180, 83, 9),
        "outline": (120, 53, 15)
    },
    "industrial_plastic": {
        "base": (30, 58, 138),  # Industrial Navy
        "highlight": (96, 165, 250),
        "shadow": (30, 64, 175),
        "outline": (15, 23, 42)
    }
}

def compute_polygon_bounds(points: List[Tuple[float, float]]) -> List[float]:
    """Calculate [x_min, y_min, x_max, y_max] from vertex points."""
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return [round(min(xs), 2), round(min(ys), 2), round(max(xs), 2), round(max(ys), 2)]

def rotate_point(cx: float, cy: float, x: float, y: float, angle_rad: float) -> Tuple[float, float]:
    """Rotate point (x, y) around center (cx, cy) by angle in radians."""
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    dx = x - cx
    dy = y - cy
    rx = cx + dx * cos_a - dy * sin_a
    ry = cy + dx * sin_a + dy * cos_a
    return (rx, ry)

def get_regular_polygon_vertices(cx: float, cy: float, radius: float, sides: int, rotation_rad: float = 0.0) -> List[Tuple[float, float]]:
    """Generate vertices for a regular polygon (e.g. hexagon)."""
    vertices = []
    angle_step = (2 * math.pi) / sides
    for i in range(sides):
        angle = rotation_rad + i * angle_step
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        vertices.append((x, y))
    return vertices

def get_gear_teeth_vertices(cx: float, cy: float, pitch_radius: float, teeth: int, tooth_depth: float, rotation_rad: float = 0.0) -> List[Tuple[float, float]]:
    """Generate realistic gear profile with outer and root radii."""
    vertices = []
    outer_radius = pitch_radius + tooth_depth / 2
    root_radius = pitch_radius - tooth_depth / 2
    steps = teeth * 4
    angle_step = (2 * math.pi) / steps

    for i in range(steps):
        angle = rotation_rad + i * angle_step
        step_mod = i % 4
        # 0: tooth tip start, 1: tooth tip end, 2: root start, 3: root end
        r = outer_radius if step_mod in (0, 1) else root_radius
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        vertices.append((x, y))
    return vertices
