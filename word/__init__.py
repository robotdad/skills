"""
DOCX Skill - Comprehensive Microsoft Word Document Manipulation

A three-tier API for working with DOCX documents:

1. **Simple API** (simple.py) - High-level builder pattern for common tasks
   - Quick document creation
   - Minimal code for common operations
   - Recommended for most use cases

2. **Advanced API** (advanced.py) - Detailed control over formatting and structure
   - Style management
   - Section control
   - Table and image handling
   - Complex formatting

3. **OOXML API** (ooxml.py) - Direct XML manipulation for power users
   - Full control over document structure
   - Custom XML elements
   - Advanced OOXML operations

Core Infrastructure (Phase 1 - Available Now):
    - Safety mechanisms (temp files, transactions, overwrite protection)
    - Validation (document structure, styles, content)
    - OOXML foundation layer

Coming Soon (Phase 2 & 3):
    - Simple API (DocumentBuilder)
    - Advanced API (AdvancedDocument, StyleManager, etc.)
    - Router (API recommendation engine)
    - Conversion utilities

Example Usage:
    >>> # Phase 1: Core infrastructure
    >>> from docx_skill.safety import TempFileManager, DocumentTransaction
    >>> from docx_skill.validation import validate_docx
    >>> from docx_skill.ooxml import OOXMLDocument
    >>> 
    >>> # Safe temp file operations
    >>> with TempFileManager() as temp_mgr:
    ...     temp_path = temp_mgr.create_temp_file("work.docx")
    ...     # Work with temp file...
    >>> 
    >>> # Validate documents
    >>> result = validate_docx("document.docx")
    >>> if result.is_valid:
    ...     print("Document is valid!")
    >>> 
    >>> # OOXML layer operations
    >>> doc = OOXMLDocument()
    >>> doc.add_heading("Title", level=1)
    >>> doc.add_paragraph("Content")
    >>> doc.save("output.docx")

Version: 0.1.0 (Phase 1 - Core Infrastructure)
"""

# Phase 1: Core Infrastructure (AVAILABLE NOW)
from .safety import (
    TempFileManager,
    SafeFileOperations,
    DocumentTransaction,
    TempFileInfo,
)

from .validation import (
    ValidationResult,
    ValidationIssue,
    ValidationLevel,
    validate_docx,
    validate_styles,
    validate_structure,
    validate_content,
)

from .ooxml import (
    OOXMLDocument,
    NAMESPACES,
    qualified_name,
    get_xml_element,
    get_xml_elements,
    set_xml_property,
)

# Public API exports
__all__ = [
    # Safety
    'TempFileManager',
    'SafeFileOperations',
    'DocumentTransaction',
    'TempFileInfo',
    
    # Validation
    'ValidationResult',
    'ValidationIssue',
    'ValidationLevel',
    'validate_docx',
    'validate_styles',
    'validate_structure',
    'validate_content',
    
    # OOXML
    'OOXMLDocument',
    'NAMESPACES',
    'qualified_name',
    'get_xml_element',
    'get_xml_elements',
    'set_xml_property',
]

__version__ = '0.1.0'
__author__ = 'Amplifier AI'
__license__ = 'MIT'
