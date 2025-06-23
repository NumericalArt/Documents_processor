# Usage Examples

This document provides practical examples demonstrating how to use the Documents Processor for various real-world scenarios.

## Basic Document Processing

### Single Document Processing

```python
from documents_processor import Document

# Process a PDF with default settings
doc = Document(\"financial_report.pdf\")
doc.process()

print(f\"Extracted {len(doc.text_content.split())} words\")
print(f\"Found {len(doc.images)} images\")
print(f\"Found {len(doc.tables)} tables\")

# Save results
with open(\"financial_report.txt\", \"w\") as f:
    f.write(doc.text_content)
```

### Processing with AI Image Descriptions

```python
import os
from documents_processor import Document

# Set up OpenAI API key
os.environ['OPENAI_API_KEY'] = 'your-api-key-here'

# Process document with AI-powered image analysis
doc = Document(\"product_catalog.pdf\")
doc.process()

# AI descriptions are automatically included in text_content
print(\"Full content with AI descriptions:\")
print(doc.text_content)
```

## Building a Knowledge Base

### Processing Document Collections for RAG Systems

```python
import os
from documents_processor import batch_process_folder

# Process entire document collection
docs = batch_process_folder(
    input_folder=\"company_documents/\",
    return_docs=True
)

print(f\"Knowledge base created from {len(docs)} documents\")

# Create embeddings for RAG system (example with sentence-transformers)
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

# Split content into chunks for better retrieval
def split_text(text, chunk_size=500):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = ' '.join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

# Process knowledge base for embeddings
all_chunks = []
for doc in docs:
    chunks = split_text(doc['text_content'])
    all_chunks.extend(chunks)

embeddings = model.encode(all_chunks)
print(f\"Created {len(embeddings)} embedding vectors for RAG system\")
```

### Selective Content Extraction

```python
from documents_processor import Document
import os

# Process only tables from financial documents
def extract_financial_tables(folder_path):
    tables_data = []
    
    for filename in os.listdir(folder_path):
        if filename.endswith('.pdf'):
            doc = Document(os.path.join(folder_path, filename))
            doc.process()
            
            for table_path in doc.tables:
                tables_data.append({
                    'source_file': filename,
                    'table_path': table_path
                })
    
    return tables_data

# Extract all tables
financial_tables = extract_financial_tables(\"quarterly_reports/\")
print(f\"Extracted {len(financial_tables)} tables from financial reports\")
```

## Handling Different Document Types

### Excel Spreadsheet Processing

```python
from documents_processor import Document
import pandas as pd

# Process Excel file with multiple sheets
doc = Document(\"sales_data.xlsx\")
doc.process()

# Access sheet data
for table_path in doc.tables:
    print(f\"Table: {table_path}\")
    
    # Load full data
    df = pd.read_csv(table_path)
    print(f\"Shape: {df.shape}\")
    print(f\"Columns: {list(df.columns)}\")
    print()
```

### Archive Processing

```python
from documents_processor import Document

# Process ZIP archive containing mixed documents
doc = Document(\"project_files.zip\")
doc.process()

# Review combined content from all files
print(f\"Total content length: {len(doc.text_content)} characters\")
print(f\"Images extracted: {len(doc.images)}\")
print(f\"Tables extracted: {len(doc.tables)}\")
```

## Advanced Processing Scenarios

### Large Document Collection Processing

```python
from documents_processor import batch_process_folder
import logging

# Setup detailed logging for large batch
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_large_collection(folder_path):
    \"\"\"Process large document collection efficiently\"\"\"
    
    docs = batch_process_folder(
        input_folder=folder_path,
        return_docs=True
    )
    
    # Process results
    successful = [doc for doc in docs if 'text_content' in doc]
    failed = [doc for doc in docs if 'text_content' not in doc]
    
    print(f\"Successfully processed: {len(successful)} files\")
    print(f\"Failed: {len(failed)} files\")
    
    return successful, failed

# Execute large batch processing
successful, failed = process_large_collection(\"legal_documents/\")
```

### Custom Content Analysis

