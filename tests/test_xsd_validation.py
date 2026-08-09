"""Tests para la validación XSD contra el esquema oficial del SAT."""

from pathlib import Path

import pytest

from cfdi_pdf.exceptions import InvalidCFDIError
from cfdi_pdf.parser import CFDIParser
from cfdi_pdf.parser.xsd_validator import CFDIXSDValidator

FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestCFDIXSDValidator:
    """Test suite para CFDIXSDValidator."""

    def test_valid_document(self) -> None:
        """Un CFDI correcto no debe reportar errores."""
        xml = (FIXTURES_DIR / "valid_xsd.xml").read_text(encoding="utf-8")
        validator = CFDIXSDValidator()
        assert validator.validate(xml) == []

    def test_invalid_moneda_catalog(self, valid_cfdi_40_xml: str) -> None:
        """Una moneda fuera de catálogo debe fallar la validación."""
        xml = valid_cfdi_40_xml.replace('Moneda="MXN"', 'Moneda="ZZZ"')
        validator = CFDIXSDValidator()
        errors = validator.validate(xml)
        assert errors

    def test_validate_raise(self) -> None:
        """validate_raise lanza InvalidCFDIError con documento inválido."""
        xml = (FIXTURES_DIR / "valid_xsd.xml").read_text(encoding="utf-8")
        bad = xml.replace("01010101", "noesclave", 1)
        validator = CFDIXSDValidator()
        with pytest.raises(InvalidCFDIError):
            validator.validate_raise(bad)


class TestCFDIParserXSD:
    """Test suite para el parser con validación XSD activada."""

    def test_parse_valid_with_xsd(self) -> None:
        """Parser con validate_xsd=True acepta un CFDI válido."""
        xml = (FIXTURES_DIR / "valid_xsd.xml").read_text(encoding="utf-8")
        parser = CFDIParser(validate_xsd=True)
        cfdi = parser.parse_string(xml)
        assert cfdi.version == "4.0"

    def test_parse_invalid_with_xsd_raises(self, valid_cfdi_40_xml: str) -> None:
        """Parser con validate_xsd=True rechaza un CFDI fuera de catálogo."""
        xml = valid_cfdi_40_xml.replace('Moneda="MXN"', 'Moneda="ZZZ"')
        parser = CFDIParser(validate_xsd=True)
        with pytest.raises(InvalidCFDIError):
            parser.parse_string(xml)
