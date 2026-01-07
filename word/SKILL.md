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

## Quick Start

### Installation

```bash
cd skills/word
pip install -r requirements.txt
```

### Basic Usage - Safety Mechanisms

```python
from docx_skill import TempFileManager, validate_docx, OOXMLDocument

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
print(f"Paragraphs: {len(doc.paragraphs)}")
print(f"Title: {doc.core_properties.title}")
```

### Transactional Operations

```python
from docx_skill import DocumentTransaction, OOXMLDocument

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
with TempFileManager(prefix="word_") as temp_mgr:
    temp_file = temp_mgr.create_temp_file("output.docx")
    temp_dir = temp_mgr.create_temp_dir()
    # Automatic cleanup on exit or error
```

**SafeFileOperations** - Overwrite protection and backups
```python
from docx_skill import SafeFileOperations

# Prevents accidental overwrites
SafeFileOperations.safe_write(content, "output.docx")  # Prompts if exists
SafeFileOperations.safe_write(content, "output.docx", force=True)  # Skip prompt
```

**DocumentTransaction** - Rollback support
```python
with DocumentTransaction("doc.docx") as txn:
    # Work with txn.get_working_path()
    # Commit to persist, otherwise rolls back
    txn.commit()
```

### Validation

**validate_docx** - Check if file is valid DOCX
```python
result = validate_docx("file.docx")
# Returns ValidationResult with is_valid, errors, warnings, info
```

**validate_styles** - Check style consistency
```python
result = validate_styles(doc)
# Checks for unused styles, style consistency
```

**validate_structure** - Verify document structure
```python
result = validate_structure(doc)
# Checks heading hierarchy, section structure
```

**validate_content** - Content constraints
```python
result = validate_content(doc, min_words=100, max_words=5000)
# Validates word count and other constraints
```

### OOXML Layer

**OOXMLDocument** - Wrapper around python-docx Document

```python
from docx_skill import OOXMLDocument

# Create new document
doc = OOXMLDocument.create()
doc.add_heading("Title", level=1)
doc.add_paragraph("Content here")
doc.save("output.docx")

# Load existing document
doc = OOXMLDocument.load("input.docx")

# Access structure
for para in doc.paragraphs:
    print(para.text)

for table in doc.tables:
    print(f"Table: {len(table.rows)} rows")

# Access properties
props = doc.core_properties
print(f"Author: {props.author}")
print(f"Title: {props.title}")
```

## Phase 2 & 3 (Coming Soon)

### Simple API (Phase 2)
```python
from docx_skill import DocumentBuilder

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
from docx_skill import NAMESPACES

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
# Run all tests
cd skills/word
python -m pytest tests/ -v

# Run specific test module
python -m pytest tests/test_safety.py -v
python -m pytest tests/test_validation.py -v
python -m pytest tests/test_ooxml.py -v
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

## See Also

- **README.md** - Complete module contract documentation
- **Phase 2 Design** - Simple & Advanced APIs (in development)
- **Phase 3 Design** - Conversion utilities (planned)
