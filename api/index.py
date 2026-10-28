import os
import sys
from fastapi import Request

# Add backend directory to sys.path so app package can be imported by Vercel serverless runtime
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.main import app  # noqa: E402


@app.get("/api/debug")
@app.get("/debug")
@app.get("/api/index.py")
async def debug_endpoint(request: Request):
    return {
        "url_path": request.url.path,
        "scope_path": request.scope.get("path"),
        "root_path": request.scope.get("root_path"),
        "routes": [route.path for route in app.routes if hasattr(route, "path")],
    }
