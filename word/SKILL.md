---
name: word
description: "Microsoft Word document manipulation with safety-first design. Use when tasks require: (1) Creating formatted Word documents programmatically, (2) Validating DOCX files, (3) Safe document operations with automatic cleanup, (4) Transaction-based editing with rollback. Provides three API levels: Simple (DocumentBuilder), Advanced (custom styles/sections), and OOXML (raw XML manipulation)."
version: 0.1.0
license: MIT
---

# Word Document Manipulation Skill

## Overview

A safety-first Word document manipulation skill with three progressive API levels. Built following the modular design philosophy with automatic temp management, validation, and transactional operations.

**Current Status:** Phase 1 Complete (Core Infrastructure)

## Workflow Decision Tree

### Creating a simple formatted document
→ Use Simple API (DocumentBuilder) - See "Quick Start" below

### Need custom styles, sections, or complex layouts
→ Use Advanced API - **Coming in Phase 2**

### Need to edit existing DOCX or access raw OOXML
→ Use OOXML API - See "OOXML Layer" below

### Validating a DOCX file
→ Use validation functions - See "Validation" section

### Need safe temp file operations
→ Use TempFileManager - See "Safety Mechanisms" section

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

## Phase 2 & 3 (Coming Soon)

### Simple API (Phase 2)
```python
from word import DocumentBuilder

doc = DocumentBuilder()
doc.add_heading("Report", level=1)
doc.add_paragraph("Content", bold=False)
doc.add_list(["Item 1", "Item 2"], numbered=False)
doc.save("report.docx")  # 5 lines instead of 200!
```

### Advanced API (Phase 2)
- Custom styles and themes
- Multiple sections with different layouts
- Advanced table features (merged cells, borders)
- Headers/footers
- Complex image placement

### Utilities (Phase 3)
- Format conversion (DOCX ↔ Markdown, PDF)
- Document templates
- Batch processing helpers

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
├── safety.py           # TempFileManager, SafeFileOperations, DocumentTransaction
├── validation.py       # ValidationResult, validate_* functions
├── ooxml.py           # OOXMLDocument wrapper
├── requirements.txt    # Dependencies
└── tests/             # Test suite
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
