from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from backend.app.api.books import router as books_router
from backend.app.api.upload import router as upload_router
from backend.app.database import init_db

APP_TITLE = "Lectorium"

BASE_DIR = Path(__file__).resolve().parents[2]
STATIC_DIR = BASE_DIR / "backend" / "app" / "static"
TEMPLATE_DIR = BASE_DIR / "backend" / "app" / "templates"
COVERS_DIR = BASE_DIR / "data" / "covers"
FAVICON_PATH = STATIC_DIR / "favicon.svg"
BOOK_ASSETS_DIR = BASE_DIR / "data" / "book-assets"

COVERS_DIR.mkdir(parents=True, exist_ok=True)
BOOK_ASSETS_DIR.mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    init_db()
    yield


app = FastAPI(title=APP_TITLE, lifespan=lifespan)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/covers", StaticFiles(directory=str(COVERS_DIR)), name="covers")
app.mount("/book-assets", StaticFiles(directory=str(BOOK_ASSETS_DIR)), name="book-assets")

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


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    if FAVICON_PATH.exists():
        return FileResponse(str(FAVICON_PATH))
    return JSONResponse(status_code=404, content={"detail": "Not found"})
