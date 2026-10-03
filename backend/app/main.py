"""FastAPI factory and frontend delivery for the separated MVP."""

from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.app.api import router as api_router
from backend.app.services import normalize_symbol
from config.settings import Config
from data.database import DatabaseManager

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIR = PROJECT_ROOT / "frontend"

LOCALHOST_ORIGINS = [
    "http://localhost:5000",
    "http://127.0.0.1:5000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]


def _error_message(detail) -> str:
    return detail if isinstance(detail, str) else "Request failed"


def create_app(config_class=Config) -> FastAPI:
    """Create an API application that serves a static, API-only frontend."""
    app = FastAPI(title="StockPredict API", version="1.0.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=LOCALHOST_ORIGINS,
        allow_credentials=False,
        allow_methods=["GET"],
        allow_headers=["Content-Type"],
    )
    app.state.db = DatabaseManager(db_path=config_class.DATABASE_PATH)

    @app.exception_handler(HTTPException)
    async def http_error_handler(_: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"success": False, "error": _error_message(exc.detail)},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(_: Request, __: RequestValidationError):
        return JSONResponse(status_code=422, content={"success": False, "error": "Invalid request"})

    @app.exception_handler(Exception)
    async def unexpected_error_handler(_: Request, __: Exception):
        return JSONResponse(status_code=500, content={"success": False, "error": "Internal server error"})

    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIR / "assets")), name="assets")
    app.include_router(api_router)

    @app.get("/", include_in_schema=False)
    async def dashboard():
        return FileResponse(FRONTEND_DIR / "index.html")

    @app.get("/symbol/{symbol}", include_in_schema=False)
    async def symbol_page(symbol: str):
        normalize_symbol(symbol)
        return FileResponse(FRONTEND_DIR / "symbol.html")

    return app
