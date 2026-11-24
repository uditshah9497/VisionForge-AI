import os
import math
import random
from typing import Dict, Any, List, Tuple
from PIL import Image, ImageDraw, ImageFilter
from backend.app.modules.synthetic.components import (
    MATERIAL_PALETTES,
    get_gear_teeth_vertices,
    get_regular_polygon_vertices,
    rotate_point
)

class SyntheticRenderer:
    """High-fidelity multi-family visual renderer for industrial inspection benchmarks."""

    def __init__(self, width: int = 800, height: int = 600):
        self.width = width
        self.height = height

    def render_scene(self, scene_graph: Dict[str, Any], output_path: str) -> Dict[str, Any]:
        """Render scene into a high-fidelity PNG image with physical textures & 3D shading."""
        family = scene_graph.get("image_family", "mechanical_assembly")
        workstation = scene_graph.get("workstation", {})
        lighting = workstation.get("lighting", {})
        ambient = lighting.get("ambient", 0.75)
        direction = lighting.get("direction", "top_left")

        shadow_dx = -8 if "right" in direction else 8
        shadow_dy = -8 if "bottom" in direction else 8

        # 1. Generate realistic textured background canvas based on image family
        if family == "pcb_electronics":
            base_img = self._create_pcb_surface(scene_graph)
        elif family == "aerospace_structural":
            base_img = self._create_aerospace_composite_surface(scene_graph)
        else:
            base_img = self._create_mechanical_breadboard_surface(scene_graph)

        # 2. Render contact shadows on a separate alpha layer
        shadow_layer = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow_layer)

        components = sorted(scene_graph.get("components", []), key=lambda c: c.get("layer", 1))

        for comp in components:
            if comp.get("defect_type") == "missing":
                continue
            self._render_component_shadow(shadow_draw, comp, shadow_dx, shadow_dy)

        # Diffuse blur for realistic soft shadows
        shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=5))
        base_img = Image.alpha_composite(base_img, shadow_layer)

        # 3. Render objects layer with metallic shading & specular bevels
        object_layer = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        object_draw = ImageDraw.Draw(object_layer)

        for comp in components:
            self._render_component(object_draw, comp, lighting, family)

        # 4. Render background clutter if any (metal swarf, hex key, calibration ticks)
        if scene_graph.get("clutter"):
            self._render_clutter(object_draw, scene_graph["clutter"], family)

        # 5. Render occlusions (wire harness bundle, fixture clamp arm)
        if scene_graph.get("occlusions"):
            self._render_occlusions(object_draw, scene_graph["occlusions"])

        final_img = Image.alpha_composite(base_img, object_layer)

        # Ambient lighting adjustment
        if ambient < 0.6:
            darken = Image.new("RGBA", (self.width, self.height), (0, 0, 0, int((0.6 - ambient) * 220)))
            final_img = Image.alpha_composite(final_img, darken)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        final_rgb = final_img.convert("RGB")
        final_rgb.save(output_path, "PNG", quality=95)

        return {
            "output_path": output_path,
            "width": self.width,
            "height": self.height,
            "file_size_bytes": os.path.getsize(output_path),
            "format": "PNG"
        }

    # -------------------------------------------------------------
    # BACKGROUND TEXTURE GENERATORS
    # -------------------------------------------------------------
    def _create_mechanical_breadboard_surface(self, scene_graph: Dict[str, Any]) -> Image.Image:
        """Create dark matte anodized breadboard with micro-grooves and threaded M6 holes."""
        img = Image.new("RGBA", (self.width, self.height), (18, 24, 34, 255))
        draw = ImageDraw.Draw(img)

        # Brushed horizontal metallic grain lines
        for y in range(0, self.height, 2):
            lum = random.randint(16, 26)
            draw.line([(0, y), (self.width, y)], fill=(lum, lum + 5, lum + 14, 255))

        # Precision M6 tapped hole matrix
        spacing = 40
        for x in range(20, self.width, spacing):
            for y in range(20, self.height, spacing):
                # Outer countersink shadow
                draw.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(12, 16, 24, 255), outline=(32, 42, 58, 255))
                # Internal thread spiral ring
                draw.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(8, 12, 18, 255), outline=(50, 62, 82, 255))
                draw.point((x - 1, y - 1), fill=(100, 115, 140, 255))

        # Laser-etched grid boundary line
        draw.rectangle([10, 10, self.width - 10, self.height - 10], outline=(30, 41, 59, 180), width=1)
        return img

    def _create_pcb_surface(self, scene_graph: Dict[str, Any]) -> Image.Image:
        """Create FR4 green solder mask PCB with copper trace routing & gold fiducials."""
        img = Image.new("RGBA", (self.width, self.height), (15, 75, 42, 255))
        draw = ImageDraw.Draw(img)

        # Solder mask weave texture
        for y in range(0, self.height, 3):
            g_val = random.randint(68, 82)
            draw.line([(0, y), (self.width, y)], fill=(12, g_val, 38, 255))

        # Copper traces running across the board
        trace_color = (25, 120, 65, 255)
        for i in range(12):
            sy = 60 + i * 45
            draw.line([(50, sy), (280, sy), (340, sy + 30), (740, sy + 30)], fill=trace_color, width=3)
            # Via holes with copper annular rings
            draw.ellipse([278, sy - 2, 282, sy + 2], fill=(217, 119, 6), outline=(245, 158, 11))
            draw.ellipse([738, sy + 28, 742, sy + 32], fill=(217, 119, 6), outline=(245, 158, 11))

        # Ground plane copper hatching
        for x in range(30, self.width, 80):
            draw.line([(x, 20), (x, self.height - 20)], fill=(20, 95, 52, 180), width=1)

        # Corner gold fiducial targets
        gold = (234, 179, 8)
        for fx, fy in [(30, 30), (self.width - 30, 30), (30, self.height - 30), (self.width - 30, self.height - 30)]:
            draw.ellipse([fx - 7, fy - 7, fx + 7, fy + 7], fill=(10, 50, 28), outline=gold, width=2)
            draw.ellipse([fx - 3, fy - 3, fx + 3, fy + 3], fill=gold)

        return img

    def _create_aerospace_composite_surface(self, scene_graph: Dict[str, Any]) -> Image.Image:
        """Create carbon-fiber composite weave surface with cross-hatch fabric pattern."""
        img = Image.new("RGBA", (self.width, self.height), (24, 26, 32, 255))
        draw = ImageDraw.Draw(img)

        # 2x2 Twill carbon-fiber weave pattern
        tile = 12
        for x in range(0, self.width, tile):
            for y in range(0, self.height, tile):
                is_horiz = ((x // tile) + (y // tile)) % 2 == 0
                c = (38, 42, 50, 255) if is_horiz else (18, 20, 24, 255)
                draw.rectangle([x, y, x + tile - 1, y + tile - 1], fill=c)

        # Inspection datum crosshair marks
        draw.line([(self.width // 2, 20), (self.width // 2, self.height - 20)], fill=(50, 55, 68, 180), width=1)
        draw.line([(20, self.height // 2), (self.width - 20, self.height // 2)], fill=(50, 55, 68, 180), width=1)
        return img

    # -------------------------------------------------------------
    # SHADOW RENDERING
    # -------------------------------------------------------------
    def _render_component_shadow(self, draw: ImageDraw.ImageDraw, comp: Dict[str, Any], dx: int, dy: int):
        cx = comp["center"]["x"] + dx
        cy = comp["center"]["y"] + dy
        ctype = comp["type"]
        dims = comp["dimensions"]
        shadow_color = (0, 0, 0, 130)

        if ctype in ("spur_gear", "hex_nut", "fastener", "electrolytic_cap", "countersunk_rivet"):
            r = dims.get("radius", 40)
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=shadow_color)
        elif ctype in ("hex_bolt", "lockwire_fastener", "torque_seal_bolt"):
            r = dims.get("flange_radius", 24)
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=shadow_color)
        elif ctype in ("mounting_plate", "assembly_fixture", "composite_panel", "microcontroller_qfp"):
            w = dims.get("width", 100)
            h = dims.get("height", 80)
            draw.rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], fill=shadow_color)
        elif ctype == "pipe":
            l = dims.get("length", 160)
            d = dims.get("diameter", 28)
            draw.rectangle([cx - l / 2, cy - d / 2, cx + l / 2, cy + d / 2], fill=shadow_color)
        else:
            w = dims.get("width", 50)
            h = dims.get("height", 40)
            draw.rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], fill=shadow_color)

    # -------------------------------------------------------------
    # COMPONENT RENDERING
    # -------------------------------------------------------------
    def _render_component(self, draw: ImageDraw.ImageDraw, comp: Dict[str, Any], lighting: Dict[str, Any], family: str):
        ctype = comp["type"]
        cx = comp["center"]["x"]
        cy = comp["center"]["y"]
        rot = math.radians(comp.get("rotation_deg", 0.0))
        palette = MATERIAL_PALETTES.get(comp.get("material", "machined_steel"), MATERIAL_PALETTES["machined_steel"])
        is_missing = comp.get("defect_type") == "missing"

        if is_missing:
            # Render empty socket with realistic chamfer and thread groove
            r = comp["dimensions"].get("radius", 22)
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(10, 14, 22, 230), outline=(239, 68, 68, 220), width=2)
            draw.ellipse([cx - r + 3, cy - r + 3, cx + r - 3, cy + r - 3], outline=(45, 55, 75, 255), width=1)
            draw.ellipse([cx - r/2, cy - r/2, cx + r/2, cy + r/2], fill=(5, 8, 14, 255))
            return

        # Mechanical components
        if ctype == "spur_gear":
            self._render_spur_gear_3d(draw, cx, cy, rot, comp["dimensions"], palette)
        elif ctype == "hex_bolt":
            self._render_hex_bolt_3d(draw, cx, cy, rot, comp["dimensions"], palette)
        elif ctype == "hex_nut":
            self._render_hex_nut_3d(draw, cx, cy, rot, comp["dimensions"], palette)
        elif ctype == "mounting_plate":
            self._render_mounting_plate_3d(draw, cx, cy, rot, comp["dimensions"], palette)
        elif ctype == "pipe":
            self._render_pipe_3d(draw, cx, cy, rot, comp["dimensions"], palette)
        elif ctype == "bracket" or ctype == "titanium_bracket":
            self._render_bracket_3d(draw, cx, cy, rot, comp["dimensions"], palette)
        elif ctype == "fastener":
            self._render_circlip_3d(draw, cx, cy, rot, comp["dimensions"], palette)
        elif ctype == "assembly_fixture":
            self._render_fixture_3d(draw, cx, cy, rot, comp["dimensions"], palette)
        elif ctype in ("industrial_connector", "electrical_connector"):
            self._render_connector_3d(draw, cx, cy, rot, comp["dimensions"], palette)
        # PCB Electronics components
        elif ctype == "microcontroller_qfp":
            self._render_qfp_ic_3d(draw, cx, cy, rot, comp["dimensions"], comp)
        elif ctype in ("smd_resistor", "smd_capacitor"):
            self._render_smd_passives(draw, cx, cy, rot, comp["dimensions"], ctype)
        elif ctype == "electrolytic_cap":
            self._render_electrolytic_cap(draw, cx, cy, rot, comp["dimensions"])
        elif ctype == "diode_sod123":
            self._render_diode_sod(draw, cx, cy, rot, comp["dimensions"], comp)
        elif ctype == "pin_header_8pin":
            self._render_pin_header(draw, cx, cy, rot, comp["dimensions"])
        else:
            # Fallback high-fidelity block
            w = comp["dimensions"].get("width", 60)
            h = comp["dimensions"].get("height", 40)
            draw.rectangle([cx - w/2, cy - h/2, cx + w/2, cy + h/2], fill=palette["base"], outline=palette["outline"], width=2)

    # -------------------------------------------------------------
    # 3D SHADED GEOMETRIC RENDERERS
    # -------------------------------------------------------------
    def _render_spur_gear_3d(self, draw: ImageDraw.ImageDraw, cx: float, cy: float, rot: float, dims: Dict[str, Any], pal: Dict[str, Any]):
        r = dims.get("radius", 55)
        teeth = dims.get("teeth", 16)
        bore_r = dims.get("bore_radius", 15)

        # Outer gear teeth with metallic body
        teeth_pts = get_gear_teeth_vertices(cx, cy, r, teeth, tooth_depth=13, rotation_rad=rot)
        draw.polygon(teeth_pts, fill=pal["base"], outline=pal["outline"])

        # Top bevel rim (specular lighting)
        draw.ellipse([cx - (r - 9), cy - (r - 9), cx + (r - 9), cy + (r - 9)], fill=pal["highlight"], outline=pal["outline"])
        draw.ellipse([cx - (r - 14), cy - (r - 14), cx + (r - 14), cy + (r - 14)], fill=pal["shadow"])

        # Inner face with circular brush grain
        inner_r = r - 15
        draw.ellipse([cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r], fill=pal["base"])

        # 4 Chamfered lightening holes
        hole_dist = r * 0.55
        for i in range(4):
            angle = rot + i * (math.pi / 2)
            hx = cx + hole_dist * math.cos(angle)
            hy = cy + hole_dist * math.sin(angle)
            draw.ellipse([hx - 9, hy - 9, hx + 9, hy + 9], fill=pal["shadow"], outline=pal["outline"])
            draw.ellipse([hx - 8, hy - 8, hx + 8, hy + 8], fill=(20, 26, 36))
            draw.arc([hx - 8, hy - 8, hx + 8, hy + 8], start=180, end=360, fill=pal["highlight"], width=1)

        # Central axle bore & drive keyway
        draw.ellipse([cx - bore_r, cy - bore_r, cx + bore_r, cy + bore_r], fill=(12, 16, 24), outline=pal["outline"], width=2)
        kw_w = 4
        kw_h = 8
        draw.rectangle([cx - kw_w, cy - bore_r - kw_h, cx + kw_w, cy - bore_r], fill=(12, 16, 24))

    def _render_hex_bolt_3d(self, draw: ImageDraw.ImageDraw, cx: float, cy: float, rot: float, dims: Dict[str, Any], pal: Dict[str, Any]):
        flange_r = dims.get("flange_radius", 24)
        head_r = dims.get("head_radius", 17)

        # Serrated flange washer base
        draw.ellipse([cx - flange_r, cy - flange_r, cx + flange_r, cy + flange_r], fill=pal["shadow"], outline=pal["outline"], width=2)
        draw.ellipse([cx - flange_r + 2, cy - flange_r + 2, cx + flange_r - 2, cy + flange_r - 2], fill=pal["base"])
        # Specular washer highlight
        draw.arc([cx - flange_r + 2, cy - flange_r + 2, cx + flange_r - 2, cy + flange_r - 2], start=135, end=315, fill=pal["highlight"], width=2)

        # 6-Sided Hexagon Head
        hex_pts = get_regular_polygon_vertices(cx, cy, head_r, 6, rotation_rad=rot)
        draw.polygon(hex_pts, fill=pal["highlight"], outline=pal["outline"])

        # Inner chamfer facet triangle lines
        for pt in hex_pts:
            draw.line([(cx, cy), pt], fill=pal["shadow"], width=1)

        # Center dimple / socket
        draw.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=pal["shadow"], outline=pal["outline"])

    def _render_hex_nut_3d(self, draw: ImageDraw.ImageDraw, cx: float, cy: float, rot: float, dims: Dict[str, Any], pal: Dict[str, Any]):
        r = dims.get("radius", 22)
        bore_r = dims.get("bore_radius", 11)

        hex_pts = get_regular_polygon_vertices(cx, cy, r, 6, rotation_rad=rot)
        draw.polygon(hex_pts, fill=pal["base"], outline=pal["outline"])
        draw.ellipse([cx - (r - 4), cy - (r - 4), cx + (r - 4), cy + (r - 4)], fill=pal["highlight"], outline=pal["outline"])

        # Threaded internal bore with helical thread spirals
        draw.ellipse([cx - bore_r, cy - bore_r, cx + bore_r, cy + bore_r], fill=(12, 16, 24), outline=pal["outline"], width=2)
        for offset in range(-6, 7, 3):
            draw.arc([cx - bore_r + 2, cy + offset - 2, cx + bore_r - 2, cy + offset + 2], start=30, end=210, fill=pal["shadow"], width=1)

    def _render_mounting_plate_3d(self, draw: ImageDraw.ImageDraw, cx: float, cy: float, rot: float, dims: Dict[str, Any], pal: Dict[str, Any]):
        w = dims.get("width", 260)
        h = dims.get("height", 180)
        x1, y1 = cx - w / 2, cy - h / 2
        x2, y2 = cx + w / 2, cy + h / 2

        # Outer chamfer shadow
        draw.rectangle([x1, y1, x2, y2], fill=pal["shadow"], outline=pal["outline"], width=2)
        # Machined face
        draw.rectangle([x1 + 4, y1 + 4, x2 - 4, y2 - 4], fill=pal["base"])
        # Top-left specular highlight edge
        draw.line([(x1 + 4, y1 + 4), (x2 - 4, y1 + 4)], fill=pal["highlight"], width=2)
        draw.line([(x1 + 4, y1 + 4), (x1 + 4, y2 - 4)], fill=pal["highlight"], width=2)

        # 4 Precision countersunk screw holes
        inset = 24
        hole_r = 9
        for hx, hy in [(x1 + inset, y1 + inset), (x2 - inset, y1 + inset), (x1 + inset, y2 - inset), (x2 - inset, y2 - inset)]:
            draw.ellipse([hx - hole_r, hy - hole_r, hx + hole_r, hy + hole_r], fill=(12, 16, 24), outline=pal["outline"], width=2)
            draw.arc([hx - hole_r, hy - hole_r, hx + hole_r, hy + hole_r], start=180, end=360, fill=pal["highlight"], width=1)

    def _render_pipe_3d(self, draw: ImageDraw.ImageDraw, cx: float, cy: float, rot: float, dims: Dict[str, Any], pal: Dict[str, Any]):
        length = dims.get("length", 180)
        diameter = dims.get("diameter", 28)
        x1, y1 = cx - length / 2, cy - diameter / 2
        x2, y2 = cx + length / 2, cy + diameter / 2

        # Cylindrical gradient simulation
        draw.rectangle([x1, y1, x2, y2], fill=pal["base"], outline=pal["outline"], width=1)
        draw.rectangle([x1, y1 + 3, x2, y1 + 8], fill=pal["highlight"])  # Specular streak
        draw.rectangle([x1, y2 - 7, x2, y2 - 2], fill=pal["shadow"])

        # End Flanges with studs
        flange_w = 14
        flange_h = diameter + 18
        for fx in (x1, x2 - flange_w):
            draw.rectangle([fx, cy - flange_h / 2, fx + flange_w, cy + flange_h / 2], fill=pal["shadow"], outline=pal["outline"], width=2)
            draw.ellipse([fx + 3, cy - flange_h / 2 + 3, fx + 11, cy - flange_h / 2 + 11], fill=pal["highlight"])
            draw.ellipse([fx + 3, cy + flange_h / 2 - 11, fx + 11, cy + flange_h / 2 - 3], fill=pal["highlight"])

    def _render_bracket_3d(self, draw: ImageDraw.ImageDraw, cx: float, cy: float, rot: float, dims: Dict[str, Any], pal: Dict[str, Any]):
        w = dims.get("width", 75)
        h = dims.get("height", 75)
        thick = dims.get("thickness", 20)
        x1, y1 = cx - w / 2, cy - h / 2

        l_shape = [
            (x1, y1),
            (x1 + thick, y1),
            (x1 + thick, y1 + h - thick),
            (x1 + w, y1 + h - thick),
            (x1 + w, y1 + h),
            (x1, y1 + h)
        ]
        draw.polygon(l_shape, fill=pal["base"], outline=pal["outline"])
        # Diagonal gusset rib
        gusset = [
            (x1 + thick, y1 + h - thick),
            (x1 + thick + 22, y1 + h - thick),
            (x1 + thick, y1 + h - thick - 22)
        ]
        draw.polygon(gusset, fill=pal["shadow"], outline=pal["outline"])
        # Slotted fastening holes
        draw.ellipse([x1 + 4, y1 + 12, x1 + thick - 4, y1 + 28], fill=(12, 16, 24), outline=pal["outline"])
        draw.ellipse([x1 + w - 28, y1 + h - thick + 4, x1 + w - 12, y1 + h - 4], fill=(12, 16, 24), outline=pal["outline"])

    def _render_circlip_3d(self, draw: ImageDraw.ImageDraw, cx: float, cy: float, rot: float, dims: Dict[str, Any], pal: Dict[str, Any]):
        r = dims.get("radius", 22)
        gap = dims.get("gap_angle_deg", 45)
        start_a = math.degrees(rot) + gap / 2
        end_a = math.degrees(rot) + 360 - gap / 2

        draw.arc([cx - r, cy - r, cx + r, cy + r], start=start_a, end=end_a, fill=pal["base"], width=8)
        draw.arc([cx - r + 1, cy - r + 1, cx + r - 1, cy + r - 1], start=start_a, end=end_a, fill=pal["highlight"], width=2)
        rad1 = math.radians(start_a)
        rad2 = math.radians(end_a)
        for rad in (rad1, rad2):
            lx = cx + r * math.cos(rad)
            ly = cy + r * math.sin(rad)
            draw.ellipse([lx - 6, ly - 6, lx + 6, ly + 6], fill=pal["base"], outline=pal["outline"])
            draw.ellipse([lx - 2, ly - 2, lx + 2, ly + 2], fill=(12, 16, 24))

    def _render_fixture_3d(self, draw: ImageDraw.ImageDraw, cx: float, cy: float, rot: float, dims: Dict[str, Any], pal: Dict[str, Any]):
        w = dims.get("width", 140)
        h = dims.get("height", 90)
        x1, y1 = cx - w / 2, cy - h / 2
        x2, y2 = cx + w / 2, cy + h / 2

        draw.rectangle([x1, y1, x2, y2], fill=(30, 41, 59), outline=pal["outline"], width=2)
        draw.rectangle([cx - 28, cy - 25, cx + 28, cy + 25], fill=(12, 16, 24), outline=pal["shadow"])
        # Hardened steel locating dowel pins
        for px in (x1 + 18, x2 - 18):
            draw.ellipse([px - 6, cy - 6, px + 6, cy + 6], fill=(240, 245, 255), outline=pal["outline"], width=1)
            draw.point((px - 2, cy - 2), fill=(255, 255, 255))

    def _render_connector_3d(self, draw: ImageDraw.ImageDraw, cx: float, cy: float, rot: float, dims: Dict[str, Any], pal: Dict[str, Any]):
        w = dims.get("width", 110)
        h = dims.get("height", 60)
        x1, y1 = cx - w / 2, cy - h / 2
        x2, y2 = cx + w / 2, cy + h / 2

        draw.rectangle([x1, y1, x2, y2], fill=pal["shadow"], outline=pal["outline"], width=2)
        draw.rectangle([x1 + 5, y1 + 5, x2 - 5, y2 - 5], fill=pal["base"])
        cav_w, cav_h = w - 30, h - 20
        draw.rectangle([cx - cav_w/2, cy - cav_h/2, cx + cav_w/2, cy + cav_h/2], fill=(12, 16, 24), outline=pal["outline"])
        gold = (234, 179, 8)
        cols, rows = 4, 2
        dx = cav_w / (cols + 1)
        dy = cav_h / (rows + 1)
        for r_i in range(1, rows + 1):
            for c_i in range(1, cols + 1):
                px = cx - cav_w/2 + c_i * dx
                py = cy - cav_h/2 + r_i * dy
                draw.ellipse([px - 3, py - 3, px + 3, py + 3], fill=gold, outline=(161, 98, 7))

    # -------------------------------------------------------------
    # SMT PCB ELECTRONICS RENDERERS
    # -------------------------------------------------------------
    def _render_qfp_ic_3d(self, draw: ImageDraw.ImageDraw, cx: float, cy: float, rot: float, dims: Dict[str, Any], comp: Dict[str, Any]):
        w = dims.get("width", 74)
        h = dims.get("height", 74)
        x1, y1 = cx - w / 2, cy - h / 2
        x2, y2 = cx + w / 2, cy + h / 2

        # Solder pads around 4 sides with silver pins
        pin_silver = (210, 220, 235)
        pin_w = 4
        pin_l = 8
        pins_per_side = 8
        step = (w - 16) / (pins_per_side - 1)

        for p_i in range(pins_per_side):
            # Top & Bottom pins
            px = x1 + 8 + p_i * step
            draw.rectangle([px - pin_w/2, y1 - pin_l, px + pin_w/2, y1], fill=pin_silver, outline=(40, 50, 65))
            draw.rectangle([px - pin_w/2, y2, px + pin_w/2, y2 + pin_l], fill=pin_silver, outline=(40, 50, 65))
            # Left & Right pins
            py = y1 + 8 + p_i * step
            draw.rectangle([x1 - pin_l, py - pin_w/2, x1, py + pin_w/2], fill=pin_silver, outline=(40, 50, 65))
            draw.rectangle([x2, py - pin_w/2, x2 + pin_l, py + pin_w/2], fill=pin_silver, outline=(40, 50, 65))

        # Black Molded Epoxy Body
        draw.rectangle([x1, y1, x2, y2], fill=(22, 26, 32), outline=(10, 12, 16), width=2)
        draw.rectangle([x1 + 3, y1 + 3, x2 - 3, y2 - 3], fill=(30, 34, 42))

        # Circular Pin 1 indicator dot (Corner)
        pin1_x = x1 + 10
        pin1_y = y1 + 10
        # If rotation defect, invert pin1 to opposite corner
        if comp.get("rotation_deg", 0.0) == 180.0:
            pin1_x = x2 - 10
            pin1_y = y2 - 10

        draw.ellipse([pin1_x - 3, pin1_y - 3, pin1_x + 3, pin1_y + 3], fill=(12, 14, 18), outline=(60, 65, 75))

        # Laser-etched Part ID
        draw.text((cx - 24, cy - 6), "VF-32A", fill=(140, 150, 165))

    def _render_smd_passives(self, draw: ImageDraw.ImageDraw, cx: float, cy: float, rot: float, dims: Dict[str, Any], ctype: str):
        w = dims.get("width", 36)
        h = dims.get("height", 20)
        x1, y1 = cx - w / 2, cy - h / 2
        x2, y2 = cx + w / 2, cy + h / 2

        body_color = (25, 28, 34) if ctype == "smd_resistor" else (160, 110, 70)  # Brown ceramic for capacitor
        silver = (220, 230, 240)

        # Main component body
        draw.rectangle([x1, y1, x2, y2], fill=body_color, outline=(15, 20, 25))
        # Tinned solder end caps
        cap_w = 7
        draw.rectangle([x1, y1, x1 + cap_w, y2], fill=silver, outline=(100, 110, 125))
        draw.rectangle([x2 - cap_w, y1, x2, y2], fill=silver, outline=(100, 110, 125))

        # Resistor value code stamping
        if ctype == "smd_resistor":
            draw.text((cx - 9, cy - 5), "103", fill=(190, 200, 215))

    def _render_electrolytic_cap(self, draw: ImageDraw.ImageDraw, cx: float, cy: float, rot: float, dims: Dict[str, Any]):
        r = dims.get("radius", 24)
        # Aluminum can top
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(195, 205, 220), outline=(80, 90, 105), width=2)
        # Black polarity stripe
        draw.chord([cx - r, cy - r, cx + r, cy + r], start=120, end=240, fill=(28, 32, 40))
        # Pressure relief vent cross stamped in metal
        draw.line([(cx - 8, cy), (cx + 8, cy)], fill=(120, 130, 145), width=2)
        draw.line([(cx, cy - 8), (cx, cy + 8)], fill=(120, 130, 145), width=2)

    def _render_diode_sod(self, draw: ImageDraw.ImageDraw, cx: float, cy: float, rot: float, dims: Dict[str, Any], comp: Dict[str, Any]):
        w = dims.get("width", 40)
        h = dims.get("height", 22)
        x1, y1 = cx - w / 2, cy - h / 2
        x2, y2 = cx + w / 2, cy + h / 2

        draw.rectangle([x1, y1, x2, y2], fill=(22, 26, 32), outline=(10, 12, 16), width=1)
        # Silver leads
        lead_w = 4
        draw.rectangle([x1 - lead_w, cy - 4, x1, cy + 4], fill=(210, 220, 235))
        draw.rectangle([x2, cy - 4, x2 + lead_w, cy + 4], fill=(210, 220, 235))

        # Cathode polarity band (white stripe)
        band_x = x1 + 6 if comp.get("rotation_deg", 0.0) != 180.0 else x2 - 10
        draw.rectangle([band_x, y1 + 2, band_x + 4, y2 - 2], fill=(245, 248, 255))

    def _render_pin_header(self, draw: ImageDraw.ImageDraw, cx: float, cy: float, rot: float, dims: Dict[str, Any]):
        w = dims.get("width", 80)
        h = dims.get("height", 40)
        x1, y1 = cx - w / 2, cy - h / 2
        x2, y2 = cx + w / 2, cy + h / 2

        draw.rectangle([x1, y1, x2, y2], fill=(20, 22, 28), outline=(10, 12, 16))
        gold = (234, 179, 8)
        cols, rows = 4, 2
        dx = w / (cols + 1)
        dy = h / (rows + 1)
        for r_i in range(1, rows + 1):
            for c_i in range(1, cols + 1):
                px = x1 + c_i * dx
                py = y1 + r_i * dy
                draw.rectangle([px - 3, py - 3, px + 3, py + 3], fill=gold, outline=(161, 98, 7))

    # -------------------------------------------------------------
    # CLUTTER & OCCLUSIONS
    # -------------------------------------------------------------
    def _render_clutter(self, draw: ImageDraw.ImageDraw, items: List[Dict[str, Any]], family: str):
        for item in items:
            itype = item.get("type", "washer")
            cx, cy = item["x"], item["y"]
            if itype == "hex_key":
                draw.line([(cx - 24, cy), (cx + 18, cy)], fill=(170, 185, 205), width=5)
                draw.line([(cx + 18, cy), (cx + 18, cy + 22)], fill=(170, 185, 205), width=5)
            elif itype == "metal_chip":
                draw.arc([cx - 8, cy - 8, cx + 8, cy + 8], start=20, end=290, fill=(215, 225, 240), width=2)
            else:
                draw.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=(160, 175, 195), outline=(70, 85, 105))
                draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(15, 20, 28))

    def _render_occlusions(self, draw: ImageDraw.ImageDraw, occlusions: List[Dict[str, Any]]):
        for occ in occlusions:
            if occ.get("type") == "wire_harness":
                pts = occ.get("points", [(100, 300), (400, 320), (700, 280)])
                draw.line(pts, fill=(10, 14, 20), width=18)
                draw.line(pts, fill=(220, 38, 38), width=10)   # High-voltage red sleeve
                draw.line(pts, fill=(254, 202, 202), width=2)  # Highlight streak
                # Zip-tie bands
                for p in pts:
                    draw.ellipse([p[0] - 6, p[1] - 6, p[0] + 6, p[1] + 6], fill=(245, 245, 250))
            elif occ.get("type") == "clamp_arm":
                x1, y1 = occ.get("x1", 200), occ.get("y1", 200)
                x2, y2 = occ.get("x2", 350), occ.get("y2", 230)
                draw.line([(x1, y1), (x2, y2)], fill=(75, 85, 100), width=20)
                draw.ellipse([x2 - 12, y2 - 12, x2 + 12, y2 + 12], fill=(245, 158, 11))
