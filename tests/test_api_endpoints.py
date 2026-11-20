import pytest
from backend.app.core.database import SessionLocal
from backend.app.api.routes import (
    health_check,
    get_available_models,
    get_analytics_overview,
    list_datasets,
    get_validation_summary
)

@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def test_health_endpoint():
    res = health_check()
    assert res["status"] == "healthy"
    assert "VisionForge" in res["service"]

def test_models_endpoint():
    models = get_available_models()
    assert len(models) >= 4
    model_ids = [m["id"] for m in models]
    assert "visionforge-demo-v1" in model_ids
    assert "gemini-1.5-pro" in model_ids

def test_analytics_overview_endpoint(db):
    data = get_analytics_overview(db)
    assert "total_images_generated" in data
    assert "validation_pass_rate" in data
    assert "accuracy_by_category" in data

def test_datasets_and_validation_summary(db):
    datasets = list_datasets(db)
    assert isinstance(datasets, list)

    summary = get_validation_summary(db)
    assert "total_evaluated" in summary
    assert "pass_rate" in summary
