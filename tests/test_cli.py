"""Tests para la CLI de cfdi-pdf."""

import sys
from pathlib import Path

import pytest

from cfdi_pdf import __version__
from cfdi_pdf.cli import main


def _run_main(argv: list[str], monkeypatch: pytest.MonkeyPatch) -> int:
    monkeypatch.setattr(sys, "argv", ["cfdi-pdf", *argv])
    return main()


def _write_cfdi(tmp_path: Path, valid_cfdi_40_xml: str, name: str = "factura.xml") -> Path:
    path = tmp_path / name
    path.write_text(valid_cfdi_40_xml, encoding="utf-8")
    return path


class TestCLI:
    """Test suite para la interfaz de línea de comandos."""

    def test_list_templates(
        self, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """--list-templates imprime los templates disponibles."""
        code = _run_main(["--list-templates"], monkeypatch)
        out = capsys.readouterr().out

        assert code == 0
        assert "minimal" in out
        assert "corporativo" in out
        assert "clasico" in out

    def test_version(
        self, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """--version imprime la versión del paquete."""
        with pytest.raises(SystemExit) as excinfo:
            _run_main(["--version"], monkeypatch)
        out = capsys.readouterr().out

        assert excinfo.value.code == 0
        assert __version__ in out

    def test_convert_single_file(
        self,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
        monkeypatch: pytest.MonkeyPatch,
        valid_cfdi_40_xml: str,
    ) -> None:
        """Convierte un XML y guarda {uuid}.pdf en el mismo directorio."""
        xml_path = _write_cfdi(tmp_path, valid_cfdi_40_xml)

        code = _run_main([str(xml_path)], monkeypatch)
        out = capsys.readouterr().out

        assert code == 0
        expected_pdf = tmp_path / "cce4d168-1234-5678-9abc-def012345678.pdf"
        assert expected_pdf.exists()
        assert expected_pdf.read_bytes().startswith(b"%PDF")
        assert "cce4d168-1234-5678-9abc-def012345678.pdf" in out

    def test_convert_with_output_dir(
        self,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
        monkeypatch: pytest.MonkeyPatch,
        valid_cfdi_40_xml: str,
    ) -> None:
        """--output-dir guarda el PDF en el directorio indicado."""
        xml_path = _write_cfdi(tmp_path, valid_cfdi_40_xml)
        output_dir = tmp_path / "pdfs"

        code = _run_main([str(xml_path), "--output-dir", str(output_dir)], monkeypatch)
        capsys.readouterr()

        assert code == 0
        assert (output_dir / "cce4d168-1234-5678-9abc-def012345678.pdf").exists()

    def test_convert_batch(
        self,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
        monkeypatch: pytest.MonkeyPatch,
        valid_cfdi_40_xml: str,
        cfdi_with_retenciones_xml: str,
    ) -> None:
        """Convierte varios XML y muestra el resumen."""
        f1 = _write_cfdi(tmp_path, valid_cfdi_40_xml, name="a.xml")
        f2 = _write_cfdi(tmp_path, cfdi_with_retenciones_xml, name="b.xml")

        code = _run_main([str(f1), str(f2)], monkeypatch)
        out = capsys.readouterr().out

        assert code == 0
        assert "Convertidos: 2  Fallidos: 0" in out

    def test_convert_missing_file(
        self,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Un archivo inexistente debe fallar con código de salida 1."""
        missing = tmp_path / "no_existe.xml"

        code = _run_main([str(missing)], monkeypatch)
        capsys.readouterr()

        assert code == 1

    def test_convert_invalid_xml(
        self,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
        monkeypatch: pytest.MonkeyPatch,
        invalid_xml: str,
    ) -> None:
        """Un XML inválido debe fallar con código de salida 1."""
        xml_path = _write_cfdi(tmp_path, invalid_xml)

        code = _run_main([str(xml_path)], monkeypatch)

        assert code == 1

    def test_download_resources(
        self, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """--download-resources predescarga los XSLT del SAT y sale con 0."""
        code = _run_main(["--download-resources"], monkeypatch)
        out = capsys.readouterr().out

        assert code == 0
        assert "Recursos del SAT" in out
