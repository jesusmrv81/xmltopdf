"""Tests for main API."""

import tempfile
from pathlib import Path

import pytest

from cfdi_pdf import CFDIPDF
from cfdi_pdf.exceptions import CFDIPDFError, XMLParseError


class TestCFDIPDF:
    """Test suite for CFDIPDF main API."""

    def test_initialization(self) -> None:
        """Test CFDIPDF initialization."""
        pdf = CFDIPDF()
        assert pdf.get_template() == "minimal"

    def test_initialization_with_custom_template(self) -> None:
        """Test CFDIPDF initialization with custom template."""
        pdf = CFDIPDF(template="minimal")
        assert pdf.get_template() == "minimal"

    def test_list_templates(self) -> None:
        """Test listing available templates."""
        pdf = CFDIPDF()
        templates = pdf.list_templates()
        assert "minimal" in templates

    def test_set_template(self) -> None:
        """Test setting template."""
        pdf = CFDIPDF()
        pdf.set_template("minimal")
        assert pdf.get_template() == "minimal"

    def test_render_from_string(self, valid_cfdi_40_xml: str) -> None:
        """Test rendering from XML string."""
        pdf = CFDIPDF()
        result = pdf.render_from_string(valid_cfdi_40_xml)

        assert isinstance(result, bytes)
        assert len(result) > 0
        # PDF magic number
        assert result.startswith(b"%PDF")

    def test_render_to_file(self, valid_cfdi_40_xml: str) -> None:
        """Test rendering to file."""
        pdf = CFDIPDF()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Write XML to file
            xml_path = Path(tmpdir) / "test.xml"
            xml_path.write_text(valid_cfdi_40_xml)

            # Render to PDF
            pdf_path = Path(tmpdir) / "test.pdf"
            result = pdf.render(xml_path=xml_path, output=pdf_path)

            assert result is None
            assert pdf_path.exists()
            assert pdf_path.stat().st_size > 0

    def test_render_invalid_xml_raises_error(self, invalid_xml: str) -> None:
        """Test that invalid XML raises error."""
        pdf = CFDIPDF()

        with pytest.raises((XMLParseError, CFDIPDFError)):
            pdf.render_from_string(invalid_xml)

    def test_render_with_cfdi_with_retenciones(self, cfdi_with_retenciones_xml: str) -> None:
        """Test rendering CFDI with retenciones."""
        pdf = CFDIPDF()
        result = pdf.render_from_string(cfdi_with_retenciones_xml)

        assert isinstance(result, bytes)
        assert len(result) > 0
        assert result.startswith(b"%PDF")

    def test_render_with_special_chars(self, cfdi_with_special_chars_xml: str) -> None:
        """Test rendering CFDI with special characters."""
        pdf = CFDIPDF()
        result = pdf.render_from_string(cfdi_with_special_chars_xml)

        assert isinstance(result, bytes)
        assert len(result) > 0
        assert result.startswith(b"%PDF")
