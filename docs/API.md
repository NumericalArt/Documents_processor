# API Documentation

## Document Class

The `Document` class is the core component of the Documents Processor, providing a unified interface for processing any supported file format.

### Basic Usage

```python
from documents_processor import Document

# Create and process a document
doc = Document(\"path/to/document.pdf\")
doc.process()

# Access extracted content
print(doc.text_content)    # Full text content
print(doc.images)          # List of extracted images
print(doc.tables)          # List of extracted tables
print(doc.metadata)        # Document metadata
```

### Constructor Parameters

```python
doc = Document(
    file_path=\"document.pdf\",        # Path to the document
    media_dir=\"media_for_processing\" # Directory for temporary files
)
```

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `text_content` | str | Extracted text content |
| `images` | List[str] | Paths to extracted images |
| `tables` | List[str] | Paths to extracted CSV tables |
| `metadata` | dict | Document metadata (title, author, dates, etc.) |
| `file_size` | int | Original file size in bytes |
| `file_ext` | str | File extension |
| `file_name` | str | Original filename |

## Batch Processing

### Process Entire Folders

```python
from documents_processor import batch_process_folder

# Process all documents in a folder
docs = batch_process_folder(
    input_folder=\"documents/\",
    output_file=\"combined_content.md\",
    preview_chars=None,
    return_docs=False
)
```

### Return Structured Data

```python
# Get structured data instead of text report
docs = batch_process_folder(
    input_folder=\"documents/\",
    return_docs=True
)

for doc in docs:
    print(f\"File: {doc['rel_path']}\")
    print(f\"Type: {doc['file_ext']}\")
    print(f\"Size: {doc['file_size']} bytes\")
    print(f\"Content length: {len(doc['text_content'])} characters\")
    print(f\"Tables: {len(doc['tables'])} CSV files\")
```

## File Format Support

### Supported Formats

| Category | Extensions | Features |
|----------|------------|----------|
| **PDF** | .pdf | Text extraction, embedded images, metadata |
| **Microsoft Office** | .docx, .doc, .pptx, .ppt | Converted via LibreOffice |
| **Spreadsheets** | .xlsx, .xls, .csv | Table extraction, multi-sheet support |
| **Text Formats** | .txt, .md, .rtf | Direct text extraction |
| **Images** | .jpg, .png, .heic, .gif, .bmp, .tiff | AI descriptions, EXIF data |
| **Archives** | .zip, .rar | Recursive extraction and processing |
| **Other** | .odt, .epub, .json, .html | Format-specific processing |

### Image Processing

All images are saved to the unified `images/` directory with unique naming:

```
images/
├── pdf_20241230_123456_001_document_img1.png     # From PDF
├── direct_20241230_123457_002_photo.jpg          # Direct image
└── archive_20241230_123458_003_scan.png          # From archive
```

## AI-Powered Features

### Setup OpenAI Integration

```python
import os

# Set API key
os.environ['OPENAI_API_KEY'] = 'your-api-key'
# or
os.environ['API_KEY'] = 'your-api-key'
```

### AI Image Descriptions

The system automatically generates AI descriptions for images when an API key is configured:

```python
doc = Document(\"document_with_images.pdf\")
doc.process()

# Images now include AI descriptions in the text output
print(doc.text_content)
# Output includes: \"[Image 1: AI-generated description] (Image saved to: images/pdf_...png)\"
```

### Configuration Options

You can configure AI processing through environment variables:

```bash
export MAX_VISION_CALLS_PER_PAGE=50      # Limit AI calls per page
export MAX_DOCUMENT_PAGES=10             # Limit pages processed
export DISABLE_PAGE_LIMIT=true           # Remove page limits
```

## Archive Processing

### ZIP Archives

```python
doc = Document(\"archive.zip\")
doc.process()

# Processes all supported files within the archive
print(doc.text_content)  # Combined content from all files
```

### RAR Archives

```python
# Requires rarfile package and unrar system tool
doc = Document(\"archive.rar\")
doc.process()
```

