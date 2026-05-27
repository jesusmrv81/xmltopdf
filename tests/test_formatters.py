"""Tests for formatters."""

from decimal import Decimal

from cfdi_pdf.utils import Formatters


class TestFormatters:
    """Test suite for Formatters."""

    def test_format_currency_mxn(self) -> None:
        """Test MXN currency formatting."""
        assert Formatters.format_currency(Decimal("1000.50"), "MXN") == "$ 1,000.50"

    def test_format_currency_usd(self) -> None:
        """Test USD currency formatting."""
        assert Formatters.format_currency(Decimal("1000.50"), "USD") == "US$ 1,000.50"

    def test_format_currency_without_symbol(self) -> None:
        """Test currency formatting without symbol."""
        assert (
            Formatters.format_currency(Decimal("1000.50"), "MXN", include_symbol=False)
            == "1,000.50"
        )

    def test_format_tax_rate_16_percent(self) -> None:
        """Test 16% tax rate formatting."""
        assert Formatters.format_tax_rate(Decimal("0.160000")) == "16%"

    def test_format_tax_rate_8_percent(self) -> None:
        """Test 8% tax rate formatting."""
        assert Formatters.format_tax_rate(Decimal("0.080000")) == "8%"

    def test_format_tax_rate_with_decimals(self) -> None:
        """Test tax rate with decimal percentage."""
        result = Formatters.format_tax_rate(Decimal("0.106667"))
        assert "%" in result
        assert "10.6667" in result

    def test_format_tax_rate_exento(self) -> None:
        """Test exempt tax rate formatting."""
        assert Formatters.format_tax_rate(None) == "Exento"

    def test_format_date(self) -> None:
        """Test date formatting."""
        result = Formatters.format_date("2024-01-15T10:30:00")
        assert "15/01/2024" in result
        assert "10:30:00" in result

    def test_format_uuid_uppercase(self) -> None:
        """Test UUID uppercase formatting."""
        uuid = "cce4d168-1234-5678-9abc-def012345678"
        assert Formatters.format_uuid(uuid) == "CCE4D168-1234-5678-9ABC-DEF012345678"

    def test_format_number_with_thousands(self) -> None:
        """Test number formatting with thousands separator."""
        assert Formatters.format_number(Decimal("1234567.89")) == "1,234,567.89"

    def test_truncate_text(self) -> None:
        """Test text truncation."""
        text = "This is a very long text that needs to be truncated"
        result = Formatters.truncate_text(text, 20)
        assert len(result) <= 20
        assert result.endswith("...")
