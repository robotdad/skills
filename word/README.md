# DOCX Skill - Phase 1: Core Infrastructure

**Version:** 0.1.0  
**Status:** Phase 1 Complete - Core Infrastructure  
**License:** MIT

A modular, regeneratable skill for comprehensive Microsoft Word document manipulation following the "bricks and studs" philosophy. This skill provides three tiers of API (Simple → Advanced → OOXML) with robust safety mechanisms and validation.

## Module Contract

### Purpose

Provide safe, validated DOCX document manipulation with multiple abstraction levels:
- **Safety-first operations** - Temp files, transactions, overwrite protection
- **Comprehensive validation** - Structure, styles, content, corruption checking
- **Flexible access** - High-level builders to low-level OOXML

### Public Interface (Phase 1)

```python
from docx_skill import (
    # Safety mechanisms
    TempFileManager,          # Context manager for temp file operations
    SafeFileOperations,       # Safe read/write with overwrite protection
    DocumentTransaction,      # Transactional document operations
    
    # Validation
    ValidationResult,         # Validation result with errors/warnings
    validate_docx,           # Check if file is valid DOCX
    validate_styles,         # Verify style consistency
    validate_structure,      # Check document structure
    validate_content,        # Validate content constraints
    
    # OOXML layer
    OOXMLDocument,           # Wrapper around python-docx Document
    NAMESPACES,              # Common OOXML namespaces
)
```

## Installation

```bash
cd docx-skill
pip install -r requirements.txt
```

## Dependencies

- **python-docx** ≥1.1.0 - Core DOCX manipulation
- **lxml** ≥4.9.0 - XML processing
- **Pillow** ≥10.0.0 - Image handling (for Phase 2)

## Usage Examples

### Safety Mechanisms

#### Temporary File Operations

```python
from docx_skill import TempFileManager

# Automatic cleanup on exit
with TempFileManager() as temp_mgr:
    # Create temp file
    temp_path = temp_mgr.create_temp_file("document.docx")
    
    # Copy existing file to temp
    temp_copy = temp_mgr.copy_to_temp("original.docx")
    
    # Work with temp files...
    # All automatically cleaned up on exit

# Preserve temp files on success
with TempFileManager(cleanup_on_success=False) as temp_mgr:
    temp_path = temp_mgr.create_temp_file("keep.docx")
    # File persists after exit
```

#### Safe File Operations

```python
from docx_skill import SafeFileOperations

ops = SafeFileOperations()

# Write with overwrite protection
try:
    ops.write_file(data, "output.docx", allow_overwrite=False)
except FileExistsError:
    print("File exists, overwrite not allowed")

# Write with confirmation callback
def confirm_overwrite(path):
    return input(f"Overwrite {path}? (y/n): ").lower() == 'y'

ops.write_file(data, "output.docx", confirm_callback=confirm_overwrite)

# Automatic backup on overwrite
ops.write_file(data, "output.docx", allow_overwrite=True, backup=True)
# Creates output.docx.bak before overwriting
```

#### Document Transactions

```python
from docx_skill import DocumentTransaction
from docx import Document

# Transactional operations with rollback
with DocumentTransaction("document.docx") as txn:
    # Get working copy path
    doc = Document(txn.get_working_path())
    
    # Make changes
    doc.add_paragraph("New content")
    doc.save(txn.get_working_path())
    
    # Commit changes (only writes if commit called)
    txn.commit()

# Automatic rollback on error
try:
    with DocumentTransaction("document.docx", backup=True) as txn:
        doc = Document(txn.get_working_path())
        # ... operations that might fail ...
        raise ValueError("Something went wrong")
        txn.commit()  # Never reached
except ValueError:
    pass  # Original file unchanged
```

### Validation

#### Basic DOCX Validation

```python
from docx_skill import validate_docx

# Quick validation
result = validate_docx("document.docx")

if result.is_valid:
    print("Document is valid!")
else:
    print("Validation failed:")
    for error in result.errors:
        print(f"  - {error}")

# Check metadata
print(f"Paragraphs: {result.metadata.get('paragraph_count')}")

# Deep corruption check
result = validate_docx("document.docx", check_corruption=True)
print(f"Validation: {result}")
```

#### Style Validation

```python
from docx_skill import validate_styles

# Check style consistency and usage
result = validate_styles("document.docx")

print(f"Defined styles: {result.metadata['defined_styles']}")
print(f"Used styles: {result.metadata['used_styles']}")

# Review warnings
for warning in result.warnings:
    print(warning)

# Find unused styles
result = validate_styles("document.docx", check_unused=True)
```

#### Structure Validation

```python
from docx_skill import validate_structure

# Check document structure
result = validate_structure("document.docx", require_heading=True)

print(f"Heading count: {result.metadata['heading_count']}")
print(f"Max heading level: {result.metadata.get('max_heading_level')}")

# Enforce heading depth
result = validate_structure("document.docx", max_depth=3)
if not result.is_valid:
    print("Structure issues found:")
    for issue in result.errors + result.warnings:
        print(f"  {issue}")
```

#### Content Validation

```python
from docx_skill import validate_content

# Check word count constraints
result = validate_content("document.docx", min_words=100, max_words=5000)

print(f"Word count: {result.metadata['word_count']:,}")
print(f"Valid: {result.is_valid}")

if not result.is_valid:
    for error in result.errors:
        print(error)
```

### OOXML Layer

#### Basic Operations

