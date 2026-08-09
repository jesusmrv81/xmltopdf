"""Tests para el Complemento de Nómina 1.2."""

from decimal import Decimal
from pathlib import Path

from cfdi_pdf.parser import CFDIParser

FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestNominaParser:
    """Test suite para el parser de Nómina 1.2."""

    def test_parse_nomina_basic(self) -> None:
        """Parsea los campos principales del complemento de nómina."""
        cfdi = CFDIParser().parse_file(FIXTURES_DIR / "nomina12.xml")

        assert cfdi.tipo_comprobante == "N"
        assert cfdi.nomina is not None
        assert cfdi.nomina.version == "1.2"
        assert cfdi.nomina.tipo_nomina == "O"
        assert cfdi.nomina.num_dias_pagados == Decimal("15")
        assert cfdi.nomina.total_percepciones == Decimal("1000.00")
        assert cfdi.nomina.total_deducciones == Decimal("100.00")

    def test_parse_nomina_receptor(self) -> None:
        """Parsea los datos del receptor de la nómina."""
        cfdi = CFDIParser().parse_file(FIXTURES_DIR / "nomina12.xml")
        assert cfdi.nomina is not None

        receptor = cfdi.nomina.receptor
        assert receptor.num_empleado == "001"
        assert receptor.tipo_contrato == "01"
        assert receptor.tipo_regimen == "02"
        assert receptor.periodicidad_pago == "04"
        assert receptor.salario_diario_integrado == Decimal("110.00")
        assert cfdi.nomina.emisor is not None
        assert cfdi.nomina.emisor.registro_patronal == "PAT12345"

    def test_parse_nomina_percepciones(self) -> None:
        """Parsea percepciones, deducciones y otros pagos."""
        cfdi = CFDIParser().parse_file(FIXTURES_DIR / "nomina12.xml")
        assert cfdi.nomina is not None

        assert cfdi.nomina.percepciones is not None
        assert len(cfdi.nomina.percepciones.percepcion) == 1
        percepcion = cfdi.nomina.percepciones.percepcion[0]
        assert percepcion.clave == "P001"
        assert percepcion.importe_gravado == Decimal("800.00")
        assert percepcion.importe_exento == Decimal("200.00")

        assert cfdi.nomina.deducciones is not None
        assert len(cfdi.nomina.deducciones.deduccion) == 2
        assert cfdi.nomina.deducciones.total_impuestos_retenidos == Decimal("50.00")

        assert cfdi.nomina.otros_pagos is not None
        assert len(cfdi.nomina.otros_pagos.otro_pago) == 1
        assert cfdi.nomina.otros_pagos.otro_pago[0].clave == "O001"

    def test_no_nomina_in_regular_cfdi(self, valid_cfdi_40_xml: str) -> None:
        """Un CFDI normal no debe traer complemento de nómina."""
        cfdi = CFDIParser().parse_string(valid_cfdi_40_xml)
        assert cfdi.nomina is None

    def test_nomina_not_in_complementos_raw(self) -> None:
        """Nómina no debe repetirse en el dict genérico de complementos."""
        cfdi = CFDIParser().parse_file(FIXTURES_DIR / "nomina12.xml")
        assert "Nomina" not in cfdi.complementos

    def test_render_nomina(self) -> None:
        """El PDF de una nómina debe generarse sin errores."""
        from cfdi_pdf import CFDIPDF

        xml = (FIXTURES_DIR / "nomina12.xml").read_text(encoding="utf-8")
        pdf = CFDIPDF(template="minimal")
        pdf_bytes, filename = pdf.render_bytes_from_string(xml)

        assert pdf_bytes.startswith(b"%PDF")
        assert filename.endswith(".pdf")
