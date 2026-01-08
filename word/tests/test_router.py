"""
Tests for router.py - API Recommendation Engine

Tests cover:
- recommend_api function
- Decision tree logic
- Requirement extraction
- Recommendation quality
"""

import pytest
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.router import (
    recommend_api,
    should_use_simple_api,
    should_use_advanced_api,
    should_use_ooxml_api,
    Recommendation,
    _extract_requirements,
)


class TestRecommendationDataclass:
    """Test Recommendation dataclass."""
    
    def test_create_recommendation(self):
        """Test creating Recommendation."""
        rec = Recommendation(
            api_level="simple",
            reasoning="Test reasoning",
            example_code="print('hello')",
            alternatives=["Alt 1", "Alt 2"]
        )
        
        assert rec.api_level == "simple"
        assert rec.reasoning == "Test reasoning"
        assert "hello" in rec.example_code
        assert len(rec.alternatives) == 2


class TestRequirementExtraction:
    """Test requirement extraction from descriptions."""
    
    def test_extract_simple_requirements(self):
        """Test extracting simple requirements."""
        desc = "create document with headings and paragraphs"
        req = _extract_requirements(desc)
        
        assert req["headings"] is True
        assert req["paragraphs"] is True
        assert req["custom_styles"] is False
        assert req["xml_manipulation"] is False
    
    def test_extract_list_requirements(self):
        """Test extracting list requirements."""
        desc = "add bulleted list and numbered items"
        req = _extract_requirements(desc)
        
        assert req["lists"] is True
    
    def test_extract_table_requirements(self):
        """Test extracting table requirements."""
        desc = "create table with data"
        req = _extract_requirements(desc)
        
        assert req["tables"] is True
    
    def test_extract_image_requirements(self):
        """Test extracting image requirements."""
        desc = "add image and picture to document"
        req = _extract_requirements(desc)
        
        assert req["images"] is True
    
    def test_extract_custom_style_requirements(self):
        """Test extracting custom style requirements."""
        desc = "create custom style for paragraphs"
        req = _extract_requirements(desc)
        
        assert req["custom_styles"] is True
    
    def test_extract_page_layout_requirements(self):
        """Test extracting page layout requirements."""
        desc = "set margins and change to landscape orientation"
        req = _extract_requirements(desc)
        
        assert req["custom_page_layout"] is True
    
    def test_extract_header_footer_requirements(self):
        """Test extracting header/footer requirements."""
        desc = "add header and footer to document"
        req = _extract_requirements(desc)
        
        assert req["headers_footers"] is True
    
    def test_extract_xml_requirements(self):
        """Test extracting XML manipulation requirements."""
        desc = "modify xml structure directly"
        req = _extract_requirements(desc)
        
        assert req["xml_manipulation"] is True


class TestDecisionFunctions:
    """Test decision functions."""
    
    def test_should_use_simple_api_basic(self):
        """Test Simple API recommendation for basic requirements."""
        req = {
            "headings": True,
            "paragraphs": True,
            "lists": True,
            "custom_styles": False,
            "xml_manipulation": False,
        }
        
        assert should_use_simple_api(req) is True
    
    def test_should_use_simple_api_with_custom_styles(self):
        """Test Simple API NOT recommended with custom styles."""
        req = {
            "headings": True,
            "custom_styles": True,
        }
        
        assert should_use_simple_api(req) is False
    
    def test_should_use_advanced_api_custom_styles(self):
        """Test Advanced API for custom styles."""
        req = {
            "custom_styles": True,
            "xml_manipulation": False,
        }
        
        assert should_use_advanced_api(req) is True
    
    def test_should_use_advanced_api_page_layout(self):
        """Test Advanced API for page layout."""
        req = {
            "custom_page_layout": True,
            "xml_manipulation": False,
        }
        
        assert should_use_advanced_api(req) is True
    
    def test_should_use_advanced_api_headers_footers(self):
        """Test Advanced API for headers/footers."""
        req = {
            "headers_footers": True,
            "xml_manipulation": False,
        }
        
        assert should_use_advanced_api(req) is True
    
    def test_should_not_use_advanced_with_xml(self):
        """Test Advanced API NOT recommended with XML manipulation."""
        req = {
            "custom_styles": True,
            "xml_manipulation": True,
        }
        
        # Should use OOXML instead
        assert should_use_advanced_api(req) is False
        assert should_use_ooxml_api(req) is True
    
    def test_should_use_ooxml_api(self):
        """Test OOXML API for XML manipulation."""
        req = {
            "xml_manipulation": True,
        }
        
        assert should_use_ooxml_api(req) is True


