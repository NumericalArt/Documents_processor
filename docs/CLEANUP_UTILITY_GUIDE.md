# Cleanup Utility Guide

A comprehensive guide for using the Documents Processor Cleanup Utility to manage temporary files efficiently and safely.

## 📋 Overview

The Cleanup Utility is designed to help you manage temporary files created during document processing. It provides safe, selective cleaning of processing directories with backup options and preview capabilities.

### Target Directories

The utility manages these temporary file directories:

| Directory | Purpose | Typical Contents |
|-----------|---------|------------------|
| `images/` | All processed and extracted images (unified storage) | PNG, JPG files from PDF, direct, and archive processing |
| `media_for_processing/` | Temporary media files | Intermediate processing files |
| `tables/` | Extracted CSV tables | CSV files extracted from Excel/spreadsheets |

## 🚀 Quick Start

### Basic Usage

```bash
# Interactive mode (default) - select which directories to clean
python cleanup_utility.py

# Clean all directories automatically
python cleanup_utility.py --all

# Preview what would be deleted without deleting
python cleanup_utility.py --preview

# Clean with backup
python cleanup_utility.py --all --backup
```

### Interactive Mode Example

```
🧹 Documents Processor Cleanup Utility
============================================================
🔍 Scanning directories...
============================================================
📁 images                   |  47 files |  139.8 MB
   └─ All processed and extracted images (unified storage)
❌ media_for_processing     |   0 files |     0 B
📁 tables                   |   5 files | 156.2 KB
   └─ Extracted CSV tables from spreadsheets
============================================================
📊 TOTAL: 52 files, 140.0 MB
```

## 🎛️ Command Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `--all` | Clean all directories automatically | `python cleanup_utility.py --all` |
| `--preview` | Show what would be deleted without deleting | `python cleanup_utility.py --preview` |
| `--backup` | Create backup before deleting files | `python cleanup_utility.py --backup` |
| `--interactive` | Interactive mode (default behavior) | `python cleanup_utility.py --interactive` |
| `--help` | Show help message and exit | `python cleanup_utility.py --help` |

## 🔍 Features

### Interactive Directory Selection
- **Visual Interface**: Clear display of directory contents and sizes
- **Selective Cleaning**: Choose which directories to clean individually
- **Real-time Updates**: See selection changes immediately
- **Smart Defaults**: Only directories with files are selected by default

### Safety Features
- **Preview Mode**: See exactly what will be deleted before deletion
- **Confirmation Prompts**: Must type "DELETE" to confirm dangerous operations
- **Backup Creation**: Optional backup of all files before deletion
- **Error Handling**: Graceful handling of permission errors and missing files

### Progress Indicators
For large operations, progress is shown:
```
🧹 Cleaning images/ (247 files)...
   ⏳ Deleted 50 files...
   ⏳ Deleted 100 files...
   ⏳ Deleted 150 files...
   ⏳ Deleted 200 files...
✅ Cleanup complete! Deleted 247 files (45.2 MB)
```

## 💾 Backup System

### Automatic Backup Creation
When using the `--backup` option, the utility:
1. Creates a timestamped backup directory
2. Preserves the original directory structure
3. Copies all files before deletion
4. Reports backup location

### Backup Directory Structure
```
cleanup_backup_20240123_143022/
├── images/
│   ├── pdf_20241230_123456_001_document_img1.png
│   ├── direct_20241230_123457_002_photo.jpg
│   └── archive_20241230_123458_003_scan.png
└── tables/
    ├── data1.csv
    └── data2.csv
```

## 👁️ Preview Mode

Preview mode shows exactly what would be deleted without performing deletion:

```bash
python cleanup_utility.py --preview
```

### Preview Output Example
```
👁️  PREVIEW MODE - Files that would be deleted:
============================================================
📁 images/
   🗑️  pdf_20241230_123456_001_document_img1.png (245.6 KB)
   🗑️  direct_20241230_123457_002_photo.jpg (1.2 MB)
   🗑️  archive_20241230_123458_003_scan.png (678.3 KB)
   ... and 44 more files

📁 tables/
   🗑️  spreadsheet1_Sheet1.csv (12.4 KB)
   🗑️  payroll_data.csv (143.8 KB)
============================================================
📊 TOTAL TO DELETE: 47 files, 139.8 MB
```

## ⚠️ Safety and Error Handling

### Confirmation System
Before deletion, you must confirm by typing "DELETE":
```
⚠️  DELETION CONFIRMATION
============================================================
🗑️  images: 47 files (139.8 MB)
🗑️  tables: 5 files (156.2 KB)
============================================================
📊 TOTAL TO DELETE: 52 files (140.0 MB)

❓ Proceed with deletion? (type 'DELETE' to confirm): DELETE
```

### Error Handling
The utility handles various error conditions gracefully:
- **Permission Errors**: Skips files that can't be accessed
- **Missing Files**: Handles files deleted by other processes
- **Directory Access**: Skips directories with permission issues
- **Backup Failures**: Offers option to continue without backup

## 🧪 Usage Examples

### Example 1: Daily Cleanup Routine
```bash
# Check what files are present
python cleanup_utility.py --preview

# Clean with backup for safety
python cleanup_utility.py --all --backup
```

### Example 2: Selective Cleaning
```bash
# Interactive mode to choose specific directories
python cleanup_utility.py

# Select only images and tables directories
# Skip media_for_processing if needed for review
```

### Example 3: Large Processing Cleanup
```bash
# Preview first to see scope
python cleanup_utility.py --all --preview

# If comfortable with preview, clean with backup
python cleanup_utility.py --all --backup
```

## 🎯 Best Practices

### Regular Cleanup Schedule
1. **Daily**: Quick preview to monitor file accumulation
2. **Weekly**: Full cleanup with backup
3. **Monthly**: Review backup directory and archive/delete old backups

### Safety Guidelines
1. **Always Preview**: Use `--preview` before large cleanups
2. **Use Backups**: Use `--backup` for important cleanup operations
3. **Check Contents**: Review files before deletion in interactive mode
4. **Monitor Space**: Keep eye on disk space when creating backups

### Integration with Documents Processor
The cleanup utility integrates seamlessly with the Documents Processor workflow:
1. **Process Documents**: Run document processing as usual
2. **Check Output**: Review processed results
3. **Clean Temporaries**: Use cleanup utility to remove temporary files
4. **Maintain Backups**: Keep backups of important processing sessions

This ensures efficient disk space management while maintaining data safety.