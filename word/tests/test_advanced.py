"""
Tests for advanced.py - Advanced Document API

Tests cover:
- AdvancedDocument creation
- StyleManager (custom styles)
- SectionManager (page layout, headers/footers)
- TableBuilder (advanced tables)
- ImageManager (advanced image handling)
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from PIL import Image
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from advanced import (
    AdvancedDocument,
    StyleManager,
    SectionManager,
    TableBuilder,
    ImageManager,
)
from ooxml import OOXMLDocument


class TestAdvancedDocument:
    """Test AdvancedDocument class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files."""
        temp = Path(tempfile.mkdtemp(prefix="test_advanced_"))
        yield temp
        shutil.rmtree(temp, ignore_errors=True)
    
    @pytest.fixture
    def test_image(self, temp_dir):
        """Create a test image file."""
        image_path = temp_dir / "test_image.png"
        img = Image.new('RGB', (100, 100), color='blue')
        img.save(image_path)
        return image_path
    
    def test_create_document(self):
        """Test creating AdvancedDocument."""
        doc = AdvancedDocument()
        assert doc is not None
    
    def test_create_with_legacy_template(self):
        """Test creating with legacy template."""
        doc = AdvancedDocument(template="legacy")
        assert doc is not None
    
    def test_managers_accessible(self):
        """Test that all managers are accessible."""
        doc = AdvancedDocument()
        
        assert isinstance(doc.styles, StyleManager)
        assert isinstance(doc.sections, SectionManager)
        assert isinstance(doc.tables, TableBuilder)
        assert isinstance(doc.images, ImageManager)
    
    def test_add_paragraph(self):
        """Test adding paragraph."""
        doc = AdvancedDocument()
        para = doc.add_paragraph("Test text")
        
        assert para is not None
        assert para.text == "Test text"
    
    def test_add_paragraph_with_style(self):
        """Test adding paragraph with style."""
        doc = AdvancedDocument()
        para = doc.add_paragraph("Heading text", style="Heading 1")
        
        assert para.style.name == "Heading 1"
    
    def test_add_heading(self):
        """Test adding heading."""
        doc = AdvancedDocument()
        heading = doc.add_heading("Title", level=1)
        
        assert heading is not None
        assert "Title" in heading.text
    
    def test_add_page_break(self):
        """Test adding page break."""
        doc = AdvancedDocument()
        result = doc.add_page_break()
        
        assert result is not None
    
    def test_save(self, temp_dir):
        """Test saving document."""
        output_path = temp_dir / "advanced_test.docx"
        
        doc = AdvancedDocument()
        doc.add_heading("Test")
        doc.add_paragraph("Content")
        
        saved_path = doc.save(str(output_path))
        
        assert saved_path == str(output_path)
        assert output_path.exists()
    
    def test_save_overwrite_protection(self, temp_dir):
        """Test save with overwrite protection."""
        output_path = temp_dir / "exists.docx"
        
        # Create first file
        doc1 = AdvancedDocument()
        doc1.add_paragraph("Original")
        doc1.save(str(output_path))
        
        # Try to overwrite
        doc2 = AdvancedDocument()
        doc2.add_paragraph("New")
        
        with pytest.raises(FileExistsError):
            doc2.save(str(output_path), overwrite=False)
    
    def test_get_ooxml_document(self):
        """Test getting underlying OOXMLDocument."""
        doc = AdvancedDocument()
        ooxml = doc.get_ooxml_document()
        
        assert isinstance(ooxml, OOXMLDocument)
    
    def test_repr(self):
        """Test string representation."""
        doc = AdvancedDocument()
        doc.add_paragraph("Test")
        
        repr_str = repr(doc)
        assert "AdvancedDocument" in repr_str


class TestStyleManager:
    """Test StyleManager class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        temp = Path(tempfile.mkdtemp(prefix="test_styles_"))
        yield temp
        shutil.rmtree(temp, ignore_errors=True)
    
    def test_add_paragraph_style(self):
        """Test creating custom paragraph style."""
        doc = AdvancedDocument()
        
        style = doc.styles.add_paragraph_style(
            name="CustomStyle",
            font_name="Arial",
            font_size=14,
            bold=True,
            italic=True,
            color=(255, 0, 0)
        )
        
        assert style is not None
        assert style.name == "CustomStyle"
        assert style.font.name == "Arial"
        assert style.font.size.pt == 14
        assert style.font.bold is True
        assert style.font.italic is True
    
    def test_add_character_style(self):
        """Test creating character style."""
        doc = AdvancedDocument()
        
        style = doc.styles.add_character_style(
            name="HighlightStyle",
            font_size=12,
            color=(0, 0, 255)
        )
        
        assert style is not None
        assert style.name == "HighlightStyle"
    
    def test_list_styles(self):
        """Test listing all styles."""
        doc = AdvancedDocument()
        styles = doc.styles.list_styles()
        
        assert isinstance(styles, list)
        assert len(styles) > 0
        # Should include default styles
        assert "Normal" in styles
    
    def test_get_style(self):
        """Test getting style by name."""
        doc = AdvancedDocument()
        
        # Get built-in style
        normal_style = doc.styles.get_style("Normal")
        assert normal_style is not None
        
        # Try to get non-existent style
        missing = doc.styles.get_style("NonExistentStyle")
        assert missing is None
    
    def test_use_custom_style(self, temp_dir):
        """Test using custom style in document."""
        output_path = temp_dir / "custom_style.docx"
        
        doc = AdvancedDocument()
        
        # Create custom style
        style = doc.styles.add_paragraph_style(
            name="Emphasis",
            font_size=16,
            bold=True
        )
        
        # Verify style was created
        assert style is not None
        assert style.name == "Emphasis"
        
        # Use the style
        para = doc.add_paragraph("Emphasized text", style="Emphasis")
        
        # Verify the paragraph was created with content
        assert "Emphasized text" in para.text
        
        # Save document
        doc.save(str(output_path))
        
        # Verify file was created
        assert output_path.exists()
        
        # Load and verify content is preserved
        loaded = OOXMLDocument.load(output_path)
        paras = [p for p in loaded.get_paragraphs() if p.text.strip()]
        assert any("Emphasized text" in p.text for p in paras)


