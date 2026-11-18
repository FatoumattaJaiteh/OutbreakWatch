import sys
import os
import logging

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.core.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("outbreakwatch")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Public Health Outbreak Surveillance & Rapid Case Reporting System API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

# CORS Middleware setup - fully permissive for localhost, 127.0.0.1, Live Server (5500), and all ports
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:5000",
        "http://127.0.0.1:5000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "null",
    ],
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1|0\.0\.0\.0)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 router
app.include_router(api_router, prefix=settings.API_V1_STR)


from fastapi.responses import HTMLResponse

@app.get("/", tags=["Health"], response_class=HTMLResponse)
def root():
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>OutbreakWatch API &bull; Ministry of Health, The Gambia</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0b2545; color: #fff; margin: 0; padding: 40px 20px; display: flex; justify-content: center; align-items: center; min-height: 80vh; }}
        .card {{ background: #132f54; border: 1px solid #1e4976; border-radius: 16px; max-width: 650px; width: 100%; padding: 32px; box-shadow: 0 20px 40px rgba(0,0,0,0.4); }}
        h1 {{ font-size: 24px; color: #38bdf8; margin: 0 0 8px; }}
        p {{ color: #cbd5e1; font-size: 14px; line-height: 1.6; }}
        .badge {{ display: inline-block; background: #059669; color: #fff; padding: 4px 10px; border-radius: 999px; font-size: 12px; font-weight: bold; margin-bottom: 20px; }}
        .btn {{ display: inline-block; background: #dc2626; color: #fff; padding: 10px 18px; border-radius: 8px; text-decoration: none; font-size: 13px; font-weight: bold; margin: 6px 6px 6px 0; transition: background 0.2s; }}
        .btn:hover {{ background: #b91c1c; }}
        .btn-alt {{ background: #0284c7; }}
        .btn-alt:hover {{ background: #0369a1; }}
        .notice {{ background: #07172c; border-left: 4px solid #f59e0b; padding: 12px 16px; border-radius: 6px; margin-top: 20px; font-size: 12px; color: #fde68a; }}
    </style>
</head>
<body>
    <div class="card">
        <span class="badge">&bull; Operational - Live</span>
        <h1>{settings.PROJECT_NAME}</h1>
        <p>Public Health Outbreak Surveillance & Rapid Case Reporting Backend API (v{settings.VERSION}). Running on FastAPI with Supabase cloud database integration.</p>
        <div style="margin-top: 24px;">
            <a href="{settings.API_V1_STR}/docs" class="btn btn-alt" target="_blank">&rarr; Interactive Swagger Docs</a>
            <a href="http://127.0.0.1:3000" class="btn" target="_blank">&rarr; Open Frontend (Port 3000)</a>
            <a href="http://127.0.0.1:5500" class="btn" target="_blank">&rarr; Open Live Server (Port 5500)</a>
        </div>
        <div class="notice">
            <strong>Note for Web Browsers:</strong> Always access this backend via <code>http://127.0.0.1:8000</code> or <code>http://localhost:8000</code>. Do not type <code>0.0.0.0</code> in browser address bars as it is rejected by browsers.
        </div>
    </div>
</body>
</html>"""


@app.get("/api/v1/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "service": settings.PROJECT_NAME, "version": settings.VERSION}


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("  OutbreakWatch Backend API is Active & Listening!")
    print("=" * 70)
    print("  👉 Open in your web browser (Chrome / Edge / Firefox):")
    print("     http://127.0.0.1:8000/   or   http://localhost:8000/")
    print("")
    print("  👉 Swagger Interactive API Documentation:")
    print("     http://127.0.0.1:8000/api/v1/docs")
    print("")
    print("  👉 Frontend Web Applications:")
    print("     http://127.0.0.1:3000/   or   http://localhost:3000/")
    print("     (or if using VS Code Live Server: http://127.0.0.1:5500/)")
    print("")
    print("  ⚠️  IMPORTANT NOTICE:")
    print("     DO NOT type 'http://0.0.0.0:8000' in Google Chrome.")
    print("     '0.0.0.0' is a server interface binding address, NOT a web URL.")
    print("     Chrome will show 'ERR_ADDRESS_INVALID' if you type 0.0.0.0.")
    print("     Always use 'http://127.0.0.1:8000' or 'http://localhost:8000'.")
    print("=" * 70 + "\n")
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)