```python
from documents_processor import Document
import re
import os

def analyze_contract_documents(folder_path):
    \"\"\"Extract key information from legal contracts\"\"\"
    
    contract_data = []
    
    for filename in os.listdir(folder_path):
        if filename.endswith(('.pdf', '.docx')):
            doc = Document(os.path.join(folder_path, filename))
            doc.process()
            
            # Extract key contract information
            content = doc.text_content
            
            # Find dates (simple regex example)
            dates = re.findall(r'\\b\\d{1,2}/\\d{1,2}/\\d{4}\\b', content)
            
            # Find monetary amounts
            amounts = re.findall(r'\\$[\\d,]+(?:\\.\\d{2})?', content)
            
            # Find parties (simplified)
            parties = re.findall(r'Party [A-Z]', content)
            
            contract_data.append({
                'filename': filename,
                'dates': dates,
                'amounts': amounts,
                'parties': list(set(parties)),
                'word_count': len(content.split()),
                'images': len(doc.images),
                'tables': len(doc.tables)
            })
    
    return contract_data

# Analyze contracts
contract_analysis = analyze_contract_documents(\"contracts/\")
for contract in contract_analysis:
    print(f\"Contract: {contract['filename']}\")
    print(f\"  Dates found: {contract['dates']}\")
    print(f\"  Amounts: {contract['amounts']}\")
    print(f\"  Word count: {contract['word_count']}\")
    print()
```

### Multi-Language Document Processing

```python
from documents_processor import Document
from langdetect import detect
import os

def process_multilingual_documents(folder_path):
    \"\"\"Process documents in multiple languages\"\"\"
    
    language_stats = {}
    
    for filename in os.listdir(folder_path):
        if filename.endswith(('.pdf', '.docx', '.txt')):
            doc = Document(os.path.join(folder_path, filename))
            doc.process()
            
            # Detect language
            try:
                language = detect(doc.text_content[:1000])  # Use first 1000 chars
            except:
                language = 'unknown'
            
            if language not in language_stats:
                language_stats[language] = {
                    'count': 0,
                    'files': [],
                    'total_words': 0
                }
            
            language_stats[language]['count'] += 1
            language_stats[language]['files'].append(filename)
            language_stats[language]['total_words'] += len(doc.text_content.split())
    
    return language_stats

# Process multilingual collection
lang_stats = process_multilingual_documents(\"international_docs/\")
for lang, stats in lang_stats.items():
    print(f\"Language: {lang}\")
    print(f\"  Documents: {stats['count']}\")
    print(f\"  Total words: {stats['total_words']}\")
    print()
```

## Error Handling and Recovery

### Robust Batch Processing

```python
from documents_processor import batch_process_folder
import logging

def robust_document_processing(input_folder, output_file):
    \"\"\"Process documents with comprehensive error handling\"\"\"
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('processing.log'),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    
    try:
        # Process with error recovery
        docs = batch_process_folder(
            input_folder=input_folder,
            output_file=output_file,
            return_docs=True
        )
        
        successful = [doc for doc in docs if 'text_content' in doc]
        failed = [doc for doc in docs if 'text_content' not in doc]
        
        logger.info(f\"Processing complete: {len(successful)} files processed\")
        
        if failed:
            logger.warning(f\"{len(failed)} files failed processing\")
            for doc in failed:
                logger.error(f\"Failed: {doc.get('rel_path', 'unknown')}\")
        
        return successful, failed
        
    except Exception as e:
        logger.error(f\"Batch processing failed: {e}\")
        return None, None

# Execute robust processing
successful, failed = robust_document_processing(\"sensitive_documents/\", \"processed_output.md\")
```

## Performance Optimization

### Memory-Efficient Processing

```python
from documents_processor import Document
import psutil
import gc
import os

def memory_efficient_processing(file_paths):
    \"\"\"Process large files while monitoring memory usage\"\"\"
    
    results = []
    
    for file_path in file_paths:
        # Check memory before processing
        memory_before = psutil.virtual_memory().percent
        
        try:
            doc = Document(file_path)
            doc.process()
            
            # Extract key information only
            result = {
                'file_path': file_path,
                'word_count': len(doc.text_content.split()),
                'image_count': len(doc.images),
                'table_count': len(doc.tables),
                'success': True
            }
            
            results.append(result)
            
        except Exception as e:
            results.append({
                'file_path': file_path,
                'error': str(e),
                'success': False
            })
        
        # Cleanup and monitor memory
        if 'doc' in locals():
            del doc
        gc.collect()
        
        memory_after = psutil.virtual_memory().percent
        print(f\"Processed {os.path.basename(file_path)}: Memory {memory_before}% -> {memory_after}%\")
    
    return results

# Process large files efficiently
large_files = [\"large_doc1.pdf\", \"large_doc2.pdf\", \"large_doc3.pdf\"]
results = memory_efficient_processing(large_files)
```