```python
from docx_skill import OOXMLDocument

# Create new document
doc = OOXMLDocument()
doc.add_heading("Document Title", level=1)
doc.add_paragraph("This is a paragraph.")
doc.add_heading("Section 1", level=2)
doc.add_paragraph("Section content...")
doc.save("output.docx")

# Load existing document
doc = OOXMLDocument.load("existing.docx")
print(f"Word count: {doc.get_word_count():,}")

# Access paragraphs
for para in doc.get_paragraphs():
    print(para.text)

# Access underlying python-docx Document
docx_obj = doc.document
```

#### Advanced OOXML Access

```python
from docx_skill import OOXMLDocument, NAMESPACES

doc = OOXMLDocument.load("document.docx")

# Get document body element
body = doc.get_body_element()

# Find specific elements
paragraphs = doc.find_elements('p')  # All paragraphs
runs = doc.find_elements('r')        # All runs

# Access core properties
props = doc.get_core_properties()
print(f"Author: {props.author}")
print(f"Title: {props.title}")

# Modify properties
props.author = "New Author"
props.title = "Updated Title"
doc.save()
```

## Architecture

### Module Structure

```
docx-skill/
├── __init__.py           # Public API exports
├── README.md            # This file (contract documentation)
├── requirements.txt     # Dependencies
├── safety.py           # Safe file operations, temp management, transactions
├── validation.py       # Document validation (structure, styles, content)
├── ooxml.py           # OOXML layer (wrapper around python-docx)
└── tests/             # Test suite
    ├── test_safety.py
    ├── test_validation.py
    ├── test_ooxml.py
    └── fixtures/      # Test documents
```

### Design Philosophy

Following the **"bricks and studs" philosophy**:

- **Self-contained module** - All code within docx-skill directory
- **Clear public interface** - Exported via `__all__` in `__init__.py`
- **Regeneratable** - Can be rebuilt from this specification alone
- **Well-documented** - Comprehensive docstrings and examples

### Safety-First Design

All file operations should use the safety mechanisms:

1. **TempFileManager** - For temporary operations with automatic cleanup
2. **SafeFileOperations** - For overwrite protection and confirmations
3. **DocumentTransaction** - For atomic operations with rollback support

## Error Handling

### ValidationResult Pattern

All validation functions return `ValidationResult` objects:

```python
@dataclass
class ValidationResult:
    issues: List[ValidationIssue]  # All errors, warnings, info
    metadata: Dict[str, Any]       # Additional data
    validated_path: Path           # Validated file path
    
    @property
    def is_valid(self) -> bool:
        """True if no ERROR-level issues"""
    
    @property
    def errors(self) -> List[ValidationIssue]:
        """ERROR-level issues only"""
    
    @property
    def warnings(self) -> List[ValidationIssue]:
        """WARNING-level issues only"""
```

### Common Error Conditions

| Error Type | Condition | Recovery Strategy |
|------------|-----------|-------------------|
| FileNotFoundError | Document doesn't exist | Check path, verify file exists |
| FileExistsError | Overwrite not allowed | Set allow_overwrite=True or use callback |
| ValueError | Invalid input/state | Check input constraints, validate first |
| RuntimeError | Transaction/manager misuse | Use within context manager |

## Performance Characteristics

- **Validation**: O(n) where n = document size
  - validate_docx: ~10-50ms for typical documents
  - validate_styles: ~20-100ms (parses styles.xml + document.xml)
  - validate_structure: ~20-100ms (parses all paragraphs)
  
- **Memory**: ~2-5MB overhead per document loaded
  
- **Temp Files**: Cleaned up automatically via context managers
  
- **Thread Safety**: Not thread-safe (use separate instances per thread)

## Testing

### Run Tests

```bash
cd docx-skill
python tests/test_safety.py
python tests/test_validation.py
python tests/test_ooxml.py
```

### Contract Validation

All public interfaces are tested for:
- Correct behavior on valid inputs
- Proper error handling on invalid inputs
- Expected return types and structures
- Side effects (file creation, cleanup, etc.)

## Roadmap

### Phase 1: Core Infrastructure ✅ COMPLETE

- [x] Safety mechanisms (TempFileManager, SafeFileOperations, DocumentTransaction)
- [x] Validation (validate_docx, validate_styles, validate_structure, validate_content)
- [x] OOXML layer (OOXMLDocument wrapper)

### Phase 2: High-Level APIs (NEXT)

- [ ] Simple API (DocumentBuilder with fluent interface)
- [ ] Advanced API (AdvancedDocument, StyleManager, SectionManager, TableBuilder, ImageManager)
- [ ] Router (API recommendation engine)

### Phase 3: Utilities (FUTURE)

- [ ] Conversion utilities (DOCX ↔ other formats)
- [ ] Template system
- [ ] Batch processing helpers

## Regeneration Specification

This module can be regenerated from this specification alone.

**Key invariants that must be preserved:**

1. **Public function signatures** - All exported functions maintain exact signatures
2. **Input/output data structures** - ValidationResult, TempFileInfo, etc.
3. **Error types and conditions** - Same exceptions in same conditions
4. **Side effect behaviors** - Temp cleanup, backup creation, transaction commits

**What can change during regeneration:**

- Internal implementation details
- Private helper functions
- Performance optimizations
- Additional features (as long as existing contract preserved)

## Contributing

When extending this module:

1. **Maintain contract** - Don't break existing public interfaces
2. **Add tests** - Cover new functionality
3. **Update README** - Document new features
4. **Follow philosophy** - Keep it simple, safe, and well-documented

## License

MIT License - See LICENSE file for details
