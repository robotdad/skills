---
name: word
description: "Microsoft Word document manipulation with safety-first design. Use when tasks require: (1) Creating formatted Word documents programmatically, (2) Converting DOCX to Markdown for LLM workflows, (3) Validating DOCX files, (4) Safe document operations with automatic cleanup, (5) Transaction-based editing with rollback. Provides three API levels: Simple (DocumentBuilder), Advanced (custom styles/sections), and OOXML (raw XML manipulation). Includes markitdown integration for zero-dependency DOCX→Markdown conversion."
version: 0.3.0
license: MIT
---

# Word Document Manipulation Skill

## Overview

A safety-first Word document manipulation skill with three progressive API levels. Built following the modular design philosophy with automatic temp management, validation, and transactional operations.

**Current Status:** Phase 1, 2 & 3 Complete (Core Infrastructure + High-Level APIs + Format Conversion)

## Workflow Decision Tree

### Creating a simple formatted document
→ Use Simple API (DocumentBuilder) - See "Simple API" section

### Need custom styles, sections, or complex layouts
→ Use Advanced API (AdvancedDocument) - See "Advanced API" section

### Need to edit existing DOCX or access raw OOXML
→ Use OOXML API - See "OOXML Layer" below

### Validating a DOCX file
→ Use validation functions - See "Validation" section

### Need safe temp file operations
→ Use TempFileManager - See "Safety Mechanisms" section

### Converting DOCX to Markdown for LLM consumption
→ Use conversion functions - See "Format Conversion" section

### Extracting plain text from DOCX
→ Use extract_text - See "Format Conversion" section

## One-Time Setup

**Use `uv` for isolated environment:**

```bash
# Navigate to skill directory (wherever skills are loaded from)
cd /path/to/skills/word  # e.g., ~/.amplifier/skills/word or ./skills/word

# Create virtual environment with uv
uv venv

# Install dependencies
uv pip install -r requirements.txt
```

**Verify installation:**

```bash
source .venv/bin/activate
python -c "from word import OOXMLDocument; print('✓ Word skill installed')"
deactivate
```

## Quick Start

### Option 1: Using venv Python directly (recommended for agents)

```bash
# Full path to venv Python
/path/to/skills/word/.venv/bin/python your_script.py
```

### Option 2: Activate venv first (interactive use)

```bash
source /path/to/skills/word/.venv/bin/activate
python your_script.py
deactivate  # when done
```

### Option 3: Add to PYTHONPATH (for scripts in other directories)

```python
import sys
sys.path.insert(0, '/path/to/skills')  # Parent of word/

from word import OOXMLDocument, TempFileManager, validate_docx
```

### Basic Usage - Safety Mechanisms

```python
from word import TempFileManager, validate_docx, OOXMLDocument

# Safe temp operations with automatic cleanup
with TempFileManager() as temp_mgr:
    temp_path = temp_mgr.create_temp_file("work.docx")
    # Work with temp file...
    # Automatically cleaned up on exit

# Validate a document
result = validate_docx("document.docx")
if result.is_valid:
    print("✓ Valid DOCX")
else:
    print(f"✗ Errors: {result.errors}")

# Load and inspect document structure
doc = OOXMLDocument.load("document.docx")
paragraphs = doc.get_paragraphs()
print(f"Paragraphs: {len(paragraphs)}")
props = doc.get_core_properties()
print(f"Title: {props.title}")
```

### Transactional Operations

```python
from word import DocumentTransaction, OOXMLDocument

# Atomic document operations with rollback
with DocumentTransaction("input.docx") as txn:
    doc = OOXMLDocument.load(txn.get_working_path())
    
    # Make changes
    doc.add_paragraph("New content")
    doc.save(txn.get_working_path())
    
    # Only persists if commit is called
    txn.commit()
    # If exception occurs, automatically rolls back
```

## Phase 1 Features (Available Now)

### Safety Mechanisms

**TempFileManager** - Context manager for automatic temp cleanup
```python
from word import TempFileManager

with TempFileManager() as temp_mgr:
    temp_file = temp_mgr.create_temp_file("output.docx")
    temp_dir = temp_mgr.get_temp_dir()
    # Automatic cleanup on exit or error
```

**SafeFileOperations** - Overwrite protection and backups
```python
from word import SafeFileOperations

ops = SafeFileOperations()
# Prevents accidental overwrites
ops.write_file(content_bytes, "output.docx", allow_overwrite=False)
```

**DocumentTransaction** - Rollback support
```python
from word import DocumentTransaction

with DocumentTransaction("doc.docx") as txn:
    # Work with txn.get_working_path()
    # Commit to persist, otherwise rolls back
    txn.commit()
```

