import os
import sys
import urllib.parse

from starlette.types import ASGIApp, Receive, Scope, Send

# Add backend directory to sys.path so app package can be imported by Vercel serverless runtime
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.main import app as fastapi_app


class VercelRewriteMiddleware:
    """
    ASGI middleware for Vercel Serverless Function rewrites.
    When Vercel rewrites /api/:path* to /api/index.py?__path__=/:path*,
    this middleware extracts __path__, normalizes the ASGI scope path to /api/...,
    and removes __path__ from the query string.
    """

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] == "http":
            query_string = scope.get("query_string", b"").decode("latin-1")
            if "__path__" in query_string:
                params = urllib.parse.parse_qs(query_string, keep_blank_values=True)
                if params.get("__path__"):
                    raw = params["__path__"][0].strip("/")
                    if not raw or raw == "api":
                        scope["path"] = "/api"
                    elif raw.startswith("api/"):
                        scope["path"] = f"/{raw}"
                    else:
                        scope["path"] = f"/api/{raw}"
                    del params["__path__"]
                    new_qs = urllib.parse.urlencode(params, doseq=True)
                    scope["query_string"] = new_qs.encode("latin-1")
        await self.app(scope, receive, send)


fastapi_app.add_middleware(VercelRewriteMiddleware)
app = fastapi_app
