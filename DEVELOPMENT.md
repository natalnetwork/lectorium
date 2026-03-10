# Lectorium Development Guide

This document describes how to set up a local development environment
and how development for Lectorium is structured.

Lectorium is a self-hosted EPUB reader with audio narration that converts
EPUB books into spoken audio using the browser's built-in Text-to-Speech
engine.

------------------------------------------------------------------------

# Development Philosophy

Lectorium follows a minimal and pragmatic architecture.

Goals:

-   keep the system simple
-   avoid unnecessary dependencies
-   maintain clear module boundaries
-   implement features incrementally

General development pipeline:

upload → parse → store → render → speak

------------------------------------------------------------------------

# Local Development Setup

## Clone the repository

``` bash
git clone https://github.com/natalnetwork/lectorium.git
cd lectorium
```

## Create a virtual environment

``` bash
python -m venv .venv
source .venv/bin/activate
```

## Install dependencies

``` bash
pip install -e .
```

## Start development server

``` bash
uvicorn backend.app.main:app --reload
```

Open in browser:

http://127.0.0.1:8000

Health endpoint:

http://127.0.0.1:8000/health

------------------------------------------------------------------------

# Project Structure

Current project layout:

    lectorium
    │
    ├── backend
    │   └── app
    │       └── main.py
    │
    ├── deploy
    │   ├── Dockerfile
    │   ├── docker-compose.yml
    │   └── nginx.conf
    │
    ├── data
    │   ├── books
    │   ├── covers
    │   └── db
    │
    └── tests

Future backend layout:

    backend/app
    │
    ├── main.py
    ├── routes
    │   ├── api.py
    │   └── ui.py
    │
    ├── services
    │   ├── epub_service.py
    │   ├── ingest_service.py
    │   ├── library_service.py
    │   └── progress_service.py
    │
    ├── templates
    └── static

------------------------------------------------------------------------

# Running with Docker

From the repository root:

``` bash
docker compose -f deploy/docker-compose.yml up --build
```

Application:

http://127.0.0.1:8080

Health endpoint:

http://127.0.0.1:8080/health

------------------------------------------------------------------------

# Code Style

Guidelines:

-   Use Python type hints
-   Prefer small focused modules
-   Explicit error handling
-   Logging instead of print statements

Formatting:

    ruff

Testing:

    pytest

------------------------------------------------------------------------

# Testing

Tests are located in the `tests` directory.

Run tests with:

``` bash
pytest
```

------------------------------------------------------------------------

# Contribution Workflow

Typical workflow:

1.  Create a new branch
2.  Implement feature or fix
3.  Add or update tests
4.  Run formatting and tests
5.  Create a pull request

Example:

``` bash
git checkout -b feature/epub-import
```

------------------------------------------------------------------------

# Planned Milestones

## Milestone 1

-   FastAPI server skeleton
-   Docker setup
-   basic project structure

## Milestone 2

-   EPUB upload
-   EPUB parsing using ebooklib
-   metadata extraction
-   cover extraction

## Milestone 3

-   library grid UI
-   book selection

## Milestone 4

-   reader view
-   audio narration playback

## Milestone 5

-   progress tracking
-   resume playback

------------------------------------------------------------------------

# Future Development

Future features may include:

-   Calibre OPDS integration
-   watchfolder auto-import
-   multi-user support
-   server-side TTS engines
-   bookmarks
-   sleep timer
