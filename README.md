# Lectorium

[![CI](https://github.com/natalnetwork/lectorium/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/natalnetwork/lectorium/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/natalnetwork/lectorium/branch/main/graph/badge.svg)](https://codecov.io/gh/natalnetwork/lectorium)
[![Tests](https://img.shields.io/badge/tests-pytest-brightgreen.svg)](https://github.com/natalnetwork/lectorium/actions/workflows/ci.yml)
[![Lint](https://img.shields.io/badge/lint-ruff-brightgreen.svg)](https://github.com/natalnetwork/lectorium/actions/workflows/ci.yml)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-compose-blue.svg)](deploy/docker-compose.yml)

**A self-hosted EPUB reader with audio narration.**

## Local Quality Checks

These commands are used to keep the workspace clean locally:

``` bash
python -m pytest
python -m ruff check .
python -m ruff format --check .
python -m pyright
```

Lectorium turns your personal EPUB library into a listenable narrated
experience directly in the browser. It is designed to be lightweight,
privacy-friendly, and easy to self-host.

Unlike cloud-based audio narration readers, Lectorium runs entirely on your
own infrastructure and uses the browser's native speech synthesis
capabilities.

------------------------------------------------------------------------

# Features

## Core Features (MVP)

-   Upload EPUB files via web interface
-   Build a private server-side book library
-   Cover-based library browsing
-   EPUB chapter navigation
-   Audio narration playback
-   Resume listening from last position
-   Responsive UI for desktop and mobile

## Planned Features

-   Calibre OPDS import
-   Watchfolder auto-import
-   Bookmarks ("audio markers")
-   Multi-user support
-   Server-side TTS engines
-   Pause/Resume (returning with new TTS integration)
-   Word-level highlighting
-   Sleep timer

------------------------------------------------------------------------

# Why Lectorium?

Many existing audio narration readers rely on cloud services and
subscription models.

Lectorium takes a different approach:

-   **Self-hosted**
-   **Open source**
-   **No subscriptions**
-   **Privacy-first**
-   **Lightweight infrastructure**

The system uses browser-native speech synthesis instead of generating
audio on the server, which keeps the system simple and efficient.

------------------------------------------------------------------------

# Architecture

Lectorium follows a simple architecture:

    Browser
       │
       ▼
    NGINX (reverse proxy)
       │
       ▼
     FastAPI Backend
         │
         ├── JSON library database
         ├── EPUB storage
         ├── Cover storage
         └── Progress tracking

Key design principles:

-   The server maintains its own independent library
-   The Calibre database is never accessed directly
-   Audio playback happens entirely in the browser
-   Reading progress is stored server-side

------------------------------------------------------------------------

# Technology Stack

Backend

-   Python 3.12
-   FastAPI

Frontend

-   HTMX
-   Alpine.js

Database

-   SQLite

EPUB Processing

-   ebooklib

Deployment

-   Docker
-   NGINX reverse proxy

------------------------------------------------------------------------

# Project Status

Early development -- MVP phase.

Pause/Resume is currently deferred until the next TTS integration to ensure
consistent audio across browsers.

Current goals:

-   establish stable architecture
-   implement EPUB import
-   build minimal reader interface
-   integrate audio narration playback

------------------------------------------------------------------------

# Getting Started

## Clone the Repository

``` bash
git clone https://github.com/natalnetwork/lectorium.git
cd lectorium
```

------------------------------------------------------------------------

# Local Development

Create virtual environment:

``` bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

``` bash
pip install -e .
```

Start development server:

``` bash
lectorium
```

The `lectorium` command is installed by the editable install above and
starts `uvicorn backend.app.main:app --reload` on `127.0.0.1:8000`.

You can override the host, port, and reload behavior via environment variables:

| Variable | Default | Description |
| --- | --- | --- |
| `LECTORIUM_HOST` | `127.0.0.1` | Bind address |
| `LECTORIUM_PORT` | `8000` | Port |
| `LECTORIUM_RELOAD` | `true` | Reload on changes (true/false, 1/0, yes/no, on/off) |

``` bash
LECTORIUM_HOST=0.0.0.0 LECTORIUM_PORT=8080 LECTORIUM_RELOAD=false lectorium
```

Background commands for local usage:

``` bash
lectorium start
lectorium status
lectorium stop
```

These commands write a pid file (.lectorium.pid) and log output to
.lectorium.log in the project root.
If a stale or running pid is detected, `lectorium start` will restart it.

Open in browser:

    http://127.0.0.1:8000

Health check:

    http://127.0.0.1:8000/health

------------------------------------------------------------------------

# Docker Deployment

Run with Docker Compose:

``` bash
docker compose -f deploy/docker-compose.yml up --build
```

Open:

    http://127.0.0.1:8080

Health endpoint:

    http://127.0.0.1:8080/health

------------------------------------------------------------------------

# Production (systemd)

An example unit file is available in deploy/lectorium.service. Adjust the
working directory and paths to match your server setup, then install:

``` bash
sudo cp deploy/lectorium.service /etc/systemd/system/lectorium.service
sudo systemctl daemon-reload
sudo systemctl enable --now lectorium
```

Status and logs:

``` bash
systemctl status lectorium
journalctl -u lectorium -f
```

------------------------------------------------------------------------

# Repository Structure

    lectorium
    │
    ├── backend
    │   └── app
    │       ├── api
    │       ├── models
    │       ├── services
    │       ├── templates
    │       ├── static
    │       └── main.py
    │
    ├── deploy
    │   ├── Dockerfile
    │   ├── docker-compose.yml
    │   ├── lectorium.service
    │   └── nginx.conf
    │
    ├── data
    │   ├── books
    │   ├── covers
    │   └── db
    │       ├── library.json
    │       └── progress.json
    │
    └── tests

------------------------------------------------------------------------

# Security Model

Lectorium is designed to protect your ebook library:

-   The Calibre SQLite database is **never accessed directly**
-   EPUB files are copied into the server library
-   Metadata is extracted and stored independently
-   Progress tracking is server-controlled

This prevents accidental corruption of existing ebook libraries.

------------------------------------------------------------------------

# Roadmap

Planned milestones:

1.  EPUB upload and library management
2.  Reader interface
3.  Browser-based TTS playback
4.  Progress tracking
5.  OPDS integration
6.  Multi-user support

------------------------------------------------------------------------

# Contributing

Contributions are welcome.

Typical areas for contributions:

-   EPUB parsing improvements
-   UI/UX enhancements
-   accessibility improvements
-   additional import mechanisms

Please open an issue before submitting major changes.

------------------------------------------------------------------------

# License

MIT License

------------------------------------------------------------------------

# Acknowledgements

Lectorium builds on the work of several open-source projects:

-   FastAPI
-   ebooklib
-   HTMX
-   Alpine.js