### Archive Limits

- Maximum archive size: 100 MB
- Maximum files per archive: 50
- Configurable via constants in the code

## Error Handling

### Graceful Error Recovery

```python
from documents_processor import Document

try:
    doc = Document(\"potentially_corrupted.pdf\")
    doc.process()
except Exception as e:
    print(f\"Processing failed: {e}\")
    # Error is logged to processed_documents/processing.log
```

### Batch Processing Errors

```python
# Batch processing continues even if individual files fail
docs = batch_process_folder(
    \"mixed_documents/\",
    return_docs=True
)

# Errors are included in the results
for doc in docs:
    if 'error' in doc:
        print(f\"Failed: {doc['rel_path']} - {doc['error']}\")
```

## Performance Configuration

### Page Limits

Control processing scope for large documents:

```bash
# Environment variables
export MAX_DOCUMENT_PAGES=50             # Process first 50 pages
export DISABLE_PAGE_LIMIT=true           # Process all pages
```

### Memory Management

The system includes several built-in limits:

- Image size limit: 10 MB per image
- Image dimension limit: 3000x3000 pixels
- Minimum image size: 200x200 pixels for AI processing

## Logging

### Built-in Logging

All processing activities are logged to:
- File: `processed_documents/processing.log`
- Console: INFO level messages

### Log Contents

- Processing start/completion times
- File sizes and page counts
- AI API call limits and usage
- Error messages and stack traces
- Performance metrics

## Output Organization

### Directory Structure

```
project_root/
├── images/                    # All extracted images (unified)
├── tables/                    # CSV exports from spreadsheets
├── media_for_processing/      # Temporary files
└── processed_documents/       # Text outputs and logs
    └── processing.log
```

### File Naming Conventions

**Images**: `{source_type}_{timestamp}_{counter}_{original_name}.{extension}`
- `source_type`: pdf, direct, archive
- `timestamp`: YYYYMMDD_HHMMSS
- `counter`: 001, 002, 003...
- `original_name`: cleaned filename

**Tables**: `{workbook_name}_{sheet_name}.csv`

## Utility Functions

### Cleanup Management

```python
# Use the cleanup utility for file management
import subprocess

# Preview cleanup
subprocess.run([\"python\", \"cleanup_utility.py\", \"--preview\"])

# Clean with backup
subprocess.run([\"python\", \"cleanup_utility.py\", \"--all\", \"--backup\"])
```

### Batch Markdown Generation

```python
# Create comprehensive reports
from process_all_to_markdown import create_markdown_report

report_path = create_markdown_report()
print(f\"Report generated: {report_path}\")
```

## Best Practices

### 1. Resource Management

```python
# Process files in batches for large collections
import os

files = [f for f in os.listdir(\"large_folder\") if f.endswith(\".pdf\")]
batch_size = 10

for i in range(0, len(files), batch_size):
    batch = files[i:i + batch_size]
    for file in batch:
        doc = Document(file)
        doc.process()
        # Process and clean up before next batch
```

### 2. Error Recovery

```python
# Implement retry logic for network-dependent features
def process_with_retry(file_path, max_retries=3):
    for attempt in range(max_retries):
        try:
            doc = Document(file_path)
            doc.process()
            return doc
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            print(f\"Attempt {attempt + 1} failed, retrying...\")
            time.sleep(2 ** attempt)  # Exponential backoff
```

### 3. Memory Optimization

```python
# Process large files efficiently
def process_large_files(file_paths):
    for file_path in file_paths:
        # Process one at a time
        doc = Document(file_path)
        doc.process()
        
        # Extract essential data
        summary = {
            'file': file_path,
            'words': len(doc.text_content.split()),
            'images': len(doc.images),
            'tables': len(doc.tables)
        }
        
        # Release memory
        del doc
        yield summary
```

This API documentation provides comprehensive coverage of the Documents Processor's capabilities for building RAG systems, processing document collections, and handling various file formats with AI-powered features.