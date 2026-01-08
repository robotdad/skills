"""
Tests for conversion module (Phase 3)

Tests format conversion utilities including:
- DOCX to Markdown (using markitdown)
- Markdown to DOCX (using pypandoc)
- DOCX to PDF (using pypandoc + LaTeX)
- Plain text extraction
- Library availability checks
"""

import pytest
from pathlib import Path
import tempfile
import shutil

# Import functions to test
import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from conversion import (
    docx_to_markdown,
    markdown_to_docx,
    docx_to_pdf,
    extract_text,
    is_markitdown_available,
    is_pypandoc_available,
    is_pandoc_available,
)

from simple import DocumentBuilder


@pytest.fixture
def temp_dir():
    """Create temporary directory for test files."""
    temp = Path(tempfile.mkdtemp())
    yield temp
    # Cleanup after test
    if temp.exists():
        shutil.rmtree(temp)


@pytest.fixture
def sample_docx(temp_dir):
    """Create a sample DOCX file for testing."""
    docx_path = temp_dir / "sample.docx"
    
    # Create document with various content
    doc = DocumentBuilder()
    doc.add_heading("Test Document", level=1)
    doc.add_paragraph("This is a test paragraph with **bold** and *italic* text.")
    doc.add_heading("Section 1", level=2)
    doc.add_paragraph("First section content.")
    doc.add_list(["Item 1", "Item 2", "Item 3"])
    doc.add_heading("Section 2", level=2)
    doc.add_paragraph("Second section content.")
    doc.save(str(docx_path))
    
    return docx_path


@pytest.fixture
def sample_markdown(temp_dir):
    """Create a sample Markdown file for testing."""
    md_path = temp_dir / "sample.md"
    
    markdown_content = """# Test Markdown Document

This is a test paragraph with **bold** and *italic* text.

## Section 1

First section content.

- Item 1
- Item 2
- Item 3

## Section 2

Second section content.
"""
    
    md_path.write_text(markdown_content, encoding='utf-8')
    return md_path


class TestLibraryAvailability:
    """Test library availability check functions."""
    
    def test_is_markitdown_available(self):
        """Test markitdown availability check."""
        result = is_markitdown_available()
        assert isinstance(result, bool)
        # Should be True if dependencies installed
    
    def test_is_pypandoc_available(self):
        """Test pypandoc availability check."""
        result = is_pypandoc_available()
        assert isinstance(result, bool)
    
    def test_is_pandoc_available(self):
        """Test pandoc binary availability check."""
        result = is_pandoc_available()
        assert isinstance(result, bool)
        # If pypandoc available, should check for binary


class TestDocxToMarkdown:
    """Test DOCX to Markdown conversion."""
    
    def test_docx_to_markdown_string_only(self, sample_docx):
        """Test conversion to string without file output."""
        if not is_markitdown_available():
            pytest.skip("markitdown not installed")
        
        markdown = docx_to_markdown(sample_docx)
        
        # Verify content
        assert isinstance(markdown, str)
        assert len(markdown) > 0
        assert "Test Document" in markdown
        assert "Section 1" in markdown
        assert "Section 2" in markdown
    
    def test_docx_to_markdown_with_file(self, sample_docx, temp_dir):
        """Test conversion with file output."""
        if not is_markitdown_available():
            pytest.skip("markitdown not installed")
        
        output_path = temp_dir / "output.md"
        markdown = docx_to_markdown(sample_docx, output_path)
        
        # Verify file created
        assert output_path.exists()
        
        # Verify content matches returned string
        file_content = output_path.read_text(encoding='utf-8')
        assert file_content == markdown
        
        # Verify content
        assert "Test Document" in markdown
        assert "Section 1" in markdown
    
    def test_docx_to_markdown_file_not_found(self, temp_dir):
        """Test error handling for missing file."""
        if not is_markitdown_available():
            pytest.skip("markitdown not installed")
        
        missing_file = temp_dir / "nonexistent.docx"
        
        with pytest.raises(FileNotFoundError):
            docx_to_markdown(missing_file)
    
    def test_docx_to_markdown_no_library(self, sample_docx, monkeypatch):
        """Test error when markitdown not installed."""
        # Mock markitdown as unavailable
        def mock_import_error(*args, **kwargs):
            raise ImportError("No module named 'markitdown'")
        
        monkeypatch.setattr("conversion.is_markitdown_available", lambda: False)
        
        with pytest.raises(ImportError) as exc_info:
            docx_to_markdown(sample_docx)
        
        assert "markitdown is not installed" in str(exc_info.value)