## Integration Examples

### Flask Web Application

```python
from flask import Flask, request, jsonify, send_file
from documents_processor import Document
import os
import tempfile

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process_document():
    \"\"\"API endpoint for document processing\"\"\"
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        file.save(tmp_file.name)
        
        try:
            # Process document
            doc = Document(tmp_file.name)
            doc.process()
            
            # Return results
            result = {
                'text_content': doc.text_content,
                'word_count': len(doc.text_content.split()),
                'image_count': len(doc.images),
                'table_count': len(doc.tables),
                'metadata': doc.metadata
            }
            
            return jsonify(result)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        
        finally:
            # Cleanup
            os.unlink(tmp_file.name)

if __name__ == '__main__':
    app.run(debug=True)
```

### Streamlit Dashboard

```python
import streamlit as st
from documents_processor import Document
import pandas as pd

def main():
    st.title(\"Document Processing Dashboard\")
    
    # File upload
    uploaded_file = st.file_uploader(\"Choose a document\", type=['pdf', 'docx', 'txt'])
    
    if uploaded_file is not None:
        # Save uploaded file
        with open(uploaded_file.name, \"wb\") as f:
            f.write(uploaded_file.getbuffer())
        
        # Process document
        with st.spinner('Processing document...'):
            doc = Document(uploaded_file.name)
            doc.process()
        
        # Display results
        st.success(\"Processing complete!\")
        
        # Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric(\"Word Count\", len(doc.text_content.split()))
        col2.metric(\"Images\", len(doc.images))
        col3.metric(\"Tables\", len(doc.tables))
        
        # Text content
        st.subheader(\"Extracted Text\")
        st.text_area(\"Content\", doc.text_content, height=300)
        
        # Images
        if doc.images:
            st.subheader(\"Extracted Images\")
            for i, image_path in enumerate(doc.images):
                st.image(image_path, caption=f\"Image {i+1}\")
        
        # Tables
        if doc.tables:
            st.subheader(\"Extracted Tables\")
            for i, table_path in enumerate(doc.tables):
                st.write(f\"Table {i+1}\")
                df = pd.read_csv(table_path)
                st.dataframe(df)

if __name__ == \"__main__\":
    main()
```

## File Management Examples

### Using the Cleanup Utility

```python
import subprocess

def cleanup_processing_files():
    \"\"\"Clean temporary files using the cleanup utility\"\"\"
    
    # Preview what would be cleaned
    subprocess.run([\"python\", \"cleanup_utility.py\", \"--preview\"])
    
    # Ask user for confirmation
    confirm = input(\"Proceed with cleanup? (y/N): \")
    
    if confirm.lower() == 'y':
        # Clean with backup
        subprocess.run([\"python\", \"cleanup_utility.py\", \"--all\", \"--backup\"])
        print(\"Cleanup completed successfully\")
    else:
        print(\"Cleanup cancelled\")

# Execute cleanup
cleanup_processing_files()
```

### Creating Comprehensive Reports

```python
from process_all_to_markdown import create_markdown_report

def generate_processing_report():
    \"\"\"Generate a comprehensive markdown report\"\"\"
    
    # Process all files and create report
    report_path = create_markdown_report()
    
    print(f\"Comprehensive report generated: {report_path}\")
    
    # Read and display summary
    with open(report_path, 'r') as f:
        content = f.read()
        
    # Extract summary statistics
    lines = content.split('\\n')
    for line in lines:
        if \"Total Files Processed:\" in line:
            print(line)
        elif \"Total Size:\" in line:
            print(line)
        elif \"Total Extracted Text:\" in line:
            print(line)

# Generate report
generate_processing_report()
```

These examples demonstrate the versatility and power of the Documents Processor for various real-world applications, from simple document processing to complex knowledge base creation and web application integration.