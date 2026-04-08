# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Flask web app that generates QR code sticker-sheet PDFs for Discogs vinyl/record collections. Users authenticate via Discogs OAuth, browse their collection (by folder or format), and export selected releases as printable PDF sheets with QR codes linking to Discogs release pages.

## Commands

```bash
# Install dependencies (uses uv)
uv sync

# Run dev server
uv run flask --app pydiscogsqrcodegenerator run --port 5001 --debug

# Run all tests
uv run pytest

# Run a single test file or test
uv run pytest tests/test_pdf_service.py
uv run pytest tests/test_pdf_service.py::test_function_name

# Run with coverage
uv run pytest --cov=pydiscogsqrcodegenerator

# Docker
docker compose up
```

## Architecture

**Package**: `src/pydiscogsqrcodegenerator/` — the active package (built via hatch). There is also `src/pydiscogstoqrfactory/` which is a copy/older name; the wheel only includes `pydiscogsqrcodegenerator`.

**App factory**: `__init__.py` → `create_app()` creates the Flask app, initializes SQLAlchemy + Flask-Session, registers blueprints, and runs lightweight schema migrations on startup.

**Blueprints** (in `blueprints/`):
- `auth` — Discogs OAuth flow (request token → authorize → callback → store access token)
- `collection` — browse collection by folder or by format/size, with sorting and filtering
- `export` — generate PDF sticker sheets and CSV exports
- `settings` — user preferences (bottom text template, printer offsets, sticker layouts)

**Services**:
- `discogs_service.py` — wraps `python3-discogs-client`. Caches collection data in a module-level dict with 5-min TTL. Handles folder browsing, format filtering, size inference, and release normalization.
- `pdf_service.py` — generates QR codes with Discogs logo overlay (segno + Pillow), renders sticker-sheet PDFs (fpdf2) with configurable grid layouts. Includes Unicode font support with fallback chain.
- `csv_service.py` — generates CSV output using a template file (`templates/qrfactory_discogs_collection_template.csv`) with placeholder substitution.

**Models** (`models.py`): `OAuthToken`, `ProcessedRelease`, `StickerLayout`, `UserSettings` — all SQLAlchemy, stored in SQLite (`instance/app.db`).

**Templates**: Jinja2 templates in top-level `templates/` directory (not inside the package). Static assets (JS, CSS, fonts, logo) are in `src/pydiscogsqrcodegenerator/static/`.

**Config** (`config.py`): `DevelopmentConfig`, `TestConfig`, `ProductionConfig` selected via `FLASK_ENV`. Discogs API credentials come from environment variables.

## Environment Variables

Requires a `.env` file with: `DISCOGS_CONSUMER_KEY`, `DISCOGS_CONSUMER_SECRET`, `SECRET_KEY`, `FRONTEND_URL`, `USERAGENT`.

## Testing

Tests use pytest with `TestConfig` (in-memory SQLite). Fixtures in `tests/conftest.py` provide `app`, `client`, `db`, and `sample_releases`. Tests mock the Discogs API client; they don't make real API calls.
