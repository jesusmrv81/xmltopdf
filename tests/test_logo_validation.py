"""Tests para la validación de logos (extensión, magic bytes y tamaño)."""

import base64
from pathlib import Path

from cfdi_pdf import CFDIPDF
from cfdi_pdf.render.engine import _MAX_LOGO_SIZE, _valid_logo

# PNG transparente 1x1 válido
PNG_1X1 = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
)
VALID_SVG = b'<?xml version="1.0"?>\n<svg xmlns="http://www.w3.org/2000/svg" width="1" height="1"/>'


class TestValidLogo:
    """Test suite para _valid_logo."""

    def test_valid_png(self, tmp_path: Path) -> None:
        path = tmp_path / "logo.png"
        ok, reason = _valid_logo(path, PNG_1X1)
        assert ok, reason

    def test_valid_svg(self, tmp_path: Path) -> None:
        path = tmp_path / "logo.svg"
        ok, reason = _valid_logo(path, VALID_SVG)
        assert ok, reason

    def test_rejects_unknown_extension(self, tmp_path: Path) -> None:
        path = tmp_path / "logo.gif"
        ok, reason = _valid_logo(path, b"GIF89a")
        assert not ok
        assert "extensión" in reason

    def test_rejects_magic_mismatch(self, tmp_path: Path) -> None:
        # Un archivo de texto renombrado a .png no pasa la firma
        path = tmp_path / "fake.png"
        ok, reason = _valid_logo(path, b"esto no es un png")
        assert not ok
        assert "firma" in reason

    def test_rejects_oversized(self, tmp_path: Path) -> None:
        path = tmp_path / "grande.png"
        ok, reason = _valid_logo(path, PNG_1X1 * (_MAX_LOGO_SIZE // len(PNG_1X1) + 1))
        assert not ok
        assert "tamaño" in reason

    def test_rejects_invalid_svg(self, tmp_path: Path) -> None:
        path = tmp_path / "logo.svg"
        ok, reason = _valid_logo(path, b"no es xml")
        assert not ok
        assert "SVG" in reason


class TestLogoInRender:
    """El render no debe fallar con un logo inválido (se ignora)."""

    def test_render_ignores_invalid_logo(self, tmp_path: Path, valid_cfdi_40_xml: str) -> None:
        fake = tmp_path / "fake.png"
        fake.write_bytes(b"contenido que no es png")

        pdf = CFDIPDF()
        pdf_bytes, _ = pdf.render_bytes_from_string(valid_cfdi_40_xml, logo_path=str(fake))
        assert pdf_bytes.startswith(b"%PDF")

    def test_render_with_valid_logo(self, tmp_path: Path, valid_cfdi_40_xml: str) -> None:
        logo = tmp_path / "logo.png"
        logo.write_bytes(PNG_1X1)

        pdf = CFDIPDF()
        pdf_bytes, _ = pdf.render_bytes_from_string(valid_cfdi_40_xml, logo_path=str(logo))
        assert pdf_bytes.startswith(b"%PDF")
