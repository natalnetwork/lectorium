from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

APP_TITLE = "Lectorium"
BASE_DIR = Path(__file__).resolve().parents[2]
STATIC_DIR = BASE_DIR / "backend" / "app" / "static"

app = FastAPI(title=APP_TITLE)

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/health", response_class=JSONResponse)
async def health() -> dict[str, str]:
    return {"status": "ok", "app": APP_TITLE.lower()}


@app.get("/", response_class=HTMLResponse)
async def index() -> str:
    return """
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Lectorium</title>
        <style>
          body {
            font-family: system-ui, sans-serif;
            max-width: 900px;
            margin: 3rem auto;
            padding: 0 1rem;
            line-height: 1.5;
            background: #111827;
            color: #f9fafb;
          }
          .card {
            border: 1px solid #374151;
            background: #1f2937;
            border-radius: 12px;
            padding: 1.5rem;
          }
          code {
            background: #111827;
            padding: 0.15rem 0.35rem;
            border-radius: 6px;
          }
          a {
            color: #93c5fd;
          }
        </style>
      </head>
      <body>
        <div class="card">
          <h1>Lectorium</h1>
          <p>Self-hosted EPUB audiobook reader with browser TTS.</p>
          <p>Project skeleton is running.</p>
          <p>Health endpoint: <a href="/health"><code>/health</code></a></p>
        </div>
      </body>
    </html>
    """
