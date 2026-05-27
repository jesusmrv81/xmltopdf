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

    def test_render_from_string_returns_path(self, valid_cfdi_40_xml: str) -> None:
        """render_from_string debe retornar la ruta al PDF generado."""
        pdf = CFDIPDF()
        with tempfile.TemporaryDirectory() as tmpdir:
            result = pdf.render_from_string(valid_cfdi_40_xml, output_dir=tmpdir)

            assert isinstance(result, Path)
            assert result.exists()
            assert result.suffix == ".pdf"
            # El nombre del archivo debe ser el UUID (lowercase)
            assert len(result.stem) == 36, "El nombre debe ser un UUID de 36 caracteres"

    def test_render_from_string_pdf_content(self, valid_cfdi_40_xml: str) -> None:
        """El PDF generado desde string debe tener contenido válido."""
        pdf = CFDIPDF()
        with tempfile.TemporaryDirectory() as tmpdir:
            result = pdf.render_from_string(valid_cfdi_40_xml, output_dir=tmpdir)
            content = result.read_bytes()
            assert content.startswith(b"%PDF")
            assert len(content) > 0

    def test_render_to_file_named_by_uuid(self, valid_cfdi_40_xml: str) -> None:
        """render() debe guardar el PDF con nombre {uuid}.pdf en output_dir."""
        pdf = CFDIPDF()

        with tempfile.TemporaryDirectory() as tmpdir:
            xml_path = Path(tmpdir) / "test.xml"
            xml_path.write_text(valid_cfdi_40_xml)

            result = pdf.render(xml_path=xml_path, output_dir=tmpdir)

            assert isinstance(result, Path)
            assert result.exists()
            assert result.suffix == ".pdf"
            assert result.stat().st_size > 0
            # Nombre de archivo = UUID
            assert len(result.stem) == 36

    def test_render_default_output_dir_is_xml_dir(self, valid_cfdi_40_xml: str) -> None:
        """Sin output_dir, el PDF se guarda en el mismo directorio del XML."""
        pdf = CFDIPDF()

        with tempfile.TemporaryDirectory() as tmpdir:
            xml_path = Path(tmpdir) / "test.xml"
            xml_path.write_text(valid_cfdi_40_xml)

            result = pdf.render(xml_path=xml_path)

            assert result.parent == xml_path.parent

    def test_render_bytes_returns_bytes_and_filename(self, valid_cfdi_40_xml: str) -> None:
        """render_bytes debe retornar (bytes, filename)."""
        pdf = CFDIPDF()

        with tempfile.TemporaryDirectory() as tmpdir:
            xml_path = Path(tmpdir) / "test.xml"
            xml_path.write_text(valid_cfdi_40_xml)

            pdf_bytes, filename = pdf.render_bytes(xml_path=xml_path)

            assert isinstance(pdf_bytes, bytes)
            assert pdf_bytes.startswith(b"%PDF")
            assert filename.endswith(".pdf")
            assert len(filename) == 40  # 36 uuid + 4 ".pdf"

    def test_render_invalid_xml_raises_error(self, invalid_xml: str) -> None:
        """Test that invalid XML raises error."""
        pdf = CFDIPDF()

        with pytest.raises((XMLParseError, CFDIPDFError)), tempfile.TemporaryDirectory() as tmpdir:
            pdf.render_from_string(invalid_xml, output_dir=tmpdir)

    def test_render_with_cfdi_with_retenciones(self, cfdi_with_retenciones_xml: str) -> None:
        """Test rendering CFDI with retenciones."""
        pdf = CFDIPDF()
        with tempfile.TemporaryDirectory() as tmpdir:
            result = pdf.render_from_string(cfdi_with_retenciones_xml, output_dir=tmpdir)
            content = result.read_bytes()
            assert content.startswith(b"%PDF")

    def test_render_with_special_chars(self, cfdi_with_special_chars_xml: str) -> None:
        """Test rendering CFDI with special characters."""
        pdf = CFDIPDF()
        with tempfile.TemporaryDirectory() as tmpdir:
            result = pdf.render_from_string(cfdi_with_special_chars_xml, output_dir=tmpdir)
            content = result.read_bytes()
            assert content.startswith(b"%PDF")