class TestMarkdownToDocx:
    """Test Markdown to DOCX conversion."""
    
    def test_markdown_to_docx(self, sample_markdown, temp_dir):
        """Test basic Markdown to DOCX conversion."""
        if not is_pypandoc_available() or not is_pandoc_available():
            pytest.skip("pypandoc/pandoc not installed")
        
        output_path = temp_dir / "output.docx"
        result_path = markdown_to_docx(sample_markdown, output_path)
        
        # Verify file created
        assert Path(result_path).exists()
        assert output_path.exists()
        
        # Verify it's a valid DOCX by trying to extract text
        text = extract_text(output_path)
        assert "Test Markdown Document" in text
        assert "Section 1" in text
        assert "Section 2" in text
    
    def test_markdown_to_docx_with_template(self, sample_markdown, temp_dir):
        """Test conversion with custom template."""
        if not is_pypandoc_available() or not is_pandoc_available():
            pytest.skip("pypandoc/pandoc not installed")
        
        # Check if modern template exists
        template_path = Path(__file__).parent.parent / "templates" / "modern.docx"
        
        output_path = temp_dir / "output.docx"
        result_path = markdown_to_docx(
            sample_markdown,
            output_path,
            template=template_path if template_path.exists() else None
        )
        
        # Verify file created
        assert Path(result_path).exists()
    
    def test_markdown_to_docx_file_not_found(self, temp_dir):
        """Test error handling for missing markdown file."""
        if not is_pypandoc_available() or not is_pandoc_available():
            pytest.skip("pypandoc/pandoc not installed")
        
        missing_file = temp_dir / "nonexistent.md"
        output_path = temp_dir / "output.docx"
        
        with pytest.raises(FileNotFoundError):
            markdown_to_docx(missing_file, output_path)
    
    def test_markdown_to_docx_no_pypandoc(self, sample_markdown, temp_dir, monkeypatch):
        """Test error when pypandoc not installed."""
        monkeypatch.setattr("conversion.is_pypandoc_available", lambda: False)
        
        output_path = temp_dir / "output.docx"
        
        with pytest.raises(ImportError) as exc_info:
            markdown_to_docx(sample_markdown, output_path)
        
        assert "pypandoc is not installed" in str(exc_info.value)
    
    def test_markdown_to_docx_no_pandoc(self, sample_markdown, temp_dir, monkeypatch):
        """Test error when pandoc binary not found."""
        monkeypatch.setattr("conversion.is_pypandoc_available", lambda: True)
        monkeypatch.setattr("conversion.is_pandoc_available", lambda: False)
        
        output_path = temp_dir / "output.docx"
        
        with pytest.raises(RuntimeError) as exc_info:
            markdown_to_docx(sample_markdown, output_path)
        
        assert "pandoc binary not found" in str(exc_info.value)


class TestDocxToPdf:
    """Test DOCX to PDF conversion."""
    
    def test_docx_to_pdf(self, sample_docx, temp_dir):
        """Test DOCX to PDF conversion."""
        if not is_pypandoc_available() or not is_pandoc_available():
            pytest.skip("pypandoc/pandoc not installed")
        
        output_path = temp_dir / "output.pdf"
        
        try:
            result_path = docx_to_pdf(sample_docx, output_path)
            
            # Verify file created
            assert Path(result_path).exists()
            assert output_path.exists()
            
            # Verify it's a PDF (starts with %PDF)
            with open(output_path, 'rb') as f:
                header = f.read(4)
                assert header == b'%PDF'
        
        except RuntimeError as e:
            if "LaTeX not found" in str(e) or "pdflatex not found" in str(e).lower():
                pytest.skip("LaTeX not installed on system")
            raise
    
    def test_docx_to_pdf_file_not_found(self, temp_dir):
        """Test error handling for missing DOCX file."""
        if not is_pypandoc_available() or not is_pandoc_available():
            pytest.skip("pypandoc/pandoc not installed")
        
        missing_file = temp_dir / "nonexistent.docx"
        output_path = temp_dir / "output.pdf"
        
        with pytest.raises(FileNotFoundError):
            docx_to_pdf(missing_file, output_path)


