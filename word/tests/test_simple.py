"""
Tests for simple.py - DocumentBuilder API

Tests cover:
- Basic document creation
- Method chaining
- Content addition (headings, paragraphs, lists, tables, images)
- Formatting options
- Safe saving with overwrite protection
- Error handling
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from PIL import Image
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from simple import DocumentBuilder
from ooxml import OOXMLDocument


class TestDocumentBuilder:
    """Test DocumentBuilder class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files."""
        temp = Path(tempfile.mkdtemp(prefix="test_simple_"))
        yield temp
        shutil.rmtree(temp, ignore_errors=True)
    
    @pytest.fixture
    def test_image(self, temp_dir):
        """Create a test image file."""
        image_path = temp_dir / "test_image.png"
        img = Image.new('RGB', (100, 100), color='red')
        img.save(image_path)
        return image_path
    
    def test_create_empty_document(self):
        """Test creating empty document."""
        builder = DocumentBuilder()
        assert builder is not None
        assert isinstance(builder.get_document(), OOXMLDocument)
    
    def test_create_with_legacy_template(self):
        """Test creating document with legacy template."""
        builder = DocumentBuilder(template="legacy")
        assert builder is not None
    
    def test_add_heading(self):
        """Test adding heading."""
        builder = DocumentBuilder()
        result = builder.add_heading("Test Heading", level=1)
        
        # Should return self for chaining
        assert result is builder
        
        # Check heading was added
        doc = builder.get_document()
        paragraphs = doc.get_paragraphs()
        # Modern template may have initial paragraph
        assert len(paragraphs) >= 1
        # Find the heading
        heading_found = any("Test Heading" in p.text for p in paragraphs)
        assert heading_found
    
    def test_add_paragraph(self):
        """Test adding paragraph."""
        builder = DocumentBuilder()
        result = builder.add_paragraph("Test paragraph")
        
        assert result is builder
        
        doc = builder.get_document()
        paragraphs = doc.get_paragraphs()
        # Modern template may have initial paragraph
        assert len(paragraphs) >= 1
        # Find the paragraph we added
        para_found = any(p.text == "Test paragraph" for p in paragraphs)
        assert para_found
    
    def test_add_paragraph_with_formatting(self):
        """Test adding paragraph with formatting."""
        builder = DocumentBuilder()
        builder.add_paragraph("Bold text", bold=True)
        builder.add_paragraph("Italic text", italic=True)
        builder.add_paragraph("Large text", font_size=18)
        
        doc = builder.get_document()
        paragraphs = doc.get_paragraphs()
        # Modern template may have initial paragraph
        assert len(paragraphs) >= 3
        
        # Find our paragraphs (skip any initial empty ones)
        non_empty = [p for p in paragraphs if p.text]
        
        # Check bold
        bold_para = next(p for p in non_empty if "Bold" in p.text)
        assert bold_para.runs[0].bold is True
        
        # Check italic
        italic_para = next(p for p in non_empty if "Italic" in p.text)
        assert italic_para.runs[0].italic is True
        
        # Check font size (18pt)
        large_para = next(p for p in non_empty if "Large" in p.text)
        assert large_para.runs[0].font.size.pt == 18
    
    def test_add_bulleted_list(self):
        """Test adding bulleted list."""
        items = ["Item 1", "Item 2", "Item 3"]
        builder = DocumentBuilder()
        result = builder.add_list(items, numbered=False)
        
        assert result is builder
        
        doc = builder.get_document()
        paragraphs = doc.get_paragraphs()
        # Should have at least the 3 list items
        assert len(paragraphs) >= 3
        
        # Check that all items appear in document
        doc_text = ' '.join(p.text for p in paragraphs)
        for item in items:
            assert item in doc_text
    
    def test_add_numbered_list(self):
        """Test adding numbered list."""
        items = ["Step 1", "Step 2", "Step 3"]
        builder = DocumentBuilder()
        builder.add_list(items, numbered=True)
        
        doc = builder.get_document()
        paragraphs = doc.get_paragraphs()
        # Should have at least the 3 list items
        assert len(paragraphs) >= 3
        
        # Check that all items appear in document
        doc_text = ' '.join(p.text for p in paragraphs)
        for item in items:
            assert item in doc_text
    
    def test_add_table_without_headers(self):
        """Test adding table without headers."""
        data = [
            ["A1", "B1", "C1"],
            ["A2", "B2", "C2"],
        ]
        
        builder = DocumentBuilder()
        result = builder.add_table(data)
        
        assert result is builder
        
        doc = builder.get_document()
        tables = doc.get_tables()
        assert len(tables) == 1
        
        table = tables[0]
        assert len(table.rows) == 2
        assert len(table.columns) == 3
        assert table.rows[0].cells[0].text == "A1"
    
    def test_add_table_with_headers(self):
        """Test adding table with headers."""
        data = [
            ["John", "Doe"],
            ["Jane", "Smith"],
        ]
        headers = ["First", "Last"]
        
        builder = DocumentBuilder()
        builder.add_table(data, headers=headers)
        
        doc = builder.get_document()
        tables = doc.get_tables()
        table = tables[0]
        
        # Should have 3 rows (1 header + 2 data)
        assert len(table.rows) == 3
        
        # Check header row
        assert table.rows[0].cells[0].text == "First"
        assert table.rows[0].cells[1].text == "Last"
        
        # Check data rows
        assert table.rows[1].cells[0].text == "John"
        assert table.rows[2].cells[0].text == "Jane"
    
    def test_add_image(self, temp_dir, test_image):
        """Test adding image."""
        builder = DocumentBuilder()
        result = builder.add_image(str(test_image))
        
        assert result is builder
    
    def test_add_image_with_width(self, temp_dir, test_image):
        """Test adding image with specific width."""
        builder = DocumentBuilder()
        builder.add_image(str(test_image), width_inches=5.0)
        
        # Document should have inline shapes (images)
        doc = builder.get_document()
        # Images are added to paragraphs, check if added
        assert len(doc.get_paragraphs()) > 0
    
    def test_add_image_not_found(self):
        """Test adding non-existent image."""
        builder = DocumentBuilder()
        
        with pytest.raises(FileNotFoundError):
            builder.add_image("nonexistent.jpg")
    
    def test_add_page_break(self):
        """Test adding page break."""
        builder = DocumentBuilder()
        result = builder.add_page_break()
        
        assert result is builder
        
        doc = builder.get_document()
        paragraphs = doc.get_paragraphs()
        # Page break creates a paragraph, modern template may have initial paragraph
        assert len(paragraphs) >= 1
    
    def test_method_chaining(self):
        """Test method chaining."""
        builder = (DocumentBuilder()
                   .add_heading("Title", level=1)
                   .add_paragraph("First paragraph")
                   .add_paragraph("Second paragraph")
                   .add_list(["A", "B", "C"])
                   .add_page_break())
        
        doc = builder.get_document()
        paragraphs = doc.get_paragraphs()
        
        # Should have at least: 1 heading + 2 paragraphs + 3 list items + 1 page break
        # Modern template may have initial paragraph
        assert len(paragraphs) >= 7
        
        # Verify content is present
        doc_text = ' '.join(p.text for p in paragraphs)
        assert "Title" in doc_text
        assert "First paragraph" in doc_text
        assert "Second paragraph" in doc_text
    
    def test_save_new_file(self, temp_dir):
        """Test saving to new file."""
        output_path = temp_dir / "test_output.docx"
        
        builder = DocumentBuilder()
        builder.add_heading("Test Document")
        builder.add_paragraph("Content")
        
        saved_path = builder.save(str(output_path))
        
        assert saved_path == str(output_path)
        assert output_path.exists()
        
        # Verify file is valid DOCX
        loaded = OOXMLDocument.load(output_path)
        assert len(loaded.get_paragraphs()) >= 2
        
        # Verify content
        doc_text = ' '.join(p.text for p in loaded.get_paragraphs())
        assert "Test Document" in doc_text
        assert "Content" in doc_text
    
    def test_save_overwrite_protection(self, temp_dir):
        """Test save with overwrite protection."""
        output_path = temp_dir / "existing.docx"
        
        # Create existing file
        builder1 = DocumentBuilder()
        builder1.add_paragraph("Original")
        builder1.save(str(output_path))
        
        # Try to save again without overwrite
        builder2 = DocumentBuilder()
        builder2.add_paragraph("New")
        
        with pytest.raises(FileExistsError):
            builder2.save(str(output_path), overwrite=False)
    
    def test_save_with_overwrite(self, temp_dir):
        """Test save with overwrite allowed."""
        output_path = temp_dir / "overwrite.docx"
        
        # Create existing file
        builder1 = DocumentBuilder()
        builder1.add_paragraph("Original")
        builder1.save(str(output_path))
        
        # Overwrite with new content
        builder2 = DocumentBuilder()
        builder2.add_paragraph("New content")
        saved_path = builder2.save(str(output_path), overwrite=True)
        
        assert saved_path == str(output_path)
        
        # Verify backup was created
        backup_path = output_path.with_suffix('.docx.bak')
        assert backup_path.exists()
        
        # Verify new content
        loaded = OOXMLDocument.load(output_path)
        text = loaded.get_text()
        assert "New content" in text
    
    def test_get_document(self):
        """Test getting underlying OOXMLDocument."""
        builder = DocumentBuilder()
        doc = builder.get_document()
        
        assert isinstance(doc, OOXMLDocument)
    
    def test_repr(self):
        """Test string representation."""
        builder = DocumentBuilder()
        builder.add_paragraph("Test")
        builder.add_table([["A", "B"]])
        
        repr_str = repr(builder)
        assert "DocumentBuilder" in repr_str
        assert "paragraphs" in repr_str
        assert "tables" in repr_str
    
    def test_complex_document(self, temp_dir):
        """Test creating complex document with all features."""
        output_path = temp_dir / "complex.docx"
        
        builder = DocumentBuilder()
        
        # Build complex document
        builder.add_heading("Report Title", level=1)
        builder.add_paragraph("Introduction paragraph", bold=True)
        builder.add_paragraph("Regular text with details.")
        
        builder.add_heading("Section 1", level=2)
        builder.add_list(["Point 1", "Point 2", "Point 3"])
        
        builder.add_heading("Data Table", level=2)
        builder.add_table(
            data=[
                ["Q1", "100", "120"],
                ["Q2", "150", "180"],
            ],
            headers=["Quarter", "Actual", "Target"]
        )
        
        builder.add_page_break()
        builder.add_heading("Conclusion", level=1)
        builder.add_paragraph("Final thoughts.")
        
        # Save
        builder.save(str(output_path))
        
        # Verify
        assert output_path.exists()
        loaded = OOXMLDocument.load(output_path)
        assert loaded.get_word_count() > 0
        assert len(loaded.get_tables()) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
