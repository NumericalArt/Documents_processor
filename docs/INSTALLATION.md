# Installation Guide

This guide provides detailed installation instructions for the Documents Processor on different platforms.

## System Requirements

- **Python**: 3.7 or higher
- **Operating System**: Windows, macOS, or Linux
- **RAM**: Minimum 2GB (4GB+ recommended for large documents)
- **Storage**: At least 100MB for dependencies, plus space for processed documents

## Quick Installation

```bash
# 1. Clone or download the project
git clone https://github.com/yourusername/documents-processor.git
cd documents-processor

# 2. Install all dependencies (core, AI features, and development tools)
pip install -r requirements.txt

# 3. Install system dependencies (see platform-specific sections below)
```

## Platform-Specific Installation

### macOS

#### Using Homebrew (Recommended)

```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install required system dependencies
brew install tesseract

# Install optional dependencies
brew install --cask libreoffice  # For advanced document conversion
brew install unrar              # For RAR archive support
```

#### Using MacPorts

```bash
# Install required dependencies
sudo port install tesseract

# Install optional dependencies
sudo port install libreoffice
sudo port install unrar
```

#### Manual Installation

1. **Tesseract OCR**:
   - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   - Install the .pkg file
   - Verify installation: `tesseract --version`

2. **LibreOffice** (Optional):
   - Download from: https://www.libreoffice.org/download/download/
   - Install the .dmg file

### Windows

#### Using Chocolatey (Recommended)

```powershell
# Install Chocolatey if not already installed
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install required dependencies
choco install tesseract

# Install optional dependencies
choco install libreoffice
choco install unrar
```

#### Manual Installation

1. **Tesseract OCR**:
   - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   - Install the .exe file
   - Add to PATH: `C:\Program Files\Tesseract-OCR`
   - Verify: `tesseract --version`

2. **LibreOffice** (Optional):
   - Download from: https://www.libreoffice.org/download/download/
   - Install the .msi file

3. **UnRAR** (Optional):
   - Download from: https://www.win-rar.com/download.html
   - Install WinRAR or just the UnRAR command-line tool

#### Environment Variables (Windows)

Add these to your system PATH:
- `C:\Program Files\Tesseract-OCR`
- `C:\Program Files\LibreOffice\program` (if installed)

### Linux (Ubuntu/Debian)

```bash
# Update package list
sudo apt update

# Install required dependencies
sudo apt install tesseract-ocr tesseract-ocr-eng

# Install optional dependencies
sudo apt install libreoffice  # For document conversion
sudo apt install unrar        # For RAR archive support

# Install additional language packs for Tesseract (optional)
sudo apt install tesseract-ocr-fra tesseract-ocr-deu  # French, German examples
```

### Linux (CentOS/RHEL/Fedora)

```bash
# For CentOS/RHEL (with EPEL repository)
sudo yum install epel-release
sudo yum install tesseract tesseract-langpack-eng

# For Fedora
sudo dnf install tesseract tesseract-langpack-eng

# Optional dependencies
sudo yum install libreoffice unrar  # CentOS/RHEL
sudo dnf install libreoffice unrar  # Fedora
```

### Linux (Arch Linux)

```bash
# Install required dependencies
sudo pacman -S tesseract tesseract-data-eng

# Install optional dependencies
sudo pacman -S libreoffice-fresh unrar
```

## Python Dependencies

### Comprehensive Installation (Recommended)

```bash
pip install -r requirements.txt
```

This single command installs all dependencies including:

**Core Document Processing:**
- PyMuPDF (PDF processing)
- pandas (data manipulation) 
- Pillow (image processing)
- striprtf (RTF processing)
- strip-markdown (Markdown processing)
- openpyxl (Excel processing)
- pytesseract (OCR interface)
- python-dotenv (environment variables)

**AI-Powered Features:**
- openai (AI image descriptions)

**Archive Processing:**
- rarfile (RAR archive support)

**Development & Testing Tools:**
- pytest, black, flake8, mypy, sphinx, pre-commit

### Minimal Installation (Core Only)

If you prefer to install only core dependencies and add features as needed:

```bash
# Install only core processing dependencies
pip install PyMuPDF>=1.23.0 pandas>=1.5.0 Pillow>=9.0.0 striprtf>=0.0.26 strip-markdown>=0.1.1 openpyxl>=3.1.0 xlrd>=2.0.0 bottleneck>=1.3.6 tabulate>=0.9.0 pytesseract>=0.3.10 python-dotenv>=1.0.0
```

## Installation Verification

### Verify Python Dependencies

```python
# Run this Python script to verify core dependencies
import sys

required_modules = [
    'fitz',           # PyMuPDF
    'pandas',         # pandas
    'PIL',            # Pillow
    'striprtf',       # striprtf
    'openpyxl',       # openpyxl
    'pytesseract',    # pytesseract
    'dotenv',         # python-dotenv
]

print("Checking Python dependencies...")
for module in required_modules:
    try:
        __import__(module)
        print(f"✅ {module}")
    except ImportError:
        print(f"❌ {module} - Not installed")

print("\nChecking optional dependencies...")
optional_modules = ['openai', 'rarfile']
for module in optional_modules:
    try:
        __import__(module)
        print(f"✅ {module}")
    except ImportError:
        print(f"⚠️  {module} - Optional, not installed")
```

### Verify System Dependencies

```bash
# Test Tesseract
tesseract --version

# Test LibreOffice (if installed)
soffice --version

# Test unrar (if installed)
unrar
```

### Test the Documents Processor

```python
from documents_processor import Document

# Create a simple test
import tempfile
import os

# Create a test text file
with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
    f.write("This is a test document for verification.")
    test_file = f.name

try:
    # Test basic functionality
    doc = Document(test_file)
    doc.process()
    
    if doc.text_content.strip():
        print("✅ Documents Processor is working correctly!")
        print(f"Extracted: {doc.text_content[:50]}...")
    else:
        print("❌ Documents Processor test failed")
        
finally:
    # Clean up
    os.unlink(test_file)
```

## Troubleshooting Installation Issues

### Common Issues

1. **"tesseract: command not found"**
   - Tesseract is not installed or not in PATH
   - Follow platform-specific installation steps above
   - Verify PATH configuration

2. **"LibreOffice soffice not found"**
   - LibreOffice is not installed (optional for basic functionality)
   - Install LibreOffice or set `SOFFICE_PATH` environment variable

3. **Import errors for Python packages**
   - Virtual environment issues
   - Try: `pip install --upgrade pip` then reinstall requirements

4. **Permission errors**
   - Use virtual environment: `python -m venv venv && source venv/bin/activate`
   - Or use `pip install --user`

### Getting Help

If you encounter issues not covered here:

1. Check the [Troubleshooting Guide](TROUBLESHOOTING.md)
2. Verify system requirements are met
3. Check GitHub issues for similar problems
4. Create a new issue with your system information and error message

## Next Steps

After successful installation:

1. Read the [Usage Examples](EXAMPLES.md)
2. Check the [API Documentation](API.md)
3. Configure your `.env` file if needed
4. Try processing your first document!