"""Formatting utilities for CFDI PDF."""

from datetime import datetime
from decimal import Decimal
from typing import Final

CURRENCY_SYMBOLS: Final[dict[str, str]] = {
    "MXN": "$",
    "USD": "US$",
    "EUR": "€",
    "GBP": "£",
    "CAD": "C$",
    "JPY": "¥",
}


class Formatters:
    """Formatting utilities for CFDI data."""

    @staticmethod
    def format_currency(amount: Decimal, moneda: str = "MXN", include_symbol: bool = True) -> str:
        """
        Format amount as currency.

        Args:
            amount: Decimal amount
            moneda: Currency code (MXN, USD, etc.)
            include_symbol: Whether to include currency symbol

        Returns:
            Formatted currency string
        """
        # Format with 2 decimal places and thousands separator
        formatted = f"{amount:,.2f}"

        if include_symbol:
            symbol = CURRENCY_SYMBOLS.get(moneda, moneda)
            return f"{symbol} {formatted}"

        return formatted

    @staticmethod
    def format_tax_rate(rate: Decimal | None) -> str:
        """
        Convert decimal tax rate to percentage string.

        Examples:
            0.160000 -> 16%
            0.080000 -> 8%
            0.106667 -> 10.6667%
            1.000000 -> 100%
        """
        if rate is None:
            return "Exento"

        # Convert to percentage and normalize (remove trailing zeros)
        percentage = (rate * Decimal("100")).normalize()

        return f"{percentage}%"

    @staticmethod
    def format_percentage(value: Decimal, decimals: int = 2) -> str:
        """Format decimal as percentage."""
        percentage = value * Decimal("100")
        return f"{percentage:.{decimals}f}%"

    @staticmethod
    def format_number(value: Decimal, decimals: int = 2) -> str:
        """Format number with thousands separator."""
        return f"{value:,.{decimals}f}"

    @staticmethod
    def format_uuid(uuid: str) -> str:
        """Format UUID for display (uppercase)."""
        return uuid.upper()

    @staticmethod
    def format_date(date_str: str) -> str:
        """
        Format ISO date string for display.

        Args:
            date_str: ISO 8601 date string. Puede incluir hora y zona horaria
                (``2024-01-15T10:30:00``, ``2024-01-15T10:30:00-06:00``, ``...Z``).

        Returns:
            Formatted date string (``15/01/2024 10:30:00 -06:00``).
            Devuelve el texto original si no se puede parsear.
        """
        if not date_str:
            return ""

        try:
            normalized = date_str[:-1] + "+00:00" if date_str.endswith("Z") else date_str
            dt = datetime.fromisoformat(normalized)
        except ValueError:
            return date_str

        formatted = dt.strftime("%d/%m/%Y")

        if dt.hour or dt.minute or dt.second:
            formatted += f" {dt.hour:02d}:{dt.minute:02d}:{dt.second:02d}"

        if dt.tzinfo is not None:
            offset = dt.utcoffset()
            if offset is not None:
                total = int(offset.total_seconds())
                sign = "+" if total >= 0 else "-"
                total = abs(total)
                hours, minutes = divmod(total // 60, 60)
                formatted += f" {sign}{hours:02d}:{minutes:02d}"

        return formatted

    @staticmethod
    def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
        """Truncate text to maximum length."""
        if len(text) <= max_length:
            return text
        return text[: max_length - len(suffix)] + suffix