class TestSectionManager:
    """Test SectionManager class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        temp = Path(tempfile.mkdtemp(prefix="test_sections_"))
        yield temp
        shutil.rmtree(temp, ignore_errors=True)
    
    def test_set_margins(self):
        """Test setting page margins."""
        doc = AdvancedDocument()
        doc.sections.set_margins(top=1.0, bottom=1.0, left=1.5, right=1.5)
        
        ooxml = doc.get_ooxml_document()
        section = ooxml.get_sections()[0]
        
        # Check margins (convert from EMU to inches)
        assert abs(section.top_margin.inches - 1.0) < 0.01
        assert abs(section.bottom_margin.inches - 1.0) < 0.01
        assert abs(section.left_margin.inches - 1.5) < 0.01
        assert abs(section.right_margin.inches - 1.5) < 0.01
    
    def test_add_section_portrait(self):
        """Test adding portrait section."""
        doc = AdvancedDocument()
        doc.add_paragraph("Page 1")
        
        section = doc.sections.add_section(orientation="portrait")
        
        assert section is not None
        doc.add_paragraph("Page 2")
        
        ooxml = doc.get_ooxml_document()
        sections = ooxml.get_sections()
        assert len(sections) == 2
    
    def test_add_section_landscape(self):
        """Test adding landscape section."""
        doc = AdvancedDocument()
        doc.add_paragraph("Portrait page")
        
        section = doc.sections.add_section(orientation="landscape")
        
        assert section is not None
        doc.add_paragraph("Landscape page")
        
        # In landscape, width > height
        assert section.page_width > section.page_height
    
    def test_add_header(self):
        """Test adding header."""
        doc = AdvancedDocument()
        doc.sections.add_header("Document Header")
        
        ooxml = doc.get_ooxml_document()
        section = ooxml.get_sections()[0]
        header_text = section.header.paragraphs[0].text
        
        assert "Document Header" in header_text
    
    def test_add_footer(self):
        """Test adding footer."""
        doc = AdvancedDocument()
        doc.sections.add_footer("Page Footer")
        
        ooxml = doc.get_ooxml_document()
        section = ooxml.get_sections()[0]
        footer_text = section.footer.paragraphs[0].text
        
        assert "Page Footer" in footer_text


class TestTableBuilder:
    """Test TableBuilder class."""
    
    def test_create_table(self):
        """Test creating empty table."""
        doc = AdvancedDocument()
        table = doc.tables.create_table(rows=3, cols=4)
        
        assert table is not None
        assert len(table.rows) == 3
        assert len(table.columns) == 4
    
    def test_add_table_from_data(self):
        """Test creating table from data."""
        doc = AdvancedDocument()
        
        data = [
            ["A", "B", "C"],
            ["D", "E", "F"],
        ]
        
        table = doc.tables.add_table_from_data(data)
        
        assert table is not None
        assert len(table.rows) == 2
        assert len(table.columns) == 3
        assert table.rows[0].cells[0].text == "A"
    
    def test_add_table_with_headers(self):
        """Test creating table with headers."""
        doc = AdvancedDocument()
        
        data = [["1", "2"], ["3", "4"]]
        headers = ["Col1", "Col2"]
        
        table = doc.tables.add_table_from_data(data, headers=headers)
        
        # Should have 3 rows (1 header + 2 data)
        assert len(table.rows) == 3
        assert table.rows[0].cells[0].text == "Col1"
        assert table.rows[1].cells[0].text == "1"
    
    def test_add_table_with_style(self):
        """Test creating table with style."""
        doc = AdvancedDocument()
        
        data = [["A", "B"]]
        table = doc.tables.add_table_from_data(
            data,
            style="Light Grid Accent 1"
        )
        
        # Table created successfully (style may or may not apply depending on template)
        assert table is not None
        assert len(table.rows) == 1
        assert table.rows[0].cells[0].text == "A"
    
    def test_list_table_styles(self):
        """Test listing table styles."""
        doc = AdvancedDocument()
        styles = doc.tables.list_table_styles()
        
        assert isinstance(styles, list)
        # Should have some table styles
        assert len(styles) > 0


class TestImageManager:
    """Test ImageManager class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        temp = Path(tempfile.mkdtemp(prefix="test_images_"))
        yield temp
        shutil.rmtree(temp, ignore_errors=True)
    
    @pytest.fixture
    def test_image(self, temp_dir):
        """Create test image."""
        image_path = temp_dir / "test.png"
        img = Image.new('RGB', (200, 150), color='green')
        img.save(image_path)
        return image_path
    
    def test_add_image_original_size(self, test_image):
        """Test adding image at original size."""
        doc = AdvancedDocument()
        result = doc.images.add_image(str(test_image))
        
        assert result is not None
    
    def test_add_image_with_width(self, test_image):
        """Test adding image with specific width."""
        doc = AdvancedDocument()
        result = doc.images.add_image(
            str(test_image),
            width_inches=4.0
        )
        
        assert result is not None
        # Width should be set to 4 inches
        assert abs(result.width.inches - 4.0) < 0.01
    
    def test_add_image_with_width_and_height(self, test_image):
        """Test adding image with width and height."""
        doc = AdvancedDocument()
        result = doc.images.add_image(
            str(test_image),
            width_inches=5.0,
            height_inches=3.0
        )
        
        assert result is not None
        assert abs(result.width.inches - 5.0) < 0.01
        assert abs(result.height.inches - 3.0) < 0.01
    
    def test_add_image_not_found(self):
        """Test adding non-existent image."""
        doc = AdvancedDocument()
        
        with pytest.raises(FileNotFoundError):
            doc.images.add_image("nonexistent.jpg")


