import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.app.core.config import DEBUG, ARTIFACTS_DIR, REPORTS_DIR, BASE_DIR
from backend.app.core.database import Base, engine
from backend.app.api.routes import router as api_router

# Initialize database schema
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="VisionForge AI: Multimodal Benchmark Factory",
    description="Automated synthetic dataset generation, verifiable visual reasoning questions, deterministic ground truth, automated task validation, and frontier multimodal model evaluation.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for generated images and reports
app.mount("/data/artifacts", StaticFiles(directory=str(ARTIFACTS_DIR)), name="artifacts")
app.mount("/data/reports", StaticFiles(directory=str(REPORTS_DIR)), name="reports")

# Include API router
app.include_router(api_router)

# Mount built frontend assets if dist exists
dist_dir = BASE_DIR / "frontend" / "dist"
if dist_dir.exists():
    assets_dir = dist_dir / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        # Don't intercept API or data routes
        if full_path.startswith("api") or full_path.startswith("data") or full_path.startswith("docs") or full_path.startswith("redoc"):
            return None
        index_file = dist_dir / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return {"error": "Frontend build not found"}
else:
    @app.get("/")
    def root():
        return {
            "service": "VisionForge AI",
            "description": "Synthetic Visual Intelligence & Multimodal Benchmark Factory",
            "api_docs": "/docs",
            "health": "/api/health"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=DEBUG)
