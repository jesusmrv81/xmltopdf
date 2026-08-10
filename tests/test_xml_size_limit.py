"""Tests para el límite de tamaño del XML (anti-DoS)."""

from pathlib import Path

import pytest

from cfdi_pdf import CFDIPDF
from cfdi_pdf.exceptions import XMLTooLargeError
from cfdi_pdf.parser import CFDIParser


class TestXMLSizeLimit:
    """Test suite para max_xml_size."""

    def test_string_over_limit_raises(self, valid_cfdi_40_xml: str) -> None:
        parser = CFDIParser(max_xml_size=100)
        with pytest.raises(XMLTooLargeError):
            parser.parse_string(valid_cfdi_40_xml)

    def test_string_within_limit(self, valid_cfdi_40_xml: str) -> None:
        parser = CFDIParser(max_xml_size=10_000)
        cfdi = parser.parse_string(valid_cfdi_40_xml)
        assert cfdi.version == "4.0"

    def test_file_over_limit_raises(self, tmp_path: Path, valid_cfdi_40_xml: str) -> None:
        xml_path = tmp_path / "grande.xml"
        xml_path.write_text(valid_cfdi_40_xml, encoding="utf-8")
        parser = CFDIParser(max_xml_size=100)
        with pytest.raises(XMLTooLargeError):
            parser.parse_file(xml_path)

    def test_none_disables_limit(self, valid_cfdi_40_xml: str) -> None:
        parser = CFDIParser(max_xml_size=None)
        cfdi = parser.parse_string(valid_cfdi_40_xml)
        assert cfdi.version == "4.0"

    def test_default_limit_allows_normal(self, valid_cfdi_40_xml: str) -> None:
        parser = CFDIParser()
        cfdi = parser.parse_string(valid_cfdi_40_xml)
        assert cfdi.version == "4.0"

    def test_api_passes_limit(self, valid_cfdi_40_xml: str) -> None:
        pdf = CFDIPDF(max_xml_size=100)
        with pytest.raises(XMLTooLargeError):
            pdf.parse_string(valid_cfdi_40_xml)