class TestAdvancedIntegration:
    """Integration tests for advanced features."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        temp = Path(tempfile.mkdtemp(prefix="test_integration_"))
        yield temp
        shutil.rmtree(temp, ignore_errors=True)
    
    def test_complex_document(self, temp_dir):
        """Test creating complex document with all features."""
        output_path = temp_dir / "complex_advanced.docx"
        
        doc = AdvancedDocument()
        
        # Custom style
        doc.styles.add_paragraph_style(
            "Highlight",
            font_size=14,
            bold=True,
            color=(255, 0, 0)
        )
        
        # Page setup
        doc.sections.set_margins(1.0, 1.0, 1.5, 1.5)
        doc.sections.add_header("Confidential Report")
        doc.sections.add_footer("© 2024 Company")
        
        # Content
        doc.add_heading("Executive Summary", level=1)
        doc.add_paragraph("Important finding", style="Highlight")
        doc.add_paragraph("Regular text")
        
        # Table
        table = doc.tables.add_table_from_data(
            data=[
                ["Q1", "100", "150"],
                ["Q2", "120", "180"],
            ],
            headers=["Quarter", "Actual", "Target"],
            style="Medium Grid 1 Accent 1"
        )
        
        # New landscape section
        doc.sections.add_section(orientation="landscape")
        doc.add_heading("Wide Data", level=1)
        
        # Save
        doc.save(str(output_path))
        
        # Verify
        assert output_path.exists()
        loaded = OOXMLDocument.load(output_path)
        assert len(loaded.get_paragraphs()) > 0
        assert len(loaded.get_tables()) == 1
        assert len(loaded.get_sections()) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
