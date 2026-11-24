import math
from typing import Dict, Any, List, Tuple

# Supported Image Families
IMAGE_FAMILIES = {
    "smart_retail_shelf": "Smart Retail & Supermarket Shelf Inspection (Universal)",
    "mechanical_assembly": "Industrial Mechanical Assembly Workstation",
    "pcb_electronics": "High-Density SMT PCB Micro-Electronics Inspection",
    "aerospace_structural": "Aerospace Fastener & Composite Panel Array",
}

# 1. Universally Understandable Smart Retail & Supermarket Shelf Items
RETAIL_COMPONENTS = [
    "soda_can",
    "milk_carton",
    "cereal_box",
    "fresh_apple",
    "water_bottle",
    "coffee_mug",
    "snack_chips",
    "chocolate_bar",
    "juice_box"
]

# 2. Industrial Mechanical Workstation Components
MECHANICAL_COMPONENTS = [
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

# 3. PCB / Micro-Electronics Components
PCB_COMPONENTS = [
    "microcontroller_qfp",
    "smd_resistor",
    "smd_capacitor",
    "electrolytic_cap",
    "diode_sod123",
    "pin_header_8pin",
    "test_pad_array",
    "crystal_oscillator"
]

# 4. Aerospace Structural Hardware
AEROSPACE_COMPONENTS = [
    "titanium_bracket",
    "countersunk_rivet",
    "lockwire_fastener",
    "composite_panel",
    "shear_pin",
    "torque_seal_bolt"
]

ALL_COMPONENTS = RETAIL_COMPONENTS + MECHANICAL_COMPONENTS + PCB_COMPONENTS + AEROSPACE_COMPONENTS

COMPONENT_NAMES = {
    # Retail & Everyday Items (Universally Understood)
    "soda_can": "Red Cola Soda Can",
    "milk_carton": "Whole Milk Carton",
    "cereal_box": "Crispy Cereal Box",
    "fresh_apple": "Red Gala Apple",
    "water_bottle": "Spring Water Bottle",
    "coffee_mug": "Ceramic Coffee Mug",
    "snack_chips": "Potato Chips Snack Bag",
    "chocolate_bar": "Dark Chocolate Bar",
    "juice_box": "Orange Juice Box",
    "retail_shelf": "Supermarket Display Shelf",
    # Mechanical
    "spur_gear": "Drive Spur Gear 40T",
    "hex_bolt": "M8 Hex Flange Bolt",
    "hex_nut": "M8 Hex Locking Nut",
    "mounting_plate": "Machined Base Plate",
    "industrial_connector": "Multi-Pin Industrial Connector",
    "electrical_connector": "DIN Rail Electrical Terminal",
    "pipe": "Hydraulic Pressure Pipe",
    "bracket": "90-Degree Gusseted Bracket",
    "fastener": "Retaining Circlip Fastener",
    "assembly_fixture": "Precision Holding Fixture",
    # PCB Electronics
    "microcontroller_qfp": "QFP-32 Microcontroller IC",
    "smd_resistor": "SMD 0805 Precision Resistor",
    "smd_capacitor": "SMD 0805 Ceramic Capacitor",
    "electrolytic_cap": "Aluminum Electrolytic Capacitor",
    "diode_sod123": "Schottky Rectifier Diode",
    "pin_header_8pin": "2x4 Gold-Plated Header",
    "test_pad_array": "Gold Test Pad Matrix",
    "crystal_oscillator": "Surface Mount Crystal Oscillator",
    # Aerospace
    "titanium_bracket": "Ti-6Al-4V Structural L-Bracket",
    "countersunk_rivet": "Countersunk Solid Shear Rivet",
    "lockwire_fastener": "Drilled Head Safety Lockwire Bolt",
    "composite_panel": "Carbon-Fiber Composite Stiffener",
    "shear_pin": "Hardened Alloy Shear Dowel Pin",
    "torque_seal_bolt": "Torque-Sealed Inspection Bolt"
}

DEFAULT_DIMENSIONS = {
    # Retail items
    "soda_can": {"radius": 24, "height": 65, "width": 48},
    "milk_carton": {"width": 55, "height": 95},
    "cereal_box": {"width": 80, "height": 115},
    "fresh_apple": {"radius": 26},
    "water_bottle": {"width": 38, "height": 95, "cap_radius": 10},
    "coffee_mug": {"width": 56, "height": 52, "radius": 26},
    "snack_chips": {"width": 68, "height": 90},
    "chocolate_bar": {"width": 75, "height": 40},
    "juice_box": {"width": 46, "height": 72},
    "retail_shelf": {"width": 580, "height": 380},
    # Mechanical
    "spur_gear": {"radius": 55, "teeth": 16, "bore_radius": 15},
    "hex_bolt": {"radius": 18, "head_radius": 18, "flange_radius": 24},
    "hex_nut": {"radius": 20, "bore_radius": 11},
    "mounting_plate": {"width": 260, "height": 180, "hole_radius": 8},
    "industrial_connector": {"width": 110, "height": 60, "pins": 8},
    "electrical_connector": {"width": 90, "height": 50, "slots": 6},
    "pipe": {"length": 180, "diameter": 28, "flange_width": 42},
    "bracket": {"width": 70, "height": 70, "thickness": 18},
    "fastener": {"radius": 22, "gap_angle_deg": 40},
    "assembly_fixture": {"width": 140, "height": 90, "slot_width": 50},
    # PCB
    "microcontroller_qfp": {"width": 74, "height": 74, "pin_count": 32},
    "smd_resistor": {"width": 36, "height": 20},
    "smd_capacitor": {"width": 36, "height": 20},
    "electrolytic_cap": {"radius": 24},
    "diode_sod123": {"width": 40, "height": 22},
    "pin_header_8pin": {"width": 80, "height": 40, "pins": 8},
    "test_pad_array": {"width": 60, "height": 40},
    "crystal_oscillator": {"width": 55, "height": 34},
    # Aerospace
    "titanium_bracket": {"width": 75, "height": 75, "thickness": 20},
    "countersunk_rivet": {"radius": 15},
    "lockwire_fastener": {"radius": 20},
    "composite_panel": {"width": 280, "height": 190},
    "shear_pin": {"radius": 12, "length": 50},
    "torque_seal_bolt": {"radius": 19}
}

# Material & Color Palettes
MATERIAL_PALETTES = {
    "retail_cola": {
        "base": (220, 38, 38),       # Vibrant Red
        "highlight": (254, 202, 202), # Specular Top
        "shadow": (153, 27, 27),
        "outline": (69, 10, 10),
    },
    "retail_milk": {
        "base": (240, 248, 255),      # Clean White/Blue
        "highlight": (255, 255, 255),
        "shadow": (200, 220, 245),
        "outline": (30, 64, 175),
    },
    "retail_cereal": {
        "base": (245, 158, 11),       # Warm Yellow / Orange
        "highlight": (254, 240, 138),
        "shadow": (180, 83, 9),
        "outline": (120, 53, 15),
    },
    "retail_apple": {
        "base": (239, 68, 68),        # Fresh Apple Red
        "highlight": (252, 165, 165),
        "shadow": (185, 28, 28),
        "outline": (127, 29, 29),
        "leaf": (34, 197, 94)
    },
    "retail_water": {
        "base": (56, 189, 248),       # Crisp Aqua Blue
        "highlight": (224, 242, 254),
        "shadow": (2, 132, 199),
        "outline": (7, 89, 133),
    },
    "retail_mug": {
        "base": (241, 245, 249),      # Ceramic Slate White
        "highlight": (255, 255, 255),
        "shadow": (148, 163, 184),
        "outline": (71, 85, 105),
        "coffee": (66, 32, 6)
    },
    "retail_chips": {
        "base": (16, 185, 129),       # Emerald Green Bag
        "highlight": (167, 243, 208),
        "shadow": (4, 120, 87),
        "outline": (6, 78, 59),
    },
    "retail_chocolate": {
        "base": (120, 53, 15),        # Rich Chocolate Brown
        "highlight": (217, 119, 6),   # Gold Foil Accent
        "shadow": (69, 26, 3),
        "outline": (30, 10, 0),
    },
    "retail_juice": {
        "base": (249, 115, 22),       # Orange Juice Box
        "highlight": (254, 215, 170),
        "shadow": (194, 65, 12),
        "outline": (124, 45, 18),
    },
    "machined_steel": {
        "base": (170, 182, 198),
        "highlight": (240, 245, 255),
        "shadow": (95, 110, 130),
        "outline": (45, 55, 75),
    },
    "brass": {
        "base": (217, 168, 62),
        "highlight": (255, 228, 140),
        "shadow": (155, 110, 30),
        "outline": (100, 70, 15),
    },
    "black_oxide": {
        "base": (55, 62, 75),
        "highlight": (115, 125, 140),
        "shadow": (28, 34, 45),
        "outline": (15, 20, 30),
    },
    "anodized_aluminum": {
        "base": (150, 165, 185),
        "highlight": (245, 248, 255),
        "shadow": (75, 90, 110),
        "outline": (35, 45, 60),
    },
    "copper": {
        "base": (217, 119, 30),
        "highlight": (255, 195, 80),
        "shadow": (170, 75, 15),
        "outline": (110, 45, 10),
    },
    "pcb_solder_mask": {
        "base": (16, 85, 48),
        "highlight": (22, 115, 65),
        "shadow": (10, 55, 32),
        "outline": (10, 45, 25),
        "trace": (30, 140, 80),
        "gold_pad": (234, 179, 8)
    },
    "composite_weave": {
        "base": (35, 38, 45),
        "highlight": (60, 65, 75),
        "shadow": (20, 22, 28),
        "outline": (12, 14, 18)
    }
}

def compute_polygon_bounds(points: List[Tuple[float, float]]) -> List[float]:
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return [round(min(xs), 2), round(min(ys), 2), round(max(xs), 2), round(max(ys), 2)]

def rotate_point(cx: float, cy: float, x: float, y: float, angle_rad: float) -> Tuple[float, float]:
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    dx = x - cx
    dy = y - cy
    rx = cx + dx * cos_a - dy * sin_a
    ry = cy + dx * sin_a + dy * cos_a
    return (rx, ry)

def get_regular_polygon_vertices(cx: float, cy: float, radius: float, sides: int, rotation_rad: float = 0.0) -> List[Tuple[float, float]]:
    vertices = []
    angle_step = (2 * math.pi) / sides
    for i in range(sides):
        angle = rotation_rad + i * angle_step
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        vertices.append((x, y))
    return vertices

def get_gear_teeth_vertices(cx: float, cy: float, pitch_radius: float, teeth: int, tooth_depth: float, rotation_rad: float = 0.0) -> List[Tuple[float, float]]:
    vertices = []
    outer_radius = pitch_radius + tooth_depth / 2
    root_radius = pitch_radius - tooth_depth / 2
    steps = teeth * 4
    angle_step = (2 * math.pi) / steps

    for i in range(steps):
        angle = rotation_rad + i * angle_step
        step_mod = i % 4
        r = outer_radius if step_mod in (0, 1) else root_radius
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        vertices.append((x, y))
    return vertices
