# Lectorium Architecture

Lectorium is a self-hosted EPUB reader with audio narration that converts
EPUB books into spoken audio using the browser's built-in Text-to-Speech
capabilities.

The system is designed to be:

-   lightweight
-   privacy-friendly
-   easy to self-host
-   independent of external ebook databases

------------------------------------------------------------------------

# High Level Architecture

Lectorium follows a simple client/server architecture.

Browser (Client) \| v NGINX Reverse Proxy \| v FastAPI Backend \| +--
SQLite Database +-- EPUB Storage +-- Cover Storage

The browser renders the user interface and performs speech synthesis.
The backend manages the book library, metadata, and user progress.

------------------------------------------------------------------------

# Core Design Principles

## Independent Library

Lectorium **never reads the Calibre SQLite database directly**.

Books must be exported manually and uploaded to the server.

Calibre Library \| v User export \| v Upload to Lectorium \| v Lectorium
Library

This prevents corruption of existing ebook libraries.

------------------------------------------------------------------------

## Client-side Text-to-Speech

Speech generation happens entirely in the browser using the Web Speech
API.

Advantages:

-   no server-side audio generation
-   no GPU requirements
-   minimal infrastructure
-   immediate playback

The backend only delivers structured text.

------------------------------------------------------------------------

## Server-side Progress Tracking

Listening progress is stored on the server.

Benefits:

-   resume playback
-   multi-device support (future)
-   multi-user support (future)

Progress data is stored in SQLite.

------------------------------------------------------------------------

# Backend Architecture

The backend is implemented using **FastAPI**.

Responsibilities:

-   handle file uploads
-   parse EPUB files
-   extract metadata
-   extract cover images
-   manage the library
-   store reading progress
-   provide API endpoints

Future structure:

backend/app main.py routes/ services/ templates/ static/

Services will contain the main business logic.

Examples:

-   epub_service -- parse EPUB files
-   ingest_service -- import uploaded books
-   library_service -- manage library entries
-   progress_service -- store reading progress

------------------------------------------------------------------------

# Storage Layout

Persistent data is stored in the `data` directory.

data ├── books │ stored EPUB files │ ├── covers │ extracted cover images
│ └── db SQLite database

Books are copied into the Lectorium storage directory when uploaded.

------------------------------------------------------------------------

# Deployment Architecture

Lectorium runs inside Docker containers.

Docker ├── nginx container └── lectorium container FastAPI application

NGINX acts as a reverse proxy and exposes the application to the
network.

------------------------------------------------------------------------

# Technology Stack

Backend

-   Python
-   FastAPI

Frontend

-   HTMX
-   AlpineJS

Database

-   SQLite

EPUB Processing

-   ebooklib

Deployment

-   Docker
-   NGINX

------------------------------------------------------------------------

# Future Extensions

The architecture is designed to support future features.

Planned additions:

-   Calibre OPDS import
-   watchfolder auto-import
-   Calibre plugin integration
-   multi-user accounts
-   server-side TTS engines
-   word-level highlighting
-   bookmarks
-   sleep timer
