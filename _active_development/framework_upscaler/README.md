# AI Framework Upscaler

**Status:** 🔨 In Development

A GUI tool that takes skeleton framework documents and uses Google Gemini AI to expand them into fully detailed documents.

## What It Does

- Load framework content in YAML, JSON, or Markdown format
- AI expands sections: Vision, Inspiration, Core Principles, Tools, Methods, Conclusion
- Expands phase-based structures with purposes and actions
- Export to your preferred format

## Requirements

```bash
pip install -r requirements.txt
```

- `requests`
- `python-dotenv`
- `pyyaml`

## Setup

1. Get a Google Gemini API key
2. Create `.env` file with: `GEMINI_API_KEY=your_key_here`

## Usage

```bash
python FDE.py
```

## Future Ideas

- Rethink the framework structure
- Add more AI models
- Batch processing
