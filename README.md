# Documents Processor 📄🔍

A comprehensive Python utility for processing and extracting content from various document formats with AI-powered image analysis capabilities.

## ✨ Features

### 🚀 Advanced Document Processing
- **📄 Universal Format Support**: Process PDF, Word, Excel, PowerPoint, text files, images, and archives with intelligent format detection
- **🤖 AI-Powered Image Analysis**: Generate intelligent descriptions of embedded images using OpenAI's Vision API
- **📍 In-Context Image Descriptions**: Text descriptions saved at original location in source text, maintaining document flow
- **🖼️ Unified Image Storage**: All images (PDF embedded, archive extracted, direct processed) saved to unified `images/` folder with unique naming
- **📊 Smart Table Extraction**: Automatic extraction and separate storage of tables in `tables/` folder with reference links
- **🔄 Batch Processing Utility**: Mass document processing via `process_all_to_markdown.py` for entire folder hierarchies

### 🏗️ Professional Architecture  
- **🎯 Universal Document Class**: Process any file type with graceful format handling and error recovery
- **📁 Recursive Folder Processing**: Handle complex folder structures and subfolders automatically
- **📝 Structured Markdown Output**: Well-formatted output optimized for LLM processing and analysis
- **🔧 Cleanup Management**: Professional cleanup utility with safety features, backup system, and interactive controls
- **⚙️ Configurable Processing**: Control limits for pages, file sizes, archive contents, and Vision API calls

### 🔍 Information Extraction & RAG Systems
- **🎯 Mass Information Extraction**: Powerful utility for extracting specific data across document collections
- **🧠 RAG System Building**: Advanced capabilities for building Retrieval-Augmented Generation systems
- **📈 Structured Data Analysis**: Extract and organize information for further AI processing and analysis
- **🔄 Batch Analysis Workflows**: Process large document collections with comprehensive reporting
- **📊 Comprehensive Reporting**: Detailed processing reports with statistics, errors, and extracted content
- **🏗️ Structured Report Processing**: AI-powered extraction of structured information from processing reports using configurable JSON schemas

### 🛠️ Technical Excellence
- **🔒 Local Processing**: All document processing happens locally with optional AI features
- **📱 Cross-Platform Support**: Works on Windows, macOS, and Linux with platform-specific optimizations
- **⚡ Memory Efficient**: Process large documents without loading entire files into memory
- **📋 Comprehensive Logging**: Detailed logging with configurable levels and file output
- **🧪 Robust Error Handling**: Graceful handling of corrupted files, unsupported formats, and edge cases

## 🚀 Quick Start

### Basic Installation

```bash
pip install -r requirements.txt
# macOS
brew install --cask libreoffice
# Ubuntu/Debian
sudo apt install libreoffice
```

### Basic Usage

```python
from documents_processor import Document

doc = Document("path/to/your/document.pdf")
doc.process()

print("Extracted text:", doc.text_content)
print("Found images:", doc.images)
print("Extracted tables:", doc.tables)
```

### Mass Processing for RAG Systems

```python
from documents_processor import batch_process_folder

results = batch_process_folder(
    input_folder="documents/",
    output_file="knowledge_base.md"
)
```

## 📋 Supported Formats

| Category | Formats | Capabilities | Requirements |
|----------|---------|-------------|--------------|
| **Documents** | PDF, DOCX, DOC, RTF, TXT, MD, ODT, EPUB | Text + embedded images + tables | Core installation |
| **Spreadsheets** | XLSX, XLS, CSV | Data extraction + table export | Core installation (optional `xlrd` for .xls) |
| **Presentations** | PPTX, PPT | Text + images + slide structure | LibreOffice |
| **Images** | JPG, PNG, HEIC, HEIF, GIF, TIFF, BMP | AI descriptions + EXIF metadata | Core installation |
| **Archives** | ZIP, RAR | Recursive processing + image extraction | Optional: rarfile + unrar |

## 🔧 Configuration

Create a `.env` file for advanced features:

```bash
# AI Image Descriptions (Optional)
OPENAI_API_KEY=your_api_key_here

# Processing Limits
MAX_DOCUMENT_PAGES=10
DISABLE_PAGE_LIMIT=false

# Optional: Direct Excel processing (default: off)
# If disabled, .xls/.xlsx are converted to PDF and processed as PDF
ENABLE_DIRECT_EXCEL=false

# Vision API Configuration
MAX_VISION_CALLS_PER_PAGE=50
```

### Notes
- When `ENABLE_DIRECT_EXCEL=true`, each sheet is exported to `tables/*.csv`, with previews added to the text output. Limits are controlled by `MAX_DOCUMENT_PAGES`/`DISABLE_PAGE_LIMIT`.
- PDF pages that are graphics or scans are saved at `dpi=200` for better detail.
- Images are saved with unique filenames across PDF, archive, and direct processing.
- Before AI description, image orientation is auto-detected and corrected in-memory.

## 🛠️ System Requirements
- Python 3.8+
- LibreOffice for Office→PDF conversion
- Optional: `rarfile` + `unrar`/`bsdtar` for RAR archives
- Optional: `xlrd` for legacy `.xls` files

## 📈 Performance & Scalability
- Configurable limits via env vars
- Unified image/table output folders for downstream processing

## 🤝 Contributing
PRs welcome.
