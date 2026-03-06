# Lectorium

**Self-hosted EPUB audiobook reader with browser-based Text-to-Speech
(TTS).**

Lectorium turns your personal EPUB library into a listenable audiobook
experience directly in the browser. It is designed to be lightweight,
privacy-friendly, and easy to self-host.

Unlike cloud-based audiobook readers, Lectorium runs entirely on your
own infrastructure and uses the browser's native speech synthesis
capabilities.

------------------------------------------------------------------------

# Features

## Core Features (MVP)

-   Upload EPUB files via web interface
-   Build a private server-side book library
-   Cover-based library browsing
-   EPUB chapter navigation
-   Browser-based Text-to-Speech playback
-   Resume listening from last position
-   Responsive UI for desktop and mobile

## Planned Features

-   Calibre OPDS import
-   Watchfolder auto-import
-   Bookmarks ("audio markers")
-   Multi-user support
-   Server-side TTS engines
-   Word-level highlighting
-   Sleep timer

------------------------------------------------------------------------

# Why Lectorium?

Many existing text-to-speech readers rely on cloud services and
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
       ├── SQLite Database
       ├── EPUB storage
       └── Cover storage

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

Current goals:

-   establish stable architecture
-   implement EPUB import
-   build minimal reader interface
-   integrate browser TTS playback

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
uvicorn backend.app.main:app --reload
```

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

# Repository Structure

    lectorium
    │
    ├── backend
    │   └── app
    │       ├── routes
    │       ├── services
    │       ├── templates
    │       └── static
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
