"""
Test suite for ooxml.py module

Tests OOXMLDocument wrapper and OOXML utility functions
"""

import sys
from pathlib import Path

# Add parent directory to path to import docx_skill
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.ooxml import OOXMLDocument, NAMESPACES, qualified_name, get_xml_element, get_xml_elements
import tempfile
import shutil


def test_ooxml_document_creation():
    """Test creating and saving new documents."""
    print("\n=== Testing OOXMLDocument Creation ===")
    
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        # Test creating new document
        print("Test 1: Create new document")
        doc = OOXMLDocument()
        assert doc.document is not None
        assert doc.path is None
        print("  ✓ New document created")
        
        # Test adding content
        print("\nTest 2: Add content to document")
        doc.add_heading("Test Document", level=1)
        doc.add_paragraph("This is a test paragraph.")
        doc.add_heading("Section 1", level=2)
        doc.add_paragraph("Section content here.")
        doc.add_page_break()
        doc.add_paragraph("Content on page 2.")
        
        paragraphs = doc.get_paragraphs()
        print(f"  Added {len(paragraphs)} paragraphs")
        assert len(paragraphs) >= 4
        print("  ✓ Content added successfully")
        
        # Test saving
        print("\nTest 3: Save document")
        output_path = temp_dir / "test_output.docx"
        saved_path = doc.save(output_path)
        
        assert saved_path.exists()
        assert doc.path == saved_path
        print(f"  ✓ Document saved: {saved_path}")
        
        print("\n✓ All creation tests passed!")
        
    finally:
        shutil.rmtree(temp_dir)


def test_ooxml_document_loading():
    """Test loading existing documents."""
    print("\n=== Testing OOXMLDocument Loading ===")
    
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        # Create a document first
        print("Test 1: Create document to load")
        doc = OOXMLDocument()
        doc.add_heading("Test Document", level=1)
        doc.add_paragraph("First paragraph.")
        doc.add_paragraph("Second paragraph.")
        doc.add_paragraph("Third paragraph.")
        
        doc_path = temp_dir / "load_test.docx"
        doc.save(doc_path)
        print(f"  Created document: {doc_path}")
        
        # Test loading
        print("\nTest 2: Load document")
        loaded_doc = OOXMLDocument.load(doc_path)
        
        assert loaded_doc.path == doc_path
        assert len(loaded_doc.get_paragraphs()) == 4  # Heading + 3 paragraphs
        print(f"  ✓ Document loaded: {len(loaded_doc.get_paragraphs())} paragraphs")
        
        # Test getting text
        print("\nTest 3: Get document text")
        text = loaded_doc.get_text()
        assert "Test Document" in text
        assert "First paragraph" in text
        print(f"  ✓ Text extracted ({len(text)} characters)")
        
        # Test word count
        print("\nTest 4: Get word count")
        word_count = loaded_doc.get_word_count()
        assert word_count > 0
        print(f"  ✓ Word count: {word_count}")
        
        # Test repr
        print("\nTest 5: String representation")
        repr_str = repr(loaded_doc)
        assert "OOXMLDocument" in repr_str
        print(f"  ✓ Repr: {repr_str}")
        
        print("\n✓ All loading tests passed!")
        
    finally:
        shutil.rmtree(temp_dir)


def test_ooxml_document_access():
    """Test accessing document elements."""
    print("\n=== Testing OOXMLDocument Element Access ===")
    
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        # Create document with various elements
        print("Test 1: Create document with tables and sections")
        doc = OOXMLDocument()
        doc.add_heading("Document with Table", level=1)
        doc.add_paragraph("Before table")
        
        # Add a table using python-docx
        table = doc.document.add_table(rows=2, cols=2)
        table.cell(0, 0).text = "Cell 1,1"
        table.cell(0, 1).text = "Cell 1,2"
        table.cell(1, 0).text = "Cell 2,1"
        table.cell(1, 1).text = "Cell 2,2"
        
        doc.add_paragraph("After table")
        
        # Test getting tables
        print("\nTest 2: Get tables")
        tables = doc.get_tables()
        assert len(tables) == 1
        print(f"  ✓ Found {len(tables)} table(s)")
        
        # Test getting sections
        print("\nTest 3: Get sections")
        sections = doc.get_sections()
        assert len(sections) >= 1
        print(f"  ✓ Found {len(sections)} section(s)")
        
        # Test getting body element
        print("\nTest 4: Get body element")
        body = doc.get_body_element()
        assert body is not None
        print("  ✓ Body element accessed")
        
        # Test finding elements
        print("\nTest 5: Find paragraph elements")
        paragraphs = doc.find_elements('p')
        print(f"  Found {len(paragraphs)} paragraph elements")
        assert len(paragraphs) > 0
        print("  ✓ Elements found via XPath")
        
        print("\n✓ All element access tests passed!")
        
    finally:
        shutil.rmtree(temp_dir)


