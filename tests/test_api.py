"""Tests for main API."""

import importlib.metadata
import tempfile
from pathlib import Path

import pytest

import cfdi_pdf
from cfdi_pdf import CFDIPDF
from cfdi_pdf.exceptions import CFDIPDFError, XMLParseError


class TestCFDIPDF:
    """Test suite for CFDIPDF main API."""

    def test_version_consistency(self) -> None:
        """__version__ debe coincidir con la metadata del paquete instalado."""
        try:
            installed = importlib.metadata.version("cfdi-pdf")
        except importlib.metadata.PackageNotFoundError:
            pytest.skip("cfdi-pdf no está instalado en este entorno")

        assert cfdi_pdf.__version__ == installed

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

    def test_render_bytes_from_string_returns_bytes(self, valid_cfdi_40_xml: str) -> None:
        """render_bytes_from_string debe retornar (bytes, filename) sin tocar disco."""
        pdf = CFDIPDF()

        pdf_bytes, filename = pdf.render_bytes_from_string(valid_cfdi_40_xml)

        assert isinstance(pdf_bytes, bytes)
        assert pdf_bytes.startswith(b"%PDF")
        assert filename == "cce4d168-1234-5678-9abc-def012345678.pdf"

    def test_render_batch_sequential(self, tmp_path: Path, valid_cfdi_40_xml: str) -> None:
        """render_batch secuencial reutiliza la instancia y devuelve resultados."""
        a = Path(tmp_path) / "a.xml"
        b = Path(tmp_path) / "b.xml"
        a.write_text(valid_cfdi_40_xml)
        b.write_text(valid_cfdi_40_xml)
        out = tmp_path / "pdfs"

        pdf = CFDIPDF()
        results = pdf.render_batch([a, b], output_dir=out)

        assert len(results) == 2
        assert all(r.error is None for r in results)
        assert all(r.output is not None and r.output.exists() for r in results)
        assert out / "cce4d168-1234-5678-9abc-def012345678.pdf" in [r.output for r in results]

    def test_render_batch_reports_errors(self, tmp_path: Path, valid_cfdi_40_xml: str) -> None:
        """Un archivo inválido no aborta el lote; se reporta su error."""
        good = Path(tmp_path) / "good.xml"
        bad = Path(tmp_path) / "bad.xml"
        good.write_text(valid_cfdi_40_xml)
        bad.write_text("xml roto")

        pdf = CFDIPDF()
        results = pdf.render_batch([good, bad], output_dir=tmp_path)

        assert len(results) == 2
        ok = {r.source.name: r for r in results}
        assert ok["good.xml"].error is None
        assert ok["bad.xml"].output is None
        assert ok["bad.xml"].error is not None

    def test_render_batch_parallel(self, tmp_path: Path, valid_cfdi_40_xml: str) -> None:
        """render_batch en paralelo procesa todos los archivos."""
        paths = []
        for i in range(2):
            p = tmp_path / f"f{i}.xml"
            p.write_text(valid_cfdi_40_xml)
            paths.append(p)

        pdf = CFDIPDF()
        results = pdf.render_batch(paths, output_dir=tmp_path, workers=2)

        assert len(results) == 2
        assert all(r.error is None for r in results)
        assert all(r.output is not None for r in results)

    def test_on_render_hook_called(self, tmp_path: Path, valid_cfdi_40_xml: str) -> None:
        """El hook on_render recibe (cfdi, output) tras renderizar."""
        events: list[tuple[str, str]] = []

        def hook(cfdi: object, output: str) -> None:
            events.append((cfdi.timbre_fiscal.uuid, output))  # type: ignore[attr-defined]

        pdf = CFDIPDF(on_render=hook)
        pdf.render_from_string(valid_cfdi_40_xml, output_dir=tmp_path)

        assert len(events) == 1
        assert events[0][0] == "CCE4D168-1234-5678-9ABC-DEF012345678"
        assert events[0][1].endswith(".pdf")

    def test_on_render_hook_with_bytes(self, valid_cfdi_40_xml: str) -> None:
        """El hook con render_bytes_from_string recibe el nombre de archivo."""
        events: list[str] = []

        def hook(cfdi: object, output: str) -> None:
            events.append(output)

        pdf = CFDIPDF(on_render=hook)
        pdf.render_bytes_from_string(valid_cfdi_40_xml)

        assert events == ["cce4d168-1234-5678-9abc-def012345678.pdf"]

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
