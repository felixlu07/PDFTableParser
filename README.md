# PDF Table Extractor

A Python-based tool that processes PDFs into standardized table formats using Anthropic's Claude Vision API. The tool converts PDF pages into high-resolution images and extracts structured data into CSV format.

## Features

- High-resolution PDF to image conversion (300 DPI)
- Automatic handling of portrait and landscape orientations
- Structured data extraction using Claude Vision API
- CSV output with UTF-8 encoding support
- Comprehensive error handling and logging
- Timestamped output files

## Prerequisites

- Python 3.8+
- `pdf2image` library
- Anthropic API key

## Installation

1. Clone the repository
2. Create and activate a virtual environment (recommended)
3. Install dependencies:
```powershell
pip install anthropic pdf2image pillow python-dotenv
```

## Configuration

1. Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```

2. Edit `.env` and add your Anthropic API key:
```
ANTHROPIC_API_KEY=your-api-key-here
```

## Usage

1. Place your PDF file in the desired directory
2. Run the script:
```powershell
python pdf_to_table_processor.py
```

The script will:
- Convert the PDF to high-resolution images
- Process each page using Claude Vision API
- Generate a CSV file with extracted data
- Include timestamps in output filenames

## Output Format

The CSV output includes the following columns:
- Commodity Name
- Qty (defaults to 1 if not found)
- UOM (defaults to 'BOX' if not found)

## Error Handling

The script includes comprehensive error handling and logging:
- All operations are logged to console
- Errors are caught and reported clearly
- Processing continues even if individual pages fail

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
