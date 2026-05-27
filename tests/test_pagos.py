"""Tests for Complemento de Pago 2.0 parsing and rendering."""

from decimal import Decimal
from pathlib import Path

from cfdi_pdf.parser import CFDIParser

FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestPagos20Parser:
    """Test suite for Complemento de Pago 2.0 parser."""

    def test_parse_pagos_multiple(self) -> None:
        """Test parsing CFDI with multiple Pagos (different currencies)."""
        xml_path = FIXTURES_DIR / "pagos20_multiple.xml"
        parser = CFDIParser()
        cfdi = parser.parse_file(xml_path)

        # Root CFDI validation
        assert cfdi.version == "4.0"
        assert cfdi.tipo_comprobante == "P"
        assert cfdi.total == 0

        # Pagos complement
        assert cfdi.pagos is not None
        assert cfdi.pagos.version == "2.0"

        # Totales
        totales = cfdi.pagos.totales
        assert totales.monto_total_pagos == Decimal("1600986.46")
        assert totales.total_traslados_base_iva16 == Decimal("1380160.72")
        assert totales.total_traslados_impuesto_iva16 == Decimal("220825.70")
        assert totales.total_retenciones_iva is None

        # Pago count
        assert len(cfdi.pagos.pago) == 2

        # First Pago
        pago1 = cfdi.pagos.pago[0]
        assert pago1.fecha_pago == "2022-04-28T17:49:04"
        assert pago1.forma_de_pago_p == "03"
        assert pago1.moneda_p == "MXN"
        assert pago1.tipo_cambio_p == Decimal("1")
        assert pago1.monto == Decimal("7097.38")

        # DoctoRelacionado for first Pago
        assert len(pago1.docto_relacionado) == 1
        docto1 = pago1.docto_relacionado[0]
        assert docto1.id_documento == "79ff44fd-f0ba-4024-a55f-0a228fa72903"
        assert docto1.moneda_dr == "USD"
        assert docto1.equivalencia_dr == Decimal("0.049693")
        assert docto1.num_parcialidad == 2
        assert docto1.imp_saldo_ant == Decimal("352.69")
        assert docto1.imp_pagado == Decimal("352.69")
        assert docto1.imp_saldo_insoluto == Decimal("0")
        assert docto1.objeto_imp_dr == "02"

        # ImpuestosDR for first Docto
        assert docto1.impuestos_dr is not None
        assert len(docto1.impuestos_dr.traslados_dr) == 1
        assert len(docto1.impuestos_dr.retenciones_dr) == 0
        traslado_dr = docto1.impuestos_dr.traslados_dr[0]
        assert traslado_dr.base_dr == Decimal("304.043103")
        assert traslado_dr.impuesto_dr == "002"
        assert traslado_dr.tipo_factor_dr == "Tasa"
        assert traslado_dr.tasa_o_cuota_dr == Decimal("0.160000")
        assert traslado_dr.importe_dr == Decimal("48.646897")

        # ImpuestosP for first Pago
        assert pago1.impuestos_p is not None
        assert len(pago1.impuestos_p.traslados_p) == 1
        assert len(pago1.impuestos_p.retenciones_p) == 0
        traslado_p = pago1.impuestos_p.traslados_p[0]
        assert traslado_p.base_p == Decimal("6118.42")
        assert traslado_p.impuesto_p == "002"
        assert traslado_p.tipo_factor_p == "Tasa"
        assert traslado_p.tasa_o_cuota_p == Decimal("0.160000")
        assert traslado_p.importe_p == Decimal("978.94")

    def test_parse_pagos_retenciones(self) -> None:
        """Test parsing CFDI with Retenciones in Pagos 2.0."""
        xml_path = FIXTURES_DIR / "pagos20_retenciones.xml"
        parser = CFDIParser()
        cfdi = parser.parse_file(xml_path)

        assert cfdi.pagos is not None
        assert len(cfdi.pagos.pago) == 1

        # Totales con retenciones
        totales = cfdi.pagos.totales
        assert totales.total_retenciones_iva == Decimal("16.00")
        assert totales.monto_total_pagos == Decimal("100.00")

        # Pago
        pago = cfdi.pagos.pago[0]
        assert pago.moneda_p == "MXN"
        assert pago.monto == Decimal("100.00")

        # DoctoRelacionado with both RetencionesDR and TrasladosDR
        assert len(pago.docto_relacionado) == 1
        docto = pago.docto_relacionado[0]
        assert docto.moneda_dr == "MXN"
        assert docto.imp_saldo_ant == Decimal("98.75")
        assert docto.imp_pagado == Decimal("98.75")
        assert docto.imp_saldo_insoluto == Decimal("0.00")

        assert docto.impuestos_dr is not None
        assert len(docto.impuestos_dr.retenciones_dr) == 1
        assert len(docto.impuestos_dr.traslados_dr) == 1

        # RetencionDR
        retencion_dr = docto.impuestos_dr.retenciones_dr[0]
        assert retencion_dr.base_dr == Decimal("100.00")
        assert retencion_dr.impuesto_dr == "002"
        assert retencion_dr.importe_dr == Decimal("16.00")

        # ImpuestosP with both RetencionesP and TrasladosP
        assert pago.impuestos_p is not None
        assert len(pago.impuestos_p.retenciones_p) == 1
        assert len(pago.impuestos_p.traslados_p) == 1

        # RetencionP (only has ImpuestoP + ImporteP, no BaseP/TipoFactorP/TasaOCuotaP)
        retencion_p = pago.impuestos_p.retenciones_p[0]
        assert retencion_p.impuesto_p == "002"
        assert retencion_p.importe_p == Decimal("16.00")

        # TrasladoP
        traslado_p = pago.impuestos_p.traslados_p[0]
        assert traslado_p.base_p == Decimal("100.00")
        assert traslado_p.impuesto_p == "002"
        assert traslado_p.importe_p == Decimal("16.00")

    def test_no_pagos_in_regular_cfdi(self, valid_cfdi_40_xml: str) -> None:
        """Test that regular CFDI (non-P) has no Pagos."""
        parser = CFDIParser()
        cfdi = parser.parse_string(valid_cfdi_40_xml)
        assert cfdi.pagos is None

    def test_pagos_version(self, valid_cfdi_40_xml: str) -> None:
        """Test pagos version is always 2.0."""
        xml_path = FIXTURES_DIR / "pagos20_multiple.xml"
        parser = CFDIParser()
        cfdi = parser.parse_file(xml_path)
        assert cfdi.pagos is not None
        assert cfdi.pagos.version == "2.0"

    def test_pagos_in_complementos_raw(self) -> None:
        """Test that Pagos is NOT included in complementos raw dict."""
        xml_path = FIXTURES_DIR / "pagos20_multiple.xml"
        parser = CFDIParser()
        cfdi = parser.parse_file(xml_path)
        # Pagos should NOT be in complementos (it's handled by dedicated parser)
        assert "Pagos" not in cfdi.complementos

    def test_pagos_timbre_fiscal(self) -> None:
        """Test that TimbreFiscalDigital is parsed correctly along with Pagos."""
        xml_path = FIXTURES_DIR / "pagos20_retenciones.xml"
        parser = CFDIParser()
        cfdi = parser.parse_file(xml_path)

        assert cfdi.timbre_fiscal is not None
        assert cfdi.timbre_fiscal.uuid == "b8fa6f87-443f-437a-80e6-799dfe501ca7"
        assert cfdi.timbre_fiscal.version == "1.1"
