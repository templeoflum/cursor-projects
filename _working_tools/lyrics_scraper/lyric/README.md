# Genius Lyrics Scraper

A Python application for scraping and storing lyrics from Genius.com.

## Features
- Search for artists on Genius
- Scrape lyrics from artist's songs
- Store lyrics in a SQLite database
- Simple command-line interface

## Setup
1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the project root and add your Genius API token:
```
GENIUS_API_TOKEN=your_token_here
```

You can get a Genius API token by:
1. Going to https://genius.com/api-clients
2. Creating an account/logging in
3. Creating a new API Client
4. Copying the Client Access Token

## Usage
Run the main script:
```bash
python main.py
```

Follow the prompts to:
1. Search for an artist
2. Select songs to scrape
3. View stored lyrics 