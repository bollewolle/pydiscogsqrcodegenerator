# PyDiscogsToQRFactory

A web application that connects to the Discogs API to retrieve your record collection and generates CSV files compatible with [QR Factory 3](https://www.tunabellysoftware.com/qrfactory/) for printing QR code stickers for your physical releases.

## Features

- **Discogs OAuth Authentication** — Secure web-based OAuth 1.0a login
- **Auto-authentication** — Automatically uses stored credentials from `.env` or database
- **Browse Collection Folders** — Navigate your Discogs collection by folder
- **Latest Additions** — Find releases added since a specific date
- **Sorting** — Sort by Artist (A-Z/Z-A), Year (Newest/Oldest), or Date Added
- **Flexible Selection** — Select individual releases, all releases, or filter by artist starting letter
- **CSV Preview & Edit** — Review and modify CSV output before downloading
- **QR Factory 3 Format** — Generates CSV in the exact format expected by QR Factory 3
- **Processing Tracker** — Keeps track of releases already processed to avoid duplicates

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- [mise](https://mise.jdx.dev/) (optional, for environment management)
- A [Discogs developer application](https://www.discogs.com/settings/developers) (for API credentials)
- [QR Factory 3](https://www.tunabellysoftware.com/qrfactory/) (macOS app for generating QR codes)

## Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd pydiscogstoqrfactory
```

### 2. Set up environment variables

```bash
cp .env.example .env
```

Edit `.env` and add your Discogs API credentials:

```env
DISCOGS_CONSUMER_KEY=your_consumer_key
DISCOGS_CONSUMER_SECRET=your_consumer_secret
```

Optionally, if you already have OAuth tokens:

```env
DISCOGS_OAUTH_TOKEN=your_oauth_token
DISCOGS_OAUTH_TOKEN_SECRET=your_oauth_token_secret
```

### 3. Install dependencies

```bash
uv sync
```

### 4. Run the application

```bash
uv run flask run
```

The app will be available at `http://localhost:5000`.

## Usage

1. **Login** — Click "Login with Discogs" to authenticate via OAuth, or the app will auto-authenticate if credentials are configured in `.env`.

2. **Browse** — Choose between "Browse Folders" to navigate your collection by folder, or "Latest Additions" to find recently added releases.

3. **Select** — Use checkboxes to select individual releases, or use "Select All" / letter filters. Releases previously processed are marked with a "Processed" badge.

4. **Preview** — Click "Preview CSV" to see the generated QR Factory 3 CSV data.

5. **Edit (optional)** — Click "Edit Before Download" to modify the BottomText, Content URL, or FileName for any release.

6. **Download** — Click "Download CSV" to get the file, then import it into QR Factory 3.

## Development

### Running tests

```bash
uv run pytest
```

With coverage:

```bash
uv run pytest --cov=pydiscogstoqrfactory
```

### Project structure

```
src/pydiscogstoqrfactory/
├── __init__.py            # App factory
├── config.py              # Configuration classes
├── extensions.py          # Flask extensions
├── models.py              # Database models
├── discogs_service.py     # Discogs API wrapper
├── csv_service.py         # CSV generation service
├── blueprints/
│   ├── auth.py            # OAuth authentication routes
│   ├── collection.py      # Collection browsing routes
│   └── export.py          # CSV export routes
├── templates/             # Jinja2 HTML templates
└── static/                # CSS and JavaScript
```

### QR Factory 3 CSV format

The CSV template is defined in `templates/qrfactory_discogs_collection_template.csv`. Each row represents a QR code with:

- **Type**: URL
- **Content**: Link to the Discogs release page
- **BottomText**: `Artist – Title [Year] – Folder`
- **FileName**: The Discogs release ID
- **Icon**: Discogs record icon overlay

## License

MIT
