"""SAT helper utilities."""


class SATHelpers:
    """Helper utilities for SAT CFDI operations."""

    @staticmethod
    def format_sello(sello: str, chunk_size: int = 64) -> str:
        """
        Format sello digital for display (with line breaks).

        Args:
            sello: Sello digital string
            chunk_size: Characters per line

        Returns:
            Formatted sello with line breaks
        """
        if not sello:
            return ""

        chunks = [sello[i : i + chunk_size] for i in range(0, len(sello), chunk_size)]
        return "\n".join(chunks)

    @staticmethod
    def truncate_sello_for_qr(sello: str) -> str:
        """Get last 8 characters of sello for QR code."""
        if len(sello) < 8:
            return sello
        return sello[-8:]
