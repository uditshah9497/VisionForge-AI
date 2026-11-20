#!/usr/bin/env python3
"""VisionForge AI - Unified Launch Script

Starts the FastAPI server which serves both the REST API and the React Enterprise UI.
"""
import sys
import os
import uvicorn

if __name__ == "__main__":
    # Ensure current directory is in sys.path
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

    print("=" * 60)
    print("  VisionForge AI: Multimodal Benchmark Factory")
    print("  Domain: Industrial Manufacturing Quality Inspection")
    print("=" * 60)
    print("  - Web Dashboard:  http://localhost:8000")
    print("  - OpenAPI Docs:   http://localhost:8000/docs")
    print("  - Health Check:   http://localhost:8000/api/health")
    print("=" * 60)

    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=False)
