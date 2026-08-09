"""Tests para la generación de cadenas originales con los XSLT oficiales."""

from pathlib import Path

from cfdi_pdf.parser import CFDIParser
from cfdi_pdf.sat.cadena_original import cadena_original_comprobante

FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestCadenaOriginal:
    """Test suite para la cadena original del comprobante y del TFD."""

    def test_cadena_comprobante_40(self, valid_cfdi_40_xml: str) -> None:
        """La cadena del comprobante 4.0 sigue el formato oficial."""
        cadena = cadena_original_comprobante(valid_cfdi_40_xml)

        assert cadena.startswith("||4.0|")
        assert cadena.endswith("||")
        assert "|AAA010101AAA|EMPRESA EJEMPLO SA DE CV|601|" in cadena
        assert "|XAXX010101000|" in cadena
        assert "002|Tasa|0.160000|160.00" in cadena

    def test_cadena_no_incluye_certificado(self, valid_cfdi_40_xml: str) -> None:
        """El atributo Certificado NO forma parte de la cadena original 4.0."""
        cadena = cadena_original_comprobante(valid_cfdi_40_xml)
        assert "MIIE" not in cadena

    def test_cadena_tfd(self, valid_cfdi_40_xml: str) -> None:
        """La cadena del timbre usa la XSLT oficial (sin SelloSAT)."""
        cfdi = CFDIParser().parse_string(valid_cfdi_40_xml)
        cadena = cfdi.timbre_fiscal.cadena_origen

        assert cadena is not None
        assert cadena.startswith("||1.1|")
        assert cadena.endswith("||")
        assert "CCE4D168-1234-5678-9ABC-DEF012345678" in cadena
        assert "SPR190613I52" in cadena
        assert "xyz789abc456" not in cadena  # SelloSAT excluido

    def test_parse_populates_cadena_comprobante(self, valid_cfdi_40_xml: str) -> None:
        """El parser calcula y guarda la cadena original del comprobante."""
        cfdi = CFDIParser().parse_string(valid_cfdi_40_xml)
        assert cfdi.cadena_original is not None
        assert cfdi.cadena_original.startswith("||4.0|")

    def test_cadena_pagos_incluye_complemento(self) -> None:
        """La cadena de un CFDI tipo P incluye el complemento de Pagos."""
        cfdi = CFDIParser().parse_file(FIXTURES_DIR / "pagos20_multiple.xml")
        cadena = cfdi.cadena_original

        assert cadena is not None
        assert "1600986.46" in cadena  # MontoTotalPagos
        assert "|2.0|" in cadena  # Version del complemento Pagos

    def test_cadena_nomina(self) -> None:
        """La cadena de un CFDI tipo N incluye el complemento de Nómina."""
        cfdi = CFDIParser().parse_file(FIXTURES_DIR / "nomina12.xml")
        cadena = cfdi.cadena_original

        assert cadena is not None
        assert "JUAN PEREZ" in cadena
        assert "P001" in cadena  # clave de percepción
