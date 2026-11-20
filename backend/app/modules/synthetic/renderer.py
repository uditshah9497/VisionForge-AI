import os
import math
import random
from typing import Dict, Any, List, Tuple
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from backend.app.modules.synthetic.components import (
    MATERIAL_PALETTES,
    get_gear_teeth_vertices,
    get_regular_polygon_vertices,
    rotate_point,
    compute_polygon_bounds
)

class SyntheticRenderer:
    """High-fidelity 2D industrial workstation image renderer using Pillow."""

    def __init__(self, width: int = 800, height: int = 600):
        self.width = width
        self.height = height

    def render_scene(self, scene_graph: Dict[str, Any], output_path: str) -> Dict[str, Any]:
        """Render a complete scene from its scene graph into a PNG image."""
        workstation = scene_graph.get("workstation", {})
        lighting = workstation.get("lighting", {})
        ambient = lighting.get("ambient", 0.75)
        direction = lighting.get("direction", "top_left")

        # Shadow offset based on lighting direction
        shadow_dx = -6 if "right" in direction else 6
        shadow_dy = -6 if "bottom" in direction else 6

        # 1. Create base canvas (dark industrial breadboard / granite surface)
        bg_color = (20, 26, 36)
        image = Image.new("RGBA", (self.width, self.height), bg_color)
        draw = ImageDraw.Draw(image)

        # 2. Render industrial optical breadboard grid (M6 tapped holes)
        grid_spacing = workstation.get("grid_spacing", 40)
        hole_radius = 3
        hole_color_base = (30, 41, 59)
        hole_highlight = (45, 55, 72)

        for x in range(grid_spacing // 2, self.width, grid_spacing):
            for y in range(grid_spacing // 2, self.height, grid_spacing):
                # Outer shadow
                draw.ellipse(
                    [x - hole_radius, y - hole_radius, x + hole_radius, y + hole_radius],
                    fill=hole_color_base,
                    outline=(15, 23, 42)
                )
                # Inner thread specular point
                draw.point((x - 1, y - 1), fill=hole_highlight)

        # 3. Create separate layers: Shadow Layer, Object Layer, Clutter Layer, Occlusion Layer
        shadow_image = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow_image)

        object_image = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        object_draw = ImageDraw.Draw(object_image)

        # Sort components by layer (base plates at layer 1, components at layer 2, etc.)
        components = sorted(scene_graph.get("components", []), key=lambda c: c.get("layer", 1))

        # First pass: Render shadows
        for comp in components:
            if comp.get("defect_type") == "missing":
                continue  # missing component doesn't cast a full shadow
            self._draw_component_shadow(shadow_draw, comp, shadow_dx, shadow_dy)

        # Apply gaussian blur to shadows for realistic diffuse industrial lighting
        shadow_image = shadow_image.filter(ImageFilter.GaussianBlur(radius=4))
        image = Image.alpha_composite(image, shadow_image)

        # Second pass: Render components
        for comp in components:
            self._draw_component(object_draw, comp, lighting)

        # Render background clutter if any (metal shavings, Allen wrench, ruler)
        if scene_graph.get("clutter"):
            self._draw_clutter(object_draw, scene_graph["clutter"])

        # Render partial occlusion overlays if any
        if scene_graph.get("occlusions"):
            self._draw_occlusions(object_draw, scene_graph["occlusions"])

        image = Image.alpha_composite(image, object_image)

        # Apply ambient lighting adjustment
        if ambient < 0.6:
            # Low lighting simulation
            overlay = Image.new("RGBA", (self.width, self.height), (0, 0, 0, int((0.6 - ambient) * 200)))
            image = Image.alpha_composite(image, overlay)

        # Ensure directory exists and save
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        final_rgb = image.convert("RGB")
        final_rgb.save(output_path, "PNG", quality=95)

        file_size = os.path.getsize(output_path)
        return {
            "output_path": output_path,
            "width": self.width,
            "height": self.height,
            "file_size_bytes": file_size,
            "format": "PNG"
        }

    def _draw_component_shadow(self, draw: ImageDraw.ImageDraw, comp: Dict[str, Any], dx: int, dy: int):
        cx = comp["center"]["x"] + dx
        cy = comp["center"]["y"] + dy
        ctype = comp["type"]
        dims = comp["dimensions"]
        shadow_color = (0, 0, 0, 110)

        if ctype in ("spur_gear", "hex_nut", "fastener"):
            r = dims.get("radius", 40)
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=shadow_color)
        elif ctype == "hex_bolt":
            r = dims.get("flange_radius", 24)
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=shadow_color)
        elif ctype in ("mounting_plate", "assembly_fixture", "industrial_connector", "electrical_connector"):
            w = dims.get("width", 100)
            h = dims.get("height", 80)
            draw.rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], fill=shadow_color)
        elif ctype == "pipe":
            l = dims.get("length", 160)
            d = dims.get("diameter", 24)
            draw.rectangle([cx - l / 2, cy - d / 2, cx + l / 2, cy + d / 2], fill=shadow_color)
        elif ctype == "bracket":
            w = dims.get("width", 60)
            h = dims.get("height", 60)
            draw.rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], fill=shadow_color)

    def _draw_component(self, draw: ImageDraw.ImageDraw, comp: Dict[str, Any], lighting: Dict[str, Any]):
        ctype = comp["type"]
        cx = comp["center"]["x"]
        cy = comp["center"]["y"]
        rot = math.radians(comp.get("rotation_deg", 0.0))
        palette = MATERIAL_PALETTES.get(comp.get("material", "machined_steel"), MATERIAL_PALETTES["machined_steel"])
        is_missing = comp.get("defect_type") == "missing"

        if is_missing:
            # Render empty socket / tapped hole with dashed or marked outline
            r = comp["dimensions"].get("radius", 20)
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(15, 23, 42, 200), outline=(239, 68, 68, 220), width=2)
            # Empty thread center
            draw.ellipse([cx - r/2, cy - r/2, cx + r/2, cy + r/2], fill=(10, 15, 26, 255))
            return

        if ctype == "spur_gear":
            self._render_spur_gear(draw, cx, cy, rot, comp["dimensions"], palette)
        elif ctype == "hex_bolt":
            self._render_hex_bolt(draw, cx, cy, rot, comp["dimensions"], palette)
        elif ctype == "hex_nut":
            self._render_hex_nut(draw, cx, cy, rot, comp["dimensions"], palette)
        elif ctype == "mounting_plate":
            self._render_mounting_plate(draw, cx, cy, rot, comp["dimensions"], palette)
        elif ctype == "industrial_connector":
            self._render_industrial_connector(draw, cx, cy, rot, comp["dimensions"], palette)
        elif ctype == "electrical_connector":
            self._render_electrical_connector(draw, cx, cy, rot, comp["dimensions"], palette)
        elif ctype == "pipe":
            self._render_pipe(draw, cx, cy, rot, comp["dimensions"], palette)
        elif ctype == "bracket":
            self._render_bracket(draw, cx, cy, rot, comp["dimensions"], palette)
        elif ctype == "fastener":
            self._render_fastener(draw, cx, cy, rot, comp["dimensions"], palette)
        elif ctype == "assembly_fixture":
            self._render_assembly_fixture(draw, cx, cy, rot, comp["dimensions"], palette)

    def _render_spur_gear(self, draw: ImageDraw.ImageDraw, cx: float, cy: float, rot: float, dims: Dict[str, Any], pal: Dict[str, Any]):
        r = dims.get("radius", 55)
        teeth = dims.get("teeth", 16)
        bore_r = dims.get("bore_radius", 15)

        # Gear teeth outer polygon
        teeth_pts = get_gear_teeth_vertices(cx, cy, r, teeth, tooth_depth=12, rotation_rad=rot)
        draw.polygon(teeth_pts, fill=pal["base"], outline=pal["outline"])

        # Inner body rim
        draw.ellipse([cx - (r - 10), cy - (r - 10), cx + (r - 10), cy + (r - 10)], fill=pal["highlight"], outline=pal["outline"])
        draw.ellipse([cx - (r - 16), cy - (r - 16), cx + (r - 16), cy + (r - 16)], fill=pal["shadow"])

        # Weight reduction holes (4 holes)
        hole_dist = r * 0.55
        for i in range(4):
            angle = rot + i * (math.pi / 2)
            hx = cx + hole_dist * math.cos(angle)
            hy = cy + hole_dist * math.sin(angle)
            draw.ellipse([hx - 7, hy - 7, hx + 7, hy + 7], fill=pal["base"], outline=pal["outline"])

        # Central axle bore + keyway notch
        draw.ellipse([cx - bore_r, cy - bore_r, cx + bore_r, cy + bore_r], fill=(20, 26, 36), outline=pal["outline"], width=2)
        keyway_w = 4
        keyway_h = 7
        draw.rectangle([cx - keyway_w, cy - bore_r - keyway_h, cx + keyway_w, cy - bore_r], fill=(20, 26, 36))

    def _render_hex_bolt(self, draw: ImageDraw.ImageDraw, cx: float, cy: float, rot: float, dims: Dict[str, Any], pal: Dict[str, Any]):
        flange_r = dims.get("flange_radius", 24)
        head_r = dims.get("head_radius", 17)

        # Circular flange with serrated rim
        draw.ellipse([cx - flange_r, cy - flange_r, cx + flange_r, cy + flange_r], fill=pal["shadow"], outline=pal["outline"], width=1)
        draw.ellipse([cx - flange_r + 2, cy - flange_r + 2, cx + flange_r - 2, cy + flange_r - 2], fill=pal["base"])

        # Hexagon head
        hex_pts = get_regular_polygon_vertices(cx, cy, head_r, 6, rotation_rad=rot)
        draw.polygon(hex_pts, fill=pal["highlight"], outline=pal["outline"])

        # Center dimple / socket
        draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=pal["shadow"], outline=pal["outline"])

    def _render_hex_nut(self, draw: ImageDraw.ImageDraw, cx: float, cy: float, rot: float, dims: Dict[str, Any], pal: Dict[str, Any]):
        r = dims.get("radius", 22)
        bore_r = dims.get("bore_radius", 11)

        # Outer Hexagon
        hex_pts = get_regular_polygon_vertices(cx, cy, r, 6, rotation_rad=rot)
        draw.polygon(hex_pts, fill=pal["base"], outline=pal["outline"])

        # Bevel ring
        draw.ellipse([cx - (r - 4), cy - (r - 4), cx + (r - 4), cy + (r - 4)], fill=pal["highlight"], outline=pal["outline"])

        # Inner threaded bore
        draw.ellipse([cx - bore_r, cy - bore_r, cx + bore_r, cy + bore_r], fill=(20, 26, 36), outline=pal["outline"], width=2)
        # Thread ridge highlights
        draw.arc([cx - bore_r + 2, cy - bore_r + 2, cx + bore_r - 2, cy + bore_r - 2], start=45, end=225, fill=pal["shadow"], width=2)

    def _render_mounting_plate(self, draw: ImageDraw.ImageDraw, cx: float, cy: float, rot: float, dims: Dict[str, Any], pal: Dict[str, Any]):
        w = dims.get("width", 260)
        h = dims.get("height", 180)
        hole_r = dims.get("hole_radius", 8)

        # Main plate body
        x1, y1 = cx - w / 2, cy - h / 2
        x2, y2 = cx + w / 2, cy + h / 2
        draw.rectangle([x1, y1, x2, y2], fill=pal["shadow"], outline=pal["outline"], width=2)
        # Beveled interior face
        draw.rectangle([x1 + 4, y1 + 4, x2 - 4, y2 - 4], fill=pal["base"])
        # Specular top edge
        draw.line([x1 + 4, y1 + 4, x2 - 4, y1 + 4], fill=pal["highlight"], width=2)

        # 4 Corner mounting holes
        inset = 24
        hole_coords = [
            (x1 + inset, y1 + inset),
            (x2 - inset, y1 + inset),
            (x1 + inset, y2 - inset),
            (x2 - inset, y2 - inset),
        ]
        for hx, hy in hole_coords:
            draw.ellipse([hx - hole_r, hy - hole_r, hx + hole_r, hy + hole_r], fill=(20, 26, 36), outline=pal["outline"])
            draw.ellipse([hx - hole_r + 2, hy - hole_r + 2, hx + hole_r - 2, hy + hole_r - 2], outline=pal["shadow"])

    def _render_industrial_connector(self, draw: ImageDraw.ImageDraw, cx: float, cy: float, rot: float, dims: Dict[str, Any], pal: Dict[str, Any]):
        w = dims.get("width", 110)
        h = dims.get("height", 60)
        x1, y1 = cx - w / 2, cy - h / 2
        x2, y2 = cx + w / 2, cy + h / 2

        # Outer casing
        draw.rectangle([x1, y1, x2, y2], fill=pal["shadow"], outline=pal["outline"], width=2)
        draw.rectangle([x1 + 5, y1 + 5, x2 - 5, y2 - 5], fill=pal["base"])

        # Inner pin cavity (dark insulated plastic)
        cav_w, cav_h = w - 30, h - 20
        draw.rectangle([cx - cav_w/2, cy - cav_h/2, cx + cav_w/2, cy + cav_h/2], fill=(15, 23, 42), outline=pal["outline"])

        # Gold pin array (2 rows of 4)
        gold = (234, 179, 8)
        cols = 4
        rows = 2
        dx = cav_w / (cols + 1)
        dy = cav_h / (rows + 1)
        start_x = cx - cav_w/2
        start_y = cy - cav_h/2

        for r_idx in range(1, rows + 1):
            for c_idx in range(1, cols + 1):
                px = start_x + c_idx * dx
                py = start_y + r_idx * dy
                draw.ellipse([px - 3, py - 3, px + 3, py + 3], fill=gold, outline=(161, 98, 7))

    def _render_electrical_connector(self, draw: ImageDraw.ImageDraw, cx: float, cy: float, rot: float, dims: Dict[str, Any], pal: Dict[str, Any]):
        w = dims.get("width", 90)
        h = dims.get("height", 50)
        x1, y1 = cx - w / 2, cy - h / 2
        x2, y2 = cx + w / 2, cy + h / 2

        draw.rectangle([x1, y1, x2, y2], fill=(30, 58, 138), outline=pal["outline"], width=2)
        # Screw terminals at top and bottom
        slots = dims.get("slots", 6)
        slot_w = (w - 12) / slots
        for s in range(slots):
            sx = x1 + 6 + s * slot_w + slot_w / 2
            # Top screw
            draw.ellipse([sx - 4, y1 + 6, sx + 4, y1 + 14], fill=(203, 213, 225), outline=pal["outline"])
            draw.line([sx - 3, y1 + 10, sx + 3, y1 + 10], fill=(51, 65, 85))
            # Bottom wire terminal
            draw.ellipse([sx - 4, y2 - 14, sx + 4, y2 - 6], fill=(234, 179, 8), outline=(161, 98, 7))

    def _render_pipe(self, draw: ImageDraw.ImageDraw, cx: float, cy: float, rot: float, dims: Dict[str, Any], pal: Dict[str, Any]):
        length = dims.get("length", 180)
        diameter = dims.get("diameter", 26)
        x1, y1 = cx - length / 2, cy - diameter / 2
        x2, y2 = cx + length / 2, cy + diameter / 2

        # Main cylinder body
        draw.rectangle([x1, y1, x2, y2], fill=pal["base"], outline=pal["outline"], width=1)
        # Specular cylinder highlight running horizontally
        draw.rectangle([x1, y1 + 4, x2, y1 + 8], fill=pal["highlight"])
        draw.rectangle([x1, y2 - 6, x2, y2 - 2], fill=pal["shadow"])

        # End flanges (coupling collars)
        flange_w = 12
        flange_h = diameter + 16
        for fx in (x1, x2 - flange_w):
            draw.rectangle([fx, cy - flange_h / 2, fx + flange_w, cy + flange_h / 2], fill=pal["shadow"], outline=pal["outline"], width=2)
            # Bolt studs on flange
            draw.ellipse([fx + 2, cy - flange_h / 2 + 4, fx + 10, cy - flange_h / 2 + 12], fill=pal["highlight"])
            draw.ellipse([fx + 2, cy + flange_h / 2 - 12, fx + 10, cy + flange_h / 2 - 4], fill=pal["highlight"])

    def _render_bracket(self, draw: ImageDraw.ImageDraw, cx: float, cy: float, rot: float, dims: Dict[str, Any], pal: Dict[str, Any]):
        w = dims.get("width", 70)
        h = dims.get("height", 70)
        thick = dims.get("thickness", 18)
        x1, y1 = cx - w / 2, cy - h / 2

        # L-Shape polygon
        l_shape = [
            (x1, y1),
            (x1 + thick, y1),
            (x1 + thick, y1 + h - thick),
            (x1 + w, y1 + h - thick),
            (x1 + w, y1 + h),
            (x1, y1 + h)
        ]
        draw.polygon(l_shape, fill=pal["base"], outline=pal["outline"])
        # Gusset rib (strengthening diagonal triangle)
        gusset = [
            (x1 + thick, y1 + h - thick),
            (x1 + thick + 20, y1 + h - thick),
            (x1 + thick, y1 + h - thick - 20)
        ]
        draw.polygon(gusset, fill=pal["shadow"], outline=pal["outline"])

        # Mounting slot holes
        draw.ellipse([x1 + 4, y1 + 10, x1 + thick - 4, y1 + 24], fill=(20, 26, 36), outline=pal["outline"])
        draw.ellipse([x1 + w - 24, y1 + h - thick + 4, x1 + w - 10, y1 + h - 4], fill=(20, 26, 36), outline=pal["outline"])

    def _render_fastener(self, draw: ImageDraw.ImageDraw, cx: float, cy: float, rot: float, dims: Dict[str, Any], pal: Dict[str, Any]):
        r = dims.get("radius", 22)
        gap = dims.get("gap_angle_deg", 45)

        # C-Clip / Circlip: Ring with opening gap
        start_angle = math.degrees(rot) + gap / 2
        end_angle = math.degrees(rot) + 360 - gap / 2

        draw.arc([cx - r, cy - r, cx + r, cy + r], start=start_angle, end=end_angle, fill=pal["base"], width=7)
        draw.arc([cx - r + 1, cy - r + 1, cx + r - 1, cy + r - 1], start=start_angle, end=end_angle, fill=pal["highlight"], width=2)

        # Retaining lug eyelets at ends
        rad1 = math.radians(start_angle)
        rad2 = math.radians(end_angle)
        for rad in (rad1, rad2):
            lx = cx + r * math.cos(rad)
            ly = cy + r * math.sin(rad)
            draw.ellipse([lx - 5, ly - 5, lx + 5, ly + 5], fill=pal["base"], outline=pal["outline"])
            draw.ellipse([lx - 2, ly - 2, lx + 2, ly + 2], fill=(20, 26, 36))

    def _render_assembly_fixture(self, draw: ImageDraw.ImageDraw, cx: float, cy: float, rot: float, dims: Dict[str, Any], pal: Dict[str, Any]):
        w = dims.get("width", 140)
        h = dims.get("height", 90)
        slot_w = dims.get("slot_width", 50)
        x1, y1 = cx - w / 2, cy - h / 2
        x2, y2 = cx + w / 2, cy + h / 2

        # Fixture base nest
        draw.rectangle([x1, y1, x2, y2], fill=(30, 41, 59), outline=pal["outline"], width=2)
        # Recessed locating nest pocket
        draw.rectangle([cx - slot_w / 2, cy - 25, cx + slot_w / 2, cy + 25], fill=(15, 23, 42), outline=pal["shadow"])

        # Dowel locating pins (hardened steel dowel pins)
        pin_r = 5
        for px in (x1 + 16, x2 - 16):
            draw.ellipse([px - pin_r, cy - pin_r, px + pin_r, cy + pin_r], fill=(226, 232, 240), outline=pal["outline"])
            draw.point((px - 1, cy - 1), fill=(255, 255, 255))

    def _draw_clutter(self, draw: ImageDraw.ImageDraw, clutter_items: List[Dict[str, Any]]):
        """Draw realistic background clutter (hex keys, washers, metal chips)."""
        for item in clutter_items:
            itype = item.get("type", "washer")
            cx, cy = item["x"], item["y"]
            if itype == "washer":
                draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(148, 163, 184), outline=(71, 85, 105))
                draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(20, 26, 36))
            elif itype == "hex_key":
                # L-shaped Allen wrench
                draw.line([cx - 20, cy, cx + 15, cy], fill=(51, 65, 85), width=4)
                draw.line([cx + 15, cy, cx + 15, cy + 18], fill=(51, 65, 85), width=4)
            elif itype == "metal_chip":
                # Metal machining curl/swarf
                draw.arc([cx - 6, cy - 6, cx + 6, cy + 6], start=30, end=270, fill=(203, 213, 225), width=2)

    def _draw_occlusions(self, draw: ImageDraw.ImageDraw, occlusions: List[Dict[str, Any]]):
        """Draw occluding objects such as wire harnesses or holding clamp arms."""
        for occ in occlusions:
            if occ.get("type") == "wire_harness":
                # Draw thick industrial wiring bundle over components
                pts = occ.get("points", [(100, 300), (400, 320), (700, 280)])
                draw.line(pts, fill=(15, 23, 42), width=14)
                draw.line(pts, fill=(220, 38, 38), width=8)  # Red outer cable
                draw.line(pts, fill=(254, 202, 202), width=2) # Cable specular highlight
            elif occ.get("type") == "clamp_arm":
                x1, y1 = occ.get("x1", 200), occ.get("y1", 200)
                x2, y2 = occ.get("x2", 350), occ.get("y2", 230)
                draw.line([(x1, y1), (x2, y2)], fill=(71, 85, 105), width=18)
                draw.ellipse([x2 - 12, y2 - 12, x2 + 12, y2 + 12], fill=(245, 158, 11))
