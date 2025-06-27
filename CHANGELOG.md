# Changelog

All notable changes to the Documents Processor project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Completed (December 2024)
- **CLEANUP**: Removed unused Tesseract/OCR dependencies and redundant setup.py
- **DOCS**: Comprehensive documentation update reflecting AI Vision capabilities
- **INSTALL**: Simplified cross-platform installation (removed tesseract dependency)
- **ARCHITECTURE**: Streamlined project structure for single-module design
- **STRUCTURED PROCESSING**: Added comprehensive structured report processing with AI-powered extraction
- **SCHEMA SIMPLIFICATION**: Removed JSON schema system in favor of self-sufficient prompts

*📦 [View complete archive](docs/archive/tesseract-removal-archive-2024-12-30.md)*

### Added
- Initial release of Documents Processor
- Support for multiple document formats (PDF, Word, Excel, PowerPoint, Images)
- Archive processing (ZIP, RAR) with size and file count limits
- AI-powered image description generation using OpenAI API
- **Structured Report Processing**: AI-powered extraction of structured information from processing reports
- **Tiered Caching System**: Memory + disk caching with TTL for optimal performance
- **Prompt Management**: Flexible prompt-based processing without rigid schemas
- Batch processing functionality for entire directories
- Comprehensive logging system with configurable levels
- Environment variable configuration support
- Structured output organization (images, tables, processed documents)

### Features
- **Multi-format Support**: PDF, DOCX, XLSX, PPTX, TXT, RTF, MD, ODT, EPUB, Images (JPG, PNG, HEIC, etc.)
- **Archive Processing**: ZIP and RAR archives with configurable limits
- **AI Integration**: OpenAI-powered image descriptions with customizable models
- **Structured Processing**: Extract structured data from processing reports using configurable prompts
- **Advanced Caching**: Multi-level caching system for API optimization
- **Batch Processing**: Process entire folders recursively
- **AI Image Analysis**: Extract information from images using OpenAI Vision API
- **Configurable Limits**: Page limits, file size limits, archive processing limits
- **Comprehensive Logging**: Detailed logging with file and console output
- **System Integration**: LibreOffice integration for document conversion

### Configuration
- Environment variable support for all major settings
- Configurable processing limits and timeouts
- Flexible API key management
- Platform-specific path configuration
- **Prompt-based Architecture**: Self-sufficient prompts with embedded JSON structure definitions

### Output Management
- Organized output structure with separate directories
- Metadata extraction and documentation
- Image extraction and processing
- Table export to CSV format
- Structured text content extraction
- **JSON Results**: Structured extraction results with comprehensive metadata

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