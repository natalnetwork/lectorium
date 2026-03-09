You are a senior Python backend engineer.

We are building a self-hosted EPUB audiobook reader called "Lectorium".
The stack is:

- Python 3.12
- FastAPI
- Jinja2
- ebooklib
- Docker deployment
- nginx reverse proxy

Current status:

The project skeleton is running.
FastAPI app works.
Health endpoint exists.
Docker + nginx are configured.

Goal of this milestone:
Implement the EPUB ingestion pipeline.

Architecture principle:
Keep modules small and focused.

Pipeline:

upload → storage → epub parsing → metadata extraction → library index

Requirements:

1. Create an upload endpoint

POST /upload

Accept multipart file uploads.

Only allow files with extension `.epub`.

2. Store uploaded files

Create directory:

data/books/

Save uploaded EPUB files there using a UUID filename.

3. Parse EPUB

Use ebooklib to open the book.

Extract:

title
author
language
table of contents
chapters

4. Extract chapters

Create a simple structure:

Book
  id
  title
  author
  chapters

Chapter
  title
  html_content

5. Create Python modules

backend/app/services/storage.py

Responsible for:
saving uploaded files
generating UUID filenames
returning file paths

backend/app/services/epub_parser.py

Responsible for:
loading EPUB
extracting metadata
extracting chapters

backend/app/models/book.py

Pydantic models:

Book
Chapter

6. Create endpoint

backend/app/api/upload.py

FastAPI router

POST /upload
returns extracted metadata.

7. Register router in main.py

Include router:

app.include_router(upload_router)

8. Minimal logging

Use standard Python logging.

9. Keep implementation simple.

No database yet.
No authentication yet.
No async complexity unless necessary.

Return JSON like:

{
  "title": "...",
  "author": "...",
  "chapters": 12
}

Goal:
First working EPUB ingestion pipeline.