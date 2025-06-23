#!/usr/bin/env python3
"""
Setup script for Documents Processor

This allows the project to be installed as a Python package.
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_file(filename):
    """Read file content for use in setup"""
    with open(os.path.join(os.path.dirname(__file__), filename), 'r', encoding='utf-8') as f:
        return f.read()

# Read requirements from files
def read_requirements(filename):
    """Read requirements from a file, filtering out comments and empty lines"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return [
                line.strip() 
                for line in f 
                if line.strip() and not line.startswith('#')
            ]
    except FileNotFoundError:
        return []

setup(
    name="documents-processor",
    version="1.0.0",
    author="Documents Processor Team",
    author_email="contact@documentsprocessor.dev",
    description="A comprehensive document processing utility supporting multiple formats with AI integration",
    long_description=read_file("README.md") if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    url="https://github.com/NumericalArt/Documents_processor",
    
    # Package discovery
    py_modules=["documents_processor"],
    
    # Dependencies
    install_requires=read_requirements("requirements.txt"),
    
    # Optional dependencies
    extras_require={
        "ai": ["openai>=1.0.0"],
        "rar": ["rarfile>=4.0"],
        "full": ["openai>=1.0.0", "rarfile>=4.0"],
    },
    
    # Python version requirement
    python_requires=">=3.7",
    
    # Classifiers
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business",
        "Topic :: Text Processing",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    
    # Keywords
    keywords="document processing pdf ocr ai image text extraction batch processing",
    
    # Entry points (optional - for command line scripts)
    entry_points={
        "console_scripts": [
            "documents-processor=documents_processor:batch_process_folder",
        ],
    },
    
    # Include additional files
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.rst", "*.yml", "*.yaml"],
    },
    
    # Project URLs
    project_urls={
        "Bug Reports": "https://github.com/NumericalArt/Documents_processor/issues",
        "Source": "https://github.com/NumericalArt/Documents_processor",
        "Documentation": "https://github.com/NumericalArt/Documents_processor/blob/main/README.md",
    },
)