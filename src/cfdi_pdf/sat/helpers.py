"""SAT helper utilities."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models import CFDI


class SATHelpers:
    """Helper utilities for SAT CFDI operations."""

    @staticmethod
    def build_cadena_original(cfdi: "CFDI") -> str:
        """
        Build cadena original for CFDI.

        NOTE: This is a simplified version. In production, use official XSLT.
        """
        if cfdi.timbre_fiscal is None:
            return ""

        # Simplified cadena original format
        parts = [
            cfdi.version,
            cfdi.serie or "",
            cfdi.folio or "",
            cfdi.fecha,
            cfdi.forma_pago,
            cfdi.metodo_pago,
            str(cfdi.sub_total),
            str(cfdi.descuento) if cfdi.descuento else "",
            cfdi.moneda,
            str(cfdi.tipo_cambio) if cfdi.tipo_cambio else "",
            str(cfdi.total),
            cfdi.tipo_comprobante,
            cfdi.exportacion,
            cfdi.lugar_expedicion,
        ]

        return "||" + "|".join(parts) + "||"

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
