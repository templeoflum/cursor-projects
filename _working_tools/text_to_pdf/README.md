# Text to PDF Converter

**Status:** ✅ Working

Converts structured text files to formatted PDF documents.

## Features

- Section headers in `{curly braces}` trigger new pages
- Numbered sections trigger new pages
- Bullet points grouped together
- Auto page management

## Requirements

```bash
pip install -r requirements.txt
```

## Usage

1. Place your text in `NAD_outline.txt`
2. Run: `python convert.py`
3. Output: `output.pdf`
