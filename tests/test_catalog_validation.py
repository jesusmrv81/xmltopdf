"""Tests para la validación de catálogos SAT standalone."""

from pathlib import Path

import pytest

from cfdi_pdf import CFDIPDF
from cfdi_pdf.exceptions import InvalidCFDIError
from cfdi_pdf.parser import CFDIParser

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _read(name: str) -> str:
    return (FIXTURES_DIR / name).read_text(encoding="utf-8")


class TestCatalogValidation:
    """Test suite para validate_catalogs."""

    def test_valid_cfdi_passes(self, valid_cfdi_40_xml: str) -> None:
        parser = CFDIParser(validate_catalogs=True)
        cfdi = parser.parse_string(valid_cfdi_40_xml)
        assert cfdi.version == "4.0"

    def test_invalid_moneda(self, valid_cfdi_40_xml: str) -> None:
        xml = valid_cfdi_40_xml.replace('Moneda="MXN"', 'Moneda="ZZZ"')
        parser = CFDIParser(validate_catalogs=True)
        with pytest.raises(InvalidCFDIError, match="moneda"):
            parser.parse_string(xml)

    def test_invalid_regimen_fiscal(self, valid_cfdi_40_xml: str) -> None:
        xml = valid_cfdi_40_xml.replace('RegimenFiscal="601"', 'RegimenFiscal="999"')
        parser = CFDIParser(validate_catalogs=True)
        with pytest.raises(InvalidCFDIError, match="regimen_fiscal"):
            parser.parse_string(xml)

    def test_invalid_uso_cfdi(self, valid_cfdi_40_xml: str) -> None:
        xml = valid_cfdi_40_xml.replace('UsoCFDI="S01"', 'UsoCFDI="ZZZ"')
        parser = CFDIParser(validate_catalogs=True)
        with pytest.raises(InvalidCFDIError, match="uso_cfdi"):
            parser.parse_string(xml)

    def test_invalid_objeto_imp(self, valid_cfdi_40_xml: str) -> None:
        xml = valid_cfdi_40_xml.replace('ObjetoImp="02"', 'ObjetoImp="99"')
        parser = CFDIParser(validate_catalogs=True)
        with pytest.raises(InvalidCFDIError, match="objeto_imp"):
            parser.parse_string(xml)

    def test_disabled_by_default(self, valid_cfdi_40_xml: str) -> None:
        """Sin validate_catalogs no se valida (default tolerante)."""
        xml = valid_cfdi_40_xml.replace('Moneda="MXN"', 'Moneda="ZZZ"')
        parser = CFDIParser()
        cfdi = parser.parse_string(xml)
        assert cfdi.moneda == "ZZZ"

    def test_api_validate_catalogs(self, valid_cfdi_40_xml: str) -> None:
        pdf = CFDIPDF(validate_catalogs=True)
        cfdi = pdf.parse_string(valid_cfdi_40_xml)
        assert cfdi.moneda == "MXN"

    def test_pagos20_valid(self) -> None:
        """Un CFDI de pagos con catálogos correctos debe pasar."""
        parser = CFDIParser(validate_catalogs=True)
        cfdi = parser.parse_file(FIXTURES_DIR / "pagos20_retenciones.xml")
        assert cfdi.tipo_comprobante == "P"
