# AI Image Manager

**Status:** ✅ Working

A Flask web application for managing and browsing AI-generated images.

## Features

- Upload AI images with metadata (prompt, seed, model, parameters)
- Browse gallery with infinite scroll
- Search by prompt or tags
- Tag management
- Delete images

## Requirements

```bash
pip install -r requirements.txt
```

## Usage

```bash
python app.py
```

Then open http://localhost:5000

## Notes

- Images stored in `static/images/`
- Metadata in SQLite database `ai_images.db`
- Change `secret_key` in app.py for production use