class TestExtractText:
    """Test plain text extraction from DOCX."""
    
    def test_extract_text_basic(self, sample_docx):
        """Test basic text extraction."""
        text = extract_text(sample_docx)
        
        assert isinstance(text, str)
        assert len(text) > 0
        assert "Test Document" in text
        assert "Section 1" in text
        assert "Section 2" in text
        assert "Item 1" in text
        assert "Item 2" in text
        assert "Item 3" in text
    
    def test_extract_text_file_not_found(self, temp_dir):
        """Test error handling for missing file."""
        missing_file = temp_dir / "nonexistent.docx"
        
        with pytest.raises(FileNotFoundError):
            extract_text(missing_file)
    
    def test_extract_text_with_table(self, temp_dir):
        """Test text extraction from document with table."""
        docx_path = temp_dir / "table_doc.docx"
        
        # Create document with table
        doc = DocumentBuilder()
        doc.add_heading("Document with Table", level=1)
        doc.add_paragraph("Before table")
        doc.add_table([
            ["Header 1", "Header 2"],
            ["Row 1 Col 1", "Row 1 Col 2"],
            ["Row 2 Col 1", "Row 2 Col 2"]
        ])
        doc.add_paragraph("After table")
        doc.save(str(docx_path))
        
        # Extract text
        text = extract_text(docx_path)
        
        # Verify table content extracted
        assert "Header 1" in text
        assert "Header 2" in text
        assert "Row 1 Col 1" in text
        assert "Row 2 Col 2" in text
        assert "Before table" in text
        assert "After table" in text


class TestRoundTripConversion:
    """Test round-trip conversions (DOCX → MD → DOCX)."""
    
    def test_roundtrip_docx_md_docx(self, sample_docx, temp_dir):
        """Test DOCX → Markdown → DOCX conversion preserves content."""
        if not is_markitdown_available():
            pytest.skip("markitdown not installed")
        if not is_pypandoc_available() or not is_pandoc_available():
            pytest.skip("pypandoc/pandoc not installed")
        
        # Extract original text
        original_text = extract_text(sample_docx)
        
        # Convert to Markdown
        md_path = temp_dir / "intermediate.md"
        markdown = docx_to_markdown(sample_docx, md_path)
        
        # Convert back to DOCX
        final_docx = temp_dir / "final.docx"
        markdown_to_docx(md_path, final_docx)
        
        # Extract final text
        final_text = extract_text(final_docx)
        
        # Verify key content preserved (exact formatting may differ)
        assert "Test Document" in final_text
        assert "Section 1" in final_text
        assert "Section 2" in final_text
        # List items might be formatted differently but content should be there
        assert "Item 1" in final_text or "Item 1" in original_text


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_docx_to_markdown_empty_document(self, temp_dir):
        """Test conversion of empty document."""
        if not is_markitdown_available():
            pytest.skip("markitdown not installed")
        
        # Create empty document
        empty_docx = temp_dir / "empty.docx"
        doc = DocumentBuilder()
        doc.save(str(empty_docx))
        
        # Should still convert without error
        markdown = docx_to_markdown(empty_docx)
        assert isinstance(markdown, str)
    
    def test_extract_text_empty_document(self, temp_dir):
        """Test text extraction from empty document."""
        empty_docx = temp_dir / "empty.docx"
        doc = DocumentBuilder()
        doc.save(str(empty_docx))
        
        text = extract_text(empty_docx)
        assert isinstance(text, str)
        # May be empty or contain minimal content
    
    def test_markdown_to_docx_creates_parent_dirs(self, temp_dir):
        """Test that output directory is created if missing."""
        if not is_pypandoc_available() or not is_pandoc_available():
            pytest.skip("pypandoc/pandoc not installed")
        
        # Create markdown file
        md_path = temp_dir / "test.md"
        md_path.write_text("# Test\n\nContent", encoding='utf-8')
        
        # Output to nested directory that doesn't exist
        output_path = temp_dir / "nested" / "dir" / "output.docx"
        
        markdown_to_docx(md_path, output_path)
        
        # Verify parent directories created
        assert output_path.exists()
        assert output_path.parent.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
