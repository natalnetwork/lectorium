from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from backend.app.api.books import router as books_router
from backend.app.api.upload import router as upload_router

APP_TITLE = "Lectorium"

BASE_DIR = Path(__file__).resolve().parents[2]
STATIC_DIR = BASE_DIR / "backend" / "app" / "static"
TEMPLATE_DIR = BASE_DIR / "backend" / "app" / "templates"
COVERS_DIR = BASE_DIR / "data" / "covers"

app = FastAPI(title=APP_TITLE)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/covers", StaticFiles(directory=str(COVERS_DIR)), name="covers")

templates = Jinja2Templates(directory=str(TEMPLATE_DIR))

app.include_router(upload_router)
app.include_router(books_router)


@app.get("/health", response_class=JSONResponse)
async def health() -> dict[str, str]:
    return {"status": "ok", "app": APP_TITLE.lower()}


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": APP_TITLE,
        },
    )
