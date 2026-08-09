"""Tests para el Complemento de Carta Porte 3.1."""

from decimal import Decimal
from pathlib import Path

from cfdi_pdf.parser import CFDIParser

FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestCartaPorteParser:
    """Test suite para el parser de Carta Porte 3.1."""

    def test_parse_carta_porte_basic(self) -> None:
        """Parsea los campos principales del complemento."""
        cfdi = CFDIParser().parse_file(FIXTURES_DIR / "carta_porte31.xml")

        assert cfdi.tipo_comprobante == "T"
        assert cfdi.carta_porte is not None
        assert cfdi.carta_porte.version == "3.1"
        assert cfdi.carta_porte.id_ccp == "CCP001"
        assert cfdi.carta_porte.tipo_de_transporte == "01"
        assert cfdi.carta_porte.trans_internacional == "No"
        assert cfdi.carta_porte.total_dist_recorrida == Decimal("10.0")

    def test_parse_ubicaciones(self) -> None:
        """Parsea las ubicaciones (origen/destino) con sus domicilios."""
        cfdi = CFDIParser().parse_file(FIXTURES_DIR / "carta_porte31.xml")
        assert cfdi.carta_porte is not None
        assert cfdi.carta_porte.ubicaciones is not None

        ubicaciones = cfdi.carta_porte.ubicaciones.ubicacion
        assert len(ubicaciones) == 2
        assert ubicaciones[0].tipo_estacion == "Origen"
        assert ubicaciones[0].domicilio is not None
        assert ubicaciones[0].domicilio.estado == "DIF"
        assert ubicaciones[1].tipo_estacion == "Destino"

    def test_parse_mercancias(self) -> None:
        """Parsea mercancías y autotransporte."""
        cfdi = CFDIParser().parse_file(FIXTURES_DIR / "carta_porte31.xml")
        assert cfdi.carta_porte is not None
        assert cfdi.carta_porte.mercancias is not None

        mercancias = cfdi.carta_porte.mercancias
        assert mercancias.peso_bruto_total == Decimal("100.00")
        assert mercancias.unidad_peso == "KGM"
        assert mercancias.num_total_mercancias == 1
        assert len(mercancias.mercancia) == 1
        assert mercancias.mercancia[0].clave_stcc == "01010101"
        assert mercancias.autotransporte is not None
        assert mercancias.autotransporte.num_permiso_sct == "AUT12345"

    def test_parse_figura_transporte(self) -> None:
        """Parsea las figuras de transporte."""
        cfdi = CFDIParser().parse_file(FIXTURES_DIR / "carta_porte31.xml")
        assert cfdi.carta_porte is not None
        assert cfdi.carta_porte.figura_transporte is not None

        figuras = cfdi.carta_porte.figura_transporte.figura
        assert len(figuras) == 1
        assert figuras[0].tipo_figura == "01"
        assert figuras[0].rfc_figura == "AAA010101AAA"

    def test_no_carta_porte_in_regular_cfdi(self, valid_cfdi_40_xml: str) -> None:
        """Un CFDI normal no debe traer complemento de Carta Porte."""
        cfdi = CFDIParser().parse_string(valid_cfdi_40_xml)
        assert cfdi.carta_porte is None

    def test_carta_porte_not_in_complementos_raw(self) -> None:
        """Carta Porte no debe repetirse en el dict genérico de complementos."""
        cfdi = CFDIParser().parse_file(FIXTURES_DIR / "carta_porte31.xml")
        assert "CartaPorte" not in cfdi.complementos

    def test_render_carta_porte(self) -> None:
        """El PDF de una Carta Porte debe generarse sin errores."""
        from cfdi_pdf import CFDIPDF

        xml = (FIXTURES_DIR / "carta_porte31.xml").read_text(encoding="utf-8")
        pdf = CFDIPDF(template="clasico")
        pdf_bytes, filename = pdf.render_bytes_from_string(xml)

        assert pdf_bytes.startswith(b"%PDF")
        assert filename.endswith(".pdf")
