# Changelog

All notable changes to this project will be documented in this file.

## [0.1.2] - 2025-01-08

### Removed
- Removed JavaScript version of the processor (pdfToTableProcessor.js)
- Removed Node.js dependencies and configuration
- Cleaned up node_modules directory

### Changed
- Project now exclusively uses Python implementation
- Updated package.json to remove Node.js configuration

## [0.1.1] - 2025-01-08

### Changed
- Project renamed to PDFTableParser
- Updated package.json with new project name

## [0.1.0] - 2025-01-08

### Added
- Initial project setup
- Core PDF processing functionality
  - PDF to high-resolution image conversion
  - Claude Vision API integration
  - CSV output generation
- Environment variable support
- Comprehensive error handling and logging
- Project documentation
  - README.md
  - .gitignore
  - .env.example

### Technical Details
- Base resolution: 300 DPI for image conversion
- Output encoding: UTF-8-SIG for special character support
- Default values:
  - Quantity: 1 (when not found)
  - UOM: 'BOX' (when not found)

### Known Limitations
- Processing time may vary based on PDF size and complexity
- API rate limits depend on Anthropic account tier
- Memory usage scales with PDF page count

### File Structure
```
fr8labs-populate-commodities/
├── pdf_to_table_processor.py  # Main processing script
├── .env.example              # Environment variable template
├── .gitignore               # Git ignore rules
├── README.md                # Project documentation
└── CHANGELOG.md             # Change history
```

### Routes and Paths
- Input: `cipl/venus_beauty_packing_list.pdf`
- Output: `[original_filename]_[timestamp].csv`
- Temporary: `pdf_images_[timestamp]/`

## [0.2.0] - 2025-01-08

### Added
- JavaScript version of PDF processor (`pdfToTableProcessor.js`)
- Node.js package configuration (`package.json`)
- Support for modern Node.js features and libraries:
  - pdf-lib for PDF processing
  - sharp for image manipulation
  - winston for logging
  - @anthropic-ai/sdk for Claude Vision API

### Technical Details
- Maintained same functionality as Python version
- Enhanced error handling with async/await patterns
- UTF-8-SIG encoding for CSV output
- Base64 image processing for Claude Vision API

### File Structure Updates
```
fr8labs-populate-commodities/
├── pdf_to_table_processor.py    # Original Python script
├── pdfToTableProcessor.js       # New JavaScript version
├── package.json                 # Node.js dependencies
├── .env.example                # Environment variable template
├── .gitignore                 # Git ignore rules
├── README.md                  # Project documentation
└── CHANGELOG.md               # Change history
