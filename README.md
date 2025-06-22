# Documents Processor 📄🔍

A comprehensive Python utility for processing and extracting content from various document formats with AI-powered image analysis capabilities.

## ✨ Features

- **📄 Multi-format Support**: Process PDF, Word, Excel, PowerPoint, text files, images, and archives
- **🤖 AI Integration**: Generate intelligent descriptions of images using OpenAI's API
- **📁 Batch Processing**: Process entire folders recursively with progress tracking
- **🔍 OCR Capabilities**: Extract text from images and scanned documents using Tesseract
- **📊 Structured Output**: Organized extraction of text, images, tables, and metadata
- **⚙️ Configurable Limits**: Control processing limits for pages, file sizes, and archive contents
- **📝 Comprehensive Logging**: Detailed logging with configurable levels and file output

## 🚀 Quick Start

### Basic Installation

```bash
# Install core dependencies
pip install -r requirements.txt

# Install system dependencies (macOS with Homebrew)
brew install tesseract
brew install --cask libreoffice

# Install system dependencies (Ubuntu/Debian)
sudo apt-get install tesseract-ocr libreoffice
```

### Basic Usage

```python
from documents_processor import Document

# Process a single document
doc = Document("path/to/your/document.pdf")
doc.process()

print("Extracted text:", doc.text_content)
print("Found images:", doc.images)
print("Extracted tables:", doc.tables)
```

### Batch Processing

```python
from documents_processor import batch_process_folder

# Process all documents in a folder
results = batch_process_folder(
    input_folder="documents/",
    output_file="processing_report.txt"
)
```

## 📋 Supported Formats

| Category | Formats | Requirements |
|----------|---------|--------------|
| **Documents** | PDF, DOCX, DOC, RTF, TXT, MD, ODT, EPUB | Core installation |
| **Spreadsheets** | XLSX, XLS, CSV | Core installation |
| **Presentations** | PPTX, PPT | LibreOffice |
| **Images** | JPG, PNG, HEIC, HEIF, GIF, TIFF, BMP | Core installation |
| **Archives** | ZIP, RAR | Optional: rarfile + unrar |
| **Special** | Pages, Numbers | macOS only |

## 💾 Installation Options

### Option 1: Core Features Only
```bash
pip install -r requirements.txt
```

### Option 2: With AI Image Descriptions
```bash
pip install -r requirements.txt
pip install -r requirements-optional.txt
```

### Option 3: Full Development Setup
```bash
pip install -r requirements.txt
pip install -r requirements-optional.txt
pip install -r requirements-dev.txt
```

## 🔧 Configuration

Create a `.env` file in your project directory:

```bash
# Copy the template
cp .env.example .env

# Edit with your settings
# Key configurations:
OPENAI_API_KEY=your_api_key_here
MAX_DOCUMENT_PAGES=10
```

## 📚 Documentation

- **[Installation Guide](docs/INSTALLATION.md)** - Detailed setup instructions for all platforms
- **[API Documentation](docs/API.md)** - Complete API reference and examples
- **[Usage Examples](docs/EXAMPLES.md)** - Practical examples and tutorials
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions

## 🛠️ System Requirements

- **Python**: 3.7 or higher
- **Required**: Tesseract OCR
- **Optional**: LibreOffice (for advanced document conversion)
- **Optional**: unrar or bsdtar (for RAR archive support)

## 📊 Output Structure

The processor creates organized output directories:

```
your_project/
├── processed_documents/    # Processing reports and logs
├── images/                # Extracted images
├── tables/               # Exported tables (CSV format)
├── extracted_images/     # Images from archives
└── media_for_processing/ # Temporary processing files
```

## 🤖 AI Features

When configured with an OpenAI API key, the processor can:

- Generate intelligent descriptions of images within documents
- Analyze charts, graphs, and diagrams
- Provide context-aware image summaries
- Support multiple OpenAI models

## 🔒 Privacy & Security

- **Local Processing**: All document processing happens locally on your machine
- **Optional AI**: AI features are opt-in and require explicit API key configuration
- **Data Control**: You maintain full control over your documents and processing results
- **No Data Retention**: Documents are not stored or transmitted unless you configure AI features

## 📈 Performance

- **Memory Efficient**: Processes documents without loading entire files into memory
- **Configurable Limits**: Control resource usage with built-in limits
- **Batch Optimization**: Efficient processing of multiple documents
- **Progress Tracking**: Monitor processing status for large batches

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines and feel free to submit issues and pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Related Projects

- [PyMuPDF](https://pymupdf.readthedocs.io/) - PDF processing
- [Tesseract](https://github.com/tesseract-ocr/tesseract) - OCR engine
- [OpenAI](https://openai.com/) - AI image analysis

---

**Made with ❤️ for document processing automation**