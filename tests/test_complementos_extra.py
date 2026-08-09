"""Tests para InformaciónGlobal, Leyendas Fiscales, IEPS y Addenda."""

from decimal import Decimal
from pathlib import Path

from cfdi_pdf import CFDIPDF
from cfdi_pdf.parser import CFDIParser

FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestComplementosExtra:
    """Test suite para complementos extra (Leyendas, IEPS, InformaciónGlobal)."""

    def _parse(self) -> CFDIParser:
        return CFDIParser().parse_file(FIXTURES_DIR / "complementos_extra.xml")

    def test_informacion_global(self) -> None:
        cfdi = self._parse()
        assert cfdi.informacion_global is not None
        assert cfdi.informacion_global.periodicidad == "01"
        assert cfdi.informacion_global.meses == "01"
        assert cfdi.informacion_global.anio == 2024

    def test_leyendas_fiscales(self) -> None:
        cfdi = self._parse()
        assert cfdi.leyendas_fiscales is not None
        assert cfdi.leyendas_fiscales.version == "1.0"
        assert len(cfdi.leyendas_fiscales.leyenda) == 1
        leyenda = cfdi.leyendas_fiscales.leyenda[0]
        assert leyenda.disposicion_fiscal == "RMF 2024 4.5.2"
        assert "pago parcial" in leyenda.texto_leyenda

    def test_ieps(self) -> None:
        cfdi = self._parse()
        assert cfdi.ieps is not None
        assert cfdi.ieps.version == "1.0"
        assert len(cfdi.ieps.traslado) == 1
        traslado = cfdi.ieps.traslado[0]
        assert traslado.impuesto == "IEPS"
        assert traslado.base == Decimal("500.00")
        assert traslado.tasa_o_cuota == Decimal("0.08")
        assert traslado.importe == Decimal("40.00")
        assert len(cfdi.ieps.retencion) == 1
        assert cfdi.ieps.retencion[0].importe == Decimal("5.00")

    def test_addenda_flagged_and_ignored(self) -> None:
        """Addenda se detecta (has_addenda) pero su contenido se ignora."""
        cfdi = self._parse()
        assert cfdi.has_addenda is True
        # El contenido arbitrario de la Addenda no debe parsearse como complemento
        assert cfdi.complementos == {}

    def test_complementos_not_repeated_in_generic_dict(self) -> None:
        cfdi = self._parse()
        assert "LeyendasFiscales" not in cfdi.complementos
        assert "IEPS" not in cfdi.complementos

    def test_regular_cfdi_has_none(self, valid_cfdi_40_xml: str) -> None:
        cfdi = CFDIParser().parse_string(valid_cfdi_40_xml)
        assert cfdi.informacion_global is None
        assert cfdi.leyendas_fiscales is None
        assert cfdi.ieps is None
        assert cfdi.has_addenda is False

    def test_render_complementos_extra(self) -> None:
        xml = (FIXTURES_DIR / "complementos_extra.xml").read_text(encoding="utf-8")
        pdf = CFDIPDF(template="minimal")
        pdf_bytes, filename = pdf.render_bytes_from_string(xml)
        assert pdf_bytes.startswith(b"%PDF")
        assert filename.endswith(".pdf")