### Validation

**validate_docx** - Check if file is valid DOCX
```python
from word import validate_docx

result = validate_docx("file.docx")
# Returns ValidationResult with is_valid, errors, warnings, info
```

**validate_styles** - Check style consistency
```python
from word import validate_styles, OOXMLDocument

doc = OOXMLDocument.load("file.docx")
result = validate_styles(doc.document)  # Pass python-docx Document object
# Checks for unused styles, style consistency
```

**validate_structure** - Verify document structure
```python
from word import validate_structure, OOXMLDocument

doc = OOXMLDocument.load("file.docx")
result = validate_structure(doc.document)
# Checks heading hierarchy, section structure
```

**validate_content** - Content constraints
```python
from word import validate_content, OOXMLDocument

doc = OOXMLDocument.load("file.docx")
result = validate_content(doc.document, min_words=100, max_words=5000)
# Validates word count and other constraints
```

### OOXML Layer

**OOXMLDocument** - Wrapper around python-docx Document

```python
from word import OOXMLDocument

# Create new document (uses modern Aptos template by default)
doc = OOXMLDocument()
doc.add_heading("Title", level=1)
doc.add_paragraph("Content here")
doc.save("output.docx")

# Create with legacy Calibri template (for compatibility)
doc = OOXMLDocument(use_modern_template=False)

# Load existing document
doc = OOXMLDocument.load("input.docx")

# Access structure
for para in doc.get_paragraphs():
    print(para.text)

for table in doc.get_tables():
    print(f"Table: {len(table.rows)} rows")

# Access properties
props = doc.get_core_properties()
print(f"Author: {props.author}")
print(f"Title: {props.title}")
```

## Phase 2 Features (Available Now)

### Simple API - DocumentBuilder

The Simple API provides a fluent interface for creating documents quickly:

```python
from word import DocumentBuilder

# Method chaining for concise document creation
doc = (DocumentBuilder()
    .add_heading("Monthly Report", level=1)
    .add_paragraph("Executive Summary", bold=True)
    .add_paragraph("This report covers Q4 performance metrics.")
    .add_heading("Key Metrics", level=2)
    .add_list([
        "Revenue increased 15%",
        "Customer satisfaction: 94%",
        "New features delivered: 12"
    ], numbered=False)
    .add_heading("Data Table", level=2)
    .add_table(
        data=[["Q3", "100K"], ["Q4", "115K"]],
        headers=["Quarter", "Revenue"]
    )
    .add_page_break()
    .add_heading("Conclusion", level=1)
    .add_paragraph("Goals exceeded across all metrics.")
    .save("report.docx"))
```

**Available methods:**
- `add_heading(text, level=1)` - Add heading (levels 1-9)
- `add_paragraph(text, bold=False, italic=False, font_size=None)` - Add formatted paragraph
- `add_list(items, numbered=False)` - Add bulleted or numbered list
- `add_table(data, headers=None)` - Add table from 2D array
- `add_image(path, width_inches=None)` - Add image with optional sizing
- `add_page_break()` - Add page break
- `save(output_path, overwrite=False)` - Save with protection

### Advanced API - Full Control

For complex documents requiring custom styles, sections, and layouts:

```python
from word import AdvancedDocument

# Create document with advanced features
doc = AdvancedDocument()

# Create custom styles
doc.styles.add_paragraph_style("Highlight", font_size=14, bold=True)
doc.styles.add_paragraph_style("Code", font_name="Courier New", font_size=10)

# Configure page layout
doc.sections.set_margins(top=1.0, bottom=1.0, left=1.5, right=1.5)
doc.sections.add_header("Confidential Report")
doc.sections.add_footer("Page X")

# Add content with custom styles
doc.add_heading("Technical Specification", level=1)
doc.add_paragraph("Important note", style="Highlight")
doc.add_paragraph("def example():\n    return True", style="Code")

# Create complex table
table = doc.tables.create_table(rows=3, cols=4)
# Populate table cells...

doc.save("advanced_doc.docx")
```

**Available managers:**
- `doc.styles` - StyleManager for custom paragraph and character styles
- `doc.sections` - SectionManager for page layout, margins, headers/footers
- `doc.tables` - TableBuilder for advanced table features
- `doc.images` - ImageManager for precise image control

### API Router - Get Recommendations

Let the router suggest which API level to use:

```python
from word import recommend_api

# Get recommendation for your task
rec = recommend_api("Create a document with custom fonts and colors")

print(rec.api_level)      # "advanced"
print(rec.reasoning)      # Why this API was recommended
print(rec.example_code)   # Working code example
print(rec.alternatives)   # Other options to consider
```

