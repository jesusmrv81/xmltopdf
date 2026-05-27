"""Tests for SAT catalogs."""

from cfdi_pdf.sat import SATCatalogs


class TestSATCatalogs:
    """Test suite for SATCatalogs."""

    def test_get_regimen_fiscal(self) -> None:
        """Test régimen fiscal lookup."""
        assert SATCatalogs.get_regimen_fiscal("601") == "General de Ley Personas Morales"
        assert SATCatalogs.get_regimen_fiscal("616") == "Sin obligaciones fiscales"

    def test_get_uso_cfdi(self) -> None:
        """Test uso CFDI lookup."""
        assert SATCatalogs.get_uso_cfdi("G03") == "Gastos en general"
        assert SATCatalogs.get_uso_cfdi("S01") == "Sin efectos fiscales"

    def test_get_forma_pago(self) -> None:
        """Test forma de pago lookup."""
        assert SATCatalogs.get_forma_pago("03") == "Transferencia electrónica de fondos"
        assert SATCatalogs.get_forma_pago("01") == "Efectivo"

    def test_get_metodo_pago(self) -> None:
        """Test método de pago lookup."""
        assert SATCatalogs.get_metodo_pago("PUE") == "Pago en una sola exhibición"
        assert SATCatalogs.get_metodo_pago("PPD") == "Pago en parcialidades o diferido"

    def test_get_tipo_comprobante(self) -> None:
        """Test tipo de comprobante lookup."""
        assert SATCatalogs.get_tipo_comprobante("I") == "Ingreso"
        assert SATCatalogs.get_tipo_comprobante("E") == "Egreso"

    def test_get_impuesto(self) -> None:
        """Test impuesto lookup."""
        assert SATCatalogs.get_impuesto("002") == "IVA"
        assert SATCatalogs.get_impuesto("001") == "ISR"

    def test_get_unknown_code(self) -> None:
        """Test unknown code returns descriptive message."""
        result = SATCatalogs.get_regimen_fiscal("999")
        assert "Desconocido" in result
        assert "999" in result