def test_ooxml_properties():
    """Test document properties access."""
    print("\n=== Testing Document Properties ===")
    
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        print("Test 1: Access and modify core properties")
        doc = OOXMLDocument()
        doc.add_paragraph("Test content")
        
        # Get properties
        props = doc.get_core_properties()
        
        # Set properties
        props.author = "Test Author"
        props.title = "Test Document"
        props.subject = "Testing"
        props.keywords = "test, docx, ooxml"
        
        print(f"  Author: {props.author}")
        print(f"  Title: {props.title}")
        print(f"  Subject: {props.subject}")
        print(f"  Keywords: {props.keywords}")
        
        # Save and reload to verify persistence
        doc_path = temp_dir / "properties_test.docx"
        doc.save(doc_path)
        
        # Reload and check
        loaded_doc = OOXMLDocument.load(doc_path)
        loaded_props = loaded_doc.get_core_properties()
        
        assert loaded_props.author == "Test Author"
        assert loaded_props.title == "Test Document"
        print("  ✓ Properties persisted correctly")
        
        print("\n✓ All properties tests passed!")
        
    finally:
        shutil.rmtree(temp_dir)


def test_ooxml_utilities():
    """Test OOXML utility functions."""
    print("\n=== Testing OOXML Utilities ===")
    
    # Test qualified_name
    print("Test 1: qualified_name function")
    qname = qualified_name('w', 'p')
    assert 'wordprocessingml' in qname
    assert 'p' in qname
    print(f"  ✓ Qualified name: {qname}")
    
    # Test with document
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        doc = OOXMLDocument()
        doc.add_paragraph("Test paragraph 1")
        doc.add_paragraph("Test paragraph 2")
        
        body = doc.get_body_element()
        
        # Test get_xml_element
        print("\nTest 2: get_xml_element function")
        first_para = get_xml_element(body, './/w:p', NAMESPACES)
        assert first_para is not None
        print("  ✓ Found first paragraph element")
        
        # Test get_xml_elements
        print("\nTest 3: get_xml_elements function")
        all_paras = get_xml_elements(body, './/w:p', NAMESPACES)
        assert len(all_paras) == 2
        print(f"  ✓ Found {len(all_paras)} paragraph elements")
        
        print("\n✓ All utility tests passed!")
        
    finally:
        shutil.rmtree(temp_dir)


def test_ooxml_clear_content():
    """Test clearing document content."""
    print("\n=== Testing Clear Content ===")
    
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        print("Test 1: Clear document content")
        doc = OOXMLDocument()
        doc.add_heading("Title", level=1)
        doc.add_paragraph("Paragraph 1")
        doc.add_paragraph("Paragraph 2")
        doc.add_paragraph("Paragraph 3")
        
        initial_count = len(doc.get_paragraphs())
        print(f"  Initial paragraphs: {initial_count}")
        assert initial_count == 4
        
        # Clear content
        doc.clear_content()
        
        # Add new content
        doc.add_paragraph("Fresh start")
        
        final_count = len(doc.get_paragraphs())
        print(f"  Final paragraphs: {final_count}")
        assert final_count == 1
        print("  ✓ Content cleared and replaced")
        
        print("\n✓ Clear content test passed!")
        
    finally:
        shutil.rmtree(temp_dir)


def run_all_tests():
    """Run all OOXML tests."""
    print("=" * 60)
    print("DOCX Skill - OOXML Module Tests")
    print("=" * 60)
    
    try:
        test_ooxml_document_creation()
        test_ooxml_document_loading()
        test_ooxml_document_access()
        test_ooxml_properties()
        test_ooxml_utilities()
        test_ooxml_clear_content()
        
        print("\n" + "=" * 60)
        print("✓ ALL OOXML TESTS PASSED!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"✗ TEST FAILED: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
