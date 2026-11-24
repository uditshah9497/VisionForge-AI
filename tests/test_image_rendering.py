import os
import pytest
from PIL import Image
from backend.app.modules.synthetic.generator import SceneGenerator
from backend.app.modules.synthetic.renderer import SyntheticRenderer

def test_image_rendering_creates_valid_png(tmp_path):
    gen = SceneGenerator(seed=55)
    sg = gen.generate_scene(seed=55)

    renderer = SyntheticRenderer(width=800, height=600)
    out_file = str(tmp_path / "test_render.png")
    res = renderer.render_scene(sg, out_file)

    assert os.path.exists(out_file)
    assert res["file_size_bytes"] > 1000
    assert res["width"] == 800
    assert res["height"] == 600

    # Verify Pillow can open and decode it
    with Image.open(out_file) as img:
        assert img.format == "PNG"
        assert img.size == (800, 600)
        assert img.mode == "RGB"

def test_render_with_lighting_and_defects(tmp_path):
    gen = SceneGenerator(seed=88)
    sg = gen.generate_scene(
        difficulty="hard",
        defect_types=["missing", "misplaced", "orientation", "occlusion"],
        lighting="low_light",
        seed=88
    )

    renderer = SyntheticRenderer()
    out_file = str(tmp_path / "test_hard.png")
    res = renderer.render_scene(sg, out_file)

    assert os.path.exists(out_file)
    assert res["file_size_bytes"] > 2000

def test_render_all_image_families(tmp_path):
    """Verify rendering succeeds across all supported industrial image families."""
    renderer = SyntheticRenderer()
    for family in ["mechanical_assembly", "pcb_electronics", "aerospace_structural"]:
        gen = SceneGenerator(seed=99)
        sg = gen.generate_scene(image_family=family, difficulty="medium", seed=99)
        out_file = str(tmp_path / f"test_{family}.png")
        res = renderer.render_scene(sg, out_file)
        assert os.path.exists(out_file)
        assert res["file_size_bytes"] > 2000
        with Image.open(out_file) as img:
            assert img.size == (800, 600)
            assert img.format == "PNG"
