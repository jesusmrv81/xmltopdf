"""Formatting utilities for CFDI PDF."""

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
            date_str: ISO 8601 date string (2024-01-15T10:30:00)

        Returns:
            Formatted date string (15/01/2024 10:30:00)
        """
        if not date_str:
            return ""

        try:
            # Parse ISO format
            if "T" in date_str:
                date_part, time_part = date_str.split("T")
            else:
                date_part = date_str
                time_part = ""

            # Reformat date (YYYY-MM-DD -> DD/MM/YYYY)
            year, month, day = date_part.split("-")
            formatted = f"{day}/{month}/{year}"

            if time_part:
                formatted += f" {time_part}"

            return formatted
        except Exception:
            return date_str

    @staticmethod
    def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
        """Truncate text to maximum length."""
        if len(text) <= max_length:
            return text
        return text[: max_length - len(suffix)] + suffix
