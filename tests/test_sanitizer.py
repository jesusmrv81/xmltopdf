"""Tests for sanitizer."""

from cfdi_pdf.parser import XMLSanitizer


class TestXMLSanitizer:
    """Test suite for XMLSanitizer."""

    def test_sanitize_valid_text(self) -> None:
        """Test sanitizing valid text."""
        text = "Hello World"
        assert XMLSanitizer.sanitize_text(text) == "Hello World"

    def test_sanitize_text_with_accents(self) -> None:
        """Test sanitizing text with accents."""
        text = "café niño año"
        assert XMLSanitizer.sanitize_text(text) == "café niño año"

    def test_sanitize_text_with_special_chars(self) -> None:
        """Test sanitizing text with special characters."""
        text = "Test & < > \" '"
        result = XMLSanitizer.sanitize_text(text)
        assert "&" in result
        assert "<" in result

    def test_escape_xml(self) -> None:
        """Test XML escaping."""
        text = "Test & < > \" '"
        result = XMLSanitizer.escape_xml(text)
        assert "&amp;" in result
        assert "&lt;" in result
        assert "&gt;" in result
        assert "&quot;" in result
        assert "&apos;" in result

    def test_unescape_xml(self) -> None:
        """Test XML unescaping."""
        text = "Test &amp; &lt; &gt; &quot; &apos;"
        result = XMLSanitizer.unescape_xml(text)
        assert "&" in result
        assert "<" in result
        assert ">" in result

    def test_sanitize_empty_string(self) -> None:
        """Test sanitizing empty string."""
        assert XMLSanitizer.sanitize_text("") == ""

    def test_sanitize_none(self) -> None:
        """Test sanitizing None."""
        assert XMLSanitizer.sanitize_text(None) is None  # type: ignore

    def test_sanitize_dict(self) -> None:
        """Test sanitizing dictionary."""
        data = {
            "name": "Test & Company",
            "description": "Café & Niño",
            "nested": {"value": "Test <value>"},
        }
        result = XMLSanitizer.sanitize_dict(data)
        assert result["name"] == "Test & Company"
        assert result["description"] == "Café & Niño"
