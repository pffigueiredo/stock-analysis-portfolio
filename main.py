import logging
import os
from app.startup import startup
from nicegui import app, ui
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

# configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self' http: https: data: blob: 'unsafe-inline'; frame-ancestors https://app.build/ https://www.app.build/ https://staging.app.build/"
        return response


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "nicegui-app"}


# suppress sqlalchemy engine logs below warning level
logging.getLogger("sqlalchemy.engine.Engine").setLevel(logging.WARNING)

app.on_startup(startup)

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

ui.run(
    host="0.0.0.0",
    port=int(os.environ.get("NICEGUI_PORT", 8000)),
    reload=False,
    storage_secret=os.environ.get("NICEGUI_STORAGE_SECRET", "STORAGE_SECRET"),
    title="Created with ♥️ by app.build",
)
