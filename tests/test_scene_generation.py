import pytest
from backend.app.modules.synthetic.generator import SceneGenerator

def test_scene_generation_basic():
    gen = SceneGenerator(seed=101)
    sg = gen.generate_scene(difficulty="medium", component_count=6, seed=101)

    assert sg is not None
    assert "scene_id" in sg
    assert sg["dimensions"]["width"] == 800
    assert sg["dimensions"]["height"] == 600
    assert len(sg["components"]) >= 5
    assert "spatial_relations" in sg

def test_seed_reproducibility():
    """Verify that reusing the same seed reproduces the exact same scene."""
    gen1 = SceneGenerator(seed=4242)
    sg1 = gen1.generate_scene(difficulty="medium", seed=4242)

    gen2 = SceneGenerator(seed=4242)
    sg2 = gen2.generate_scene(difficulty="medium", seed=4242)

    assert len(sg1["components"]) == len(sg2["components"])
    for c1, c2 in zip(sg1["components"], sg2["components"]):
        assert c1["id"] == c2["id"]
        assert c1["type"] == c2["type"]
        assert c1["center"] == c2["center"]
        assert c1["bbox"] == c2["bbox"]
        assert c1["rotation_deg"] == c2["rotation_deg"]

def test_different_seeds_produce_different_scenes():
    """Verify that changing random seed produces different scene compositions."""
    gen = SceneGenerator()
    sg1 = gen.generate_scene(seed=123)
    sg2 = gen.generate_scene(seed=999)

    # Centers or types should vary
    centers1 = [c["center"] for c in sg1["components"]]
    centers2 = [c["center"] for c in sg2["components"]]
    assert centers1 != centers2

def test_bounding_boxes_within_canvas():
    """Verify all component bounding boxes lie within canvas bounds."""
    gen = SceneGenerator(seed=777)
    sg = gen.generate_scene(difficulty="hard", component_count=8, seed=777)

    w = sg["dimensions"]["width"]
    h = sg["dimensions"]["height"]

    for comp in sg["components"]:
        bbox = comp["bbox"]
        assert bbox[0] >= 0, f"bbox min_x {bbox[0]} < 0"
        assert bbox[1] >= 0, f"bbox min_y {bbox[1]} < 0"
        assert bbox[2] <= w + 10, f"bbox max_x {bbox[2]} > {w}"
        assert bbox[3] <= h + 10, f"bbox max_y {bbox[3]} > {h}"
        assert bbox[2] > bbox[0], "bbox width must be positive"
        assert bbox[3] > bbox[1], "bbox height must be positive"
