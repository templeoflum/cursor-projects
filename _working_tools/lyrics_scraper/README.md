# Genius Lyrics Scraper

**Status:** ✅ Working

CLI tool to search artists, scrape lyrics from Genius.com, and store locally.

## Features

- Search Genius for artists
- Browse song lists
- Scrape full lyrics
- Store in local SQLite database
- View saved lyrics by artist

## Requirements

```bash
pip install -r requirements.txt
```

## Setup

1. Get API token from https://genius.com/api-clients
2. Create `.env` file: `GENIUS_API_TOKEN=your_token_here`

## Usage

```bash
cd lyric
python main.py
```

Follow the interactive menu.
