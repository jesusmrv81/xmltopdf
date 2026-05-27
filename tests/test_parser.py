"""Tests for CFDI parser."""

from decimal import Decimal

import pytest

from cfdi_pdf.exceptions import InvalidCFDIError, XMLParseError
from cfdi_pdf.parser import CFDIParser


class TestCFDIParser:
    """Test suite for CFDIParser."""

    def test_parse_valid_cfdi_40(self, valid_cfdi_40_xml: str) -> None:
        """Test parsing valid CFDI 4.0 XML."""
        parser = CFDIParser()
        cfdi = parser.parse_string(valid_cfdi_40_xml)

        assert cfdi.version == "4.0"
        assert cfdi.serie == "A"
        assert cfdi.folio == "123"
        assert cfdi.emisor.rfc == "AAA010101AAA"
        assert cfdi.emisor.nombre == "EMPRESA EJEMPLO SA DE CV"
        assert cfdi.receptor.rfc == "XAXX010101000"
        assert len(cfdi.conceptos) == 1
        assert cfdi.conceptos[0].cantidad == 2
        assert cfdi.total == 1160.00

    def test_parse_cfdi_with_retenciones(self, cfdi_with_retenciones_xml: str) -> None:
        """Test parsing CFDI with tax withholdings."""
        parser = CFDIParser()
        cfdi = parser.parse_string(cfdi_with_retenciones_xml)

        assert cfdi.impuestos is not None
        assert cfdi.impuestos.total_impuestos_trasladados == 1600.00
        assert cfdi.impuestos.total_impuestos_retenidos == 1000.00
        assert len(cfdi.impuestos.traslados) == 1
        assert len(cfdi.impuestos.retenciones) == 1

    def test_parse_invalid_xml(self, invalid_xml: str) -> None:
        """Test parsing invalid XML raises error."""
        parser = CFDIParser()

        with pytest.raises((XMLParseError, InvalidCFDIError)):
            parser.parse_string(invalid_xml)

    def test_parse_cfdi_with_special_chars(self, cfdi_with_special_chars_xml: str) -> None:
        """Test parsing CFDI with special characters."""
        parser = CFDIParser()
        cfdi = parser.parse_string(cfdi_with_special_chars_xml)

        assert "café" in cfdi.conceptos[0].descripcion
        assert "niño" in cfdi.conceptos[0].descripcion
        assert "año" in cfdi.conceptos[0].descripcion

    def test_parse_timbre_fiscal_digital(self, valid_cfdi_40_xml: str) -> None:
        """Test parsing Timbre Fiscal Digital."""
        parser = CFDIParser()
        cfdi = parser.parse_string(valid_cfdi_40_xml)

        assert cfdi.timbre_fiscal is not None
        assert cfdi.timbre_fiscal.version == "1.1"
        assert cfdi.timbre_fiscal.uuid == "CCE4D168-1234-5678-9ABC-DEF012345678"
        assert cfdi.timbre_fiscal.rfc_prov_certif == "SPR190613I52"

    def test_parse_taxes_at_concept_level(self, valid_cfdi_40_xml: str) -> None:
        """Test parsing taxes at concept level."""
        parser = CFDIParser()
        cfdi = parser.parse_string(valid_cfdi_40_xml)

        concepto = cfdi.conceptos[0]
        assert concepto.impuestos is not None
        assert len(concepto.impuestos.traslados) == 1

        traslado = concepto.impuestos.traslados[0]
        assert traslado.impuesto == "002"
        assert traslado.tasa_o_cuota == Decimal("0.160000")
        assert traslado.importe == Decimal("160.00")