class TestRecommendApi:
    """Test recommend_api function."""
    
    def test_recommend_simple_basic(self):
        """Test recommending Simple API for basic task."""
        rec = recommend_api("Create document with heading and paragraphs")
        
        assert rec.api_level == "simple"
        assert "Simple API" in rec.reasoning
        assert "DocumentBuilder" in rec.example_code
        assert len(rec.alternatives) > 0
    
    def test_recommend_simple_with_list(self):
        """Test recommending Simple API for list."""
        rec = recommend_api("Add bulleted list to document")
        
        assert rec.api_level == "simple"
        assert "add_list" in rec.example_code.lower() or "list" in rec.example_code.lower()
    
    def test_recommend_simple_with_table(self):
        """Test recommending Simple API for table."""
        rec = recommend_api("Create table with data")
        
        assert rec.api_level == "simple"
        assert "table" in rec.example_code.lower()
    
    def test_recommend_advanced_custom_style(self):
        """Test recommending Advanced API for custom styles."""
        rec = recommend_api("Create custom paragraph style with specific font")
        
        assert rec.api_level == "advanced"
        assert "Advanced API" in rec.reasoning
        assert "AdvancedDocument" in rec.example_code
        assert "styles" in rec.example_code.lower()
    
    def test_recommend_advanced_page_layout(self):
        """Test recommending Advanced API for page layout."""
        rec = recommend_api("Set page margins and add header")
        
        assert rec.api_level == "advanced"
        assert "margins" in rec.reasoning.lower() or "header" in rec.reasoning.lower()
    
    def test_recommend_advanced_landscape(self):
        """Test recommending Advanced API for landscape."""
        rec = recommend_api("Change page to landscape orientation")
        
        assert rec.api_level == "advanced"
        assert "sections" in rec.example_code.lower() or "orientation" in rec.example_code.lower()
    
    def test_recommend_ooxml_xml_manipulation(self):
        """Test recommending OOXML API for XML manipulation."""
        rec = recommend_api("Modify XML structure of document body")
        
        assert rec.api_level == "ooxml"
        assert "OOXML API" in rec.reasoning
        assert "OOXMLDocument" in rec.example_code
        assert "xml" in rec.reasoning.lower()
    
    def test_recommend_ooxml_low_level(self):
        """Test recommending OOXML API for low-level access."""
        rec = recommend_api("Direct manipulation of ooxml elements")
        
        assert rec.api_level == "ooxml"
    
    def test_recommendation_has_example_code(self):
        """Test all recommendations include example code."""
        tasks = [
            "Create simple document",
            "Create custom style",
            "Modify XML directly",
        ]
        
        for task in tasks:
            rec = recommend_api(task)
            assert len(rec.example_code) > 0
            assert "from" in rec.example_code
            assert "import" in rec.example_code
    
    def test_recommendation_has_reasoning(self):
        """Test all recommendations include reasoning."""
        tasks = [
            "Create document with heading",
            "Set page margins",
            "Access document body element",
        ]
        
        for task in tasks:
            rec = recommend_api(task)
            assert len(rec.reasoning) > 0
            assert rec.api_level in rec.reasoning.lower() or "api" in rec.reasoning.lower()
    
    def test_recommendation_has_alternatives(self):
        """Test all recommendations include alternatives."""
        rec = recommend_api("Create document")
        
        assert isinstance(rec.alternatives, list)
        assert len(rec.alternatives) > 0
    
    def test_complex_task_routing(self):
        """Test routing complex tasks."""
        # Task with multiple features but no XML
        rec = recommend_api(
            "Create document with custom styles, landscape section, "
            "headers and footers, and formatted tables"
        )
        
        assert rec.api_level == "advanced"
        
        # Task with XML requirement overrides everything
        rec = recommend_api(
            "Create custom styles and modify XML structure directly"
        )
        
        assert rec.api_level == "ooxml"


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_description(self):
        """Test with empty description."""
        rec = recommend_api("")
        
        # Should default to simple
        assert rec.api_level == "simple"
    
    def test_ambiguous_description(self):
        """Test with ambiguous description."""
        rec = recommend_api("do something with document")
        
        # Should have valid recommendation
        assert rec.api_level in ["simple", "advanced", "ooxml"]
        assert len(rec.reasoning) > 0
    
    def test_case_insensitive(self):
        """Test case insensitivity."""
        rec1 = recommend_api("Create HEADING and PARAGRAPH")
        rec2 = recommend_api("create heading and paragraph")
        
        assert rec1.api_level == rec2.api_level


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
