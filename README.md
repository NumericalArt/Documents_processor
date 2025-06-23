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

### 🛠️ Technical Excellence
- **🔒 Local Processing**: All document processing happens locally with optional AI features
- **📱 Cross-Platform Support**: Works on Windows, macOS, and Linux with platform-specific optimizations
- **⚡ Memory Efficient**: Process large documents without loading entire files into memory
- **📋 Comprehensive Logging**: Detailed logging with configurable levels and file output
- **🧪 Robust Error Handling**: Graceful handling of corrupted files, unsupported formats, and edge cases

## 🚀 Quick Start

### Basic Installation

```bash
# Install all dependencies (includes AI and development tools)
pip install -r requirements.txt

# Install system dependencies (macOS with Homebrew)
brew install --cask libreoffice

# Install system dependencies (Ubuntu/Debian)
sudo apt-get install libreoffice
```

### Basic Usage

```python
from documents_processor import Document

# Process a single document with AI image descriptions
doc = Document("path/to/your/document.pdf")
doc.process()

print("Extracted text:", doc.text_content)
print("Found images:", doc.images)  # Saved to images/ with unique names
print("Extracted tables:", doc.tables)  # Saved to tables/ as CSV files
```

### Mass Processing for RAG Systems

```python
from documents_processor import batch_process_folder

# Process entire document collection for RAG system
results = batch_process_folder(
    input_folder="documents/",
    output_file="knowledge_base.md"  # Structured for LLM processing
)
```

### Professional Cleanup Management

```bash
# Interactive cleanup with safety features
python cleanup_utility.py

# Preview what would be cleaned
python cleanup_utility.py --preview

# Automatic cleanup with backup
python cleanup_utility.py --all --backup
```

## 📋 Supported Formats

| Category | Formats | Capabilities | Requirements |
|----------|---------|-------------|--------------|
| **Documents** | PDF, DOCX, DOC, RTF, TXT, MD, ODT, EPUB, PY, JSON | Text + embedded images + tables | Core installation |
| **Spreadsheets** | XLSX, XLS, CSV | Data extraction + table export | Core installation |
| **Presentations** | PPTX, PPT | Text + images + slide structure | LibreOffice |
| **Images** | JPG, PNG, HEIC, HEIF, GIF, TIFF, BMP | OCR + AI descriptions + EXIF | Core installation |
| **Archives** | ZIP, RAR | Recursive processing + image extraction | Optional: rarfile + unrar |
| **Special** | Pages, Numbers | Native Apple format support | macOS only |

## 🔧 Configuration

Create a `.env` file for advanced features:

```bash
# AI Image Descriptions (Optional)
OPENAI_API_KEY=your_api_key_here

# Processing Limits
MAX_DOCUMENT_PAGES=10
DISABLE_PAGE_LIMIT=false

# Vision API Configuration  
MAX_VISION_CALLS_PER_PAGE=50
```

## 📚 Documentation

- **[Installation Guide](docs/INSTALLATION.md)** - Comprehensive setup for all platforms
- **[Cleanup Utility Guide](docs/CLEANUP_UTILITY_GUIDE.md)** - Professional file management
- **[API Documentation](docs/API.md)** - Complete API reference and examples
- **[Usage Examples](docs/EXAMPLES.md)** - Practical examples and tutorials

## 🛠️ System Requirements

- **Python**: 3.7 or higher
- **Optional**: LibreOffice (for advanced document conversion)
- **Optional**: OpenAI API key (for AI image descriptions)
- **Optional**: unrar or bsdtar (for RAR archive support)

## 📊 Output Structure

The processor creates organized output directories:

```
your_project/
├── processed_documents/    # Processing reports and logs
├── images/                # All images (unified storage with unique names)
├── tables/               # Exported tables (CSV format with references)
└── media_for_processing/ # Temporary processing files
```

## 🤖 AI-Powered Features

When configured with an OpenAI API key:

- **🔍 Intelligent Image Analysis**: Automatic recognition and description of embedded graphics
- **📊 Chart & Graph Analysis**: Analysis of charts, graphs, and diagrams with context
- **📋 Document Structure Recognition**: Understanding of document layout and content hierarchy
- **🎯 Context-Aware Descriptions**: Image summaries that understand document context
- **⚙️ Multiple Model Support**: Compatible with various OpenAI Vision models

## 🔒 Privacy & Security

- **🏠 Local-First Processing**: All document processing happens locally on your machine
- **🔐 Optional AI**: AI features require explicit API key configuration and are fully optional
- **📝 Data Control**: You maintain complete control over documents and processing results
- **🚫 No Data Retention**: Documents are not stored or transmitted unless you configure AI features
- **🛡️ Secure Configuration**: API keys stored in local .env files only

## 📈 Performance & Scalability

- **⚡ Memory Efficient**: Stream processing without loading entire files into memory
- **📊 Configurable Limits**: Fine-grained control over resource usage and processing scope
- **🔄 Batch Optimization**: Efficient processing of large document collections
- **📋 Progress Tracking**: Real-time monitoring of processing status for large batches
- **🎯 Selective Processing**: Process only specific file types or content areas as needed

## 🔮 Future Development

### 📧 Email Processing Support (Coming Soon)
- **EML Standard**: RFC 822/2822 email message format support
- **MSG Format**: Microsoft Outlook message files (.msg)
- **MBOX Format**: Unix mailbox format for bulk email processing
- **PST/OST**: Outlook data file processing with attachment extraction
- **Thunderbird Support**: Mozilla Thunderbird email format compatibility
- **Email Metadata**: Header analysis, sender/recipient extraction, date parsing
- **Attachment Processing**: Automatic extraction and processing of email attachments
- **Thread Analysis**: Email conversation threading and relationship mapping

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines and feel free to submit issues and pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Related Projects

- [PyMuPDF](https://pymupdf.readthedocs.io/) - PDF processing
- [Tesseract](https://github.com/tesseract-ocr/tesseract) - OCR engine
- [OpenAI](https://openai.com/) - AI image analysis

---

**Made with ❤️ for professional document processing and RAG system development**