## Phase 3 Features (Available Now)

### Format Conversion

Convert DOCX documents to Markdown or extract plain text for LLM workflows, analysis, or processing.

**DOCX to Markdown** - Using markitdown (zero system dependencies)

```python
from word import docx_to_markdown, is_markitdown_available

# Check if markitdown is installed
if not is_markitdown_available():
    print("Install with: pip install markitdown")
    # Or: pip install 'markitdown[all]' for full features

# Convert DOCX to Markdown file
markdown = docx_to_markdown("contract.docx", "contract.md")
print(f"Converted {len(markdown)} characters")

# Convert to string only (no file output)
markdown_text = docx_to_markdown("report.docx")

# Use in LLM workflow
markdown = docx_to_markdown("document.docx")
# Pass markdown to your LLM for analysis, summarization, etc.
```

**Extract Plain Text** - Using python-docx (no additional dependencies)

```python
from word import extract_text

# Extract all text content (no formatting)
text = extract_text("document.docx")
word_count = len(text.split())
print(f"Document has {word_count} words")

# Search for keywords
text = extract_text("report.docx")
if "conclusion" in text.lower():
    print("Document contains conclusion section")

# Extract for text analysis
text = extract_text("article.docx")
# Perform sentiment analysis, keyword extraction, etc.
```

**Why markitdown?**
- **Zero system dependencies** - Just `pip install markitdown`, no pandoc/LibreOffice required
- **LLM-optimized** - Designed specifically for AI/RAG workflows
- **Structure preservation** - Maintains document hierarchy perfectly for LLM consumption
- **Microsoft-backed** - Official Microsoft library for document conversion

**Installation:**
```bash
# Basic installation
pip install markitdown

# Full features (recommended)
pip install 'markitdown[all]'
```

## Error Handling

All operations return clear error messages:

```python
try:
    result = validate_docx("corrupted.docx")
    if not result.is_valid:
        print(f"Validation failed:")
        for error in result.errors:
            print(f"  - {error}")
except FileNotFoundError:
    print("File not found")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Common OOXML Namespaces

```python
from word import NAMESPACES

# Word processing ML
NAMESPACES['w']     # http://schemas.openxmlformats.org/wordprocessingml/2006/main
NAMESPACES['r']     # http://schemas.openxmlformats.org/officeDocument/2006/relationships
NAMESPACES['wp']    # http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing
```

## Dependencies

- **python-docx** ≥1.1.0 - Core DOCX manipulation
- **lxml** ≥4.9.0 - XML processing
- **Pillow** ≥10.0.0 - Image processing

## Testing

```bash
# Run all tests (from skill directory, with venv activated)
cd /path/to/skills/word
source .venv/bin/activate
python -m pytest tests/ -v

# Or use venv Python directly
.venv/bin/python -m pytest tests/ -v
```

## Architecture

**Module Structure:**
```
word/
├── __init__.py          # Public API exports
├── simple.py           # DocumentBuilder (Simple API)
├── advanced.py         # AdvancedDocument + managers (Advanced API)
├── router.py           # API recommendation engine
├── safety.py           # TempFileManager, SafeFileOperations, DocumentTransaction
├── validation.py       # ValidationResult, validate_* functions
├── ooxml.py           # OOXMLDocument wrapper (OOXML API)
├── templates/         # Document templates
│   └── modern.docx    # Microsoft 365 default (Aptos)
├── requirements.txt    # Dependencies
└── tests/             # Test suite
    ├── test_simple.py
    ├── test_advanced.py
    ├── test_router.py
    ├── test_safety.py
    ├── test_validation.py
    └── test_ooxml.py
```

**Design Philosophy:**
- Safety first: Auto-cleanup, overwrite protection, transactions
- Progressive complexity: Simple → Advanced → OOXML
- Clear contracts: Each module independently regeneratable
- Validation everywhere: Catch errors before they happen

## Performance Characteristics

- **TempFileManager**: O(1) cleanup, uses context managers
- **Validation**: O(n) where n = document elements
- **OOXMLDocument**: Lazy loading, minimal memory overhead

## Modern Template (Microsoft 365)

By default, `OOXMLDocument()` uses the modern Microsoft 365 template bundled at `templates/modern.docx`:

- **Body font:** Aptos (Microsoft 365 default since 2024)
- **Heading font:** Aptos Display
- **Legacy font:** Calibri (Office 2007-2023)

To use the legacy template for compatibility with older systems:
```python
doc = OOXMLDocument(use_modern_template=False)
```
