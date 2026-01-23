# Document Converter

**Status:** ✅ Working

Converts Word documents to Markdown and PDF with automatic file watching.

## Features

- DOCX → Markdown conversion
- Markdown → PDF with styling
- Auto-watch mode: converts on file save
- Branded PDF output

## Requirements

```bash
pip install -r requirements.txt
```

Also requires **wkhtmltopdf** installed:
- Windows: `C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe`

## Usage

**Watch mode (auto-convert on changes):**
```bash
python watch_and_convert.py
```

**Single conversion:**
```bash
python convert_to_md.py
python md_to_pdf.py
```
