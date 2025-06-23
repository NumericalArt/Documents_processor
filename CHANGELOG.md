# Changelog

All notable changes to the Documents Processor project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of Documents Processor
- Support for multiple document formats (PDF, Word, Excel, PowerPoint, Images)
- Archive processing (ZIP, RAR) with size and file count limits
- AI-powered image description generation using OpenAI API
- Batch processing functionality for entire directories
- Comprehensive logging system with configurable levels
- Environment variable configuration support
- OCR support for images and scanned documents
- Structured output organization (images, tables, processed documents)

### Features
- **Multi-format Support**: PDF, DOCX, XLSX, PPTX, TXT, RTF, MD, ODT, EPUB, Images (JPG, PNG, HEIC, etc.)
- **Archive Processing**: ZIP and RAR archives with configurable limits
- **AI Integration**: OpenAI-powered image descriptions with customizable models
- **Batch Processing**: Process entire folders recursively
- **OCR Capabilities**: Extract text from images using Tesseract
- **Configurable Limits**: Page limits, file size limits, archive processing limits
- **Comprehensive Logging**: Detailed logging with file and console output
- **System Integration**: LibreOffice integration for document conversion

### Configuration
- Environment variable support for all major settings
- Configurable processing limits and timeouts
- Flexible API key management
- Platform-specific path configuration

### Output Management
- Organized output structure with separate directories
- Metadata extraction and documentation
- Image extraction and processing
- Table export to CSV format
- Structured text content extraction

## [1.0.0] - 2024-12-30

### Added
- Initial version of the Documents Processor
- Core document processing functionality
- Basic logging and error handling
- Support for common document formats

### Technical Details
- Python 3.7+ compatibility
- Comprehensive dependency management
- Error handling and recovery mechanisms
- Memory-efficient processing for large files