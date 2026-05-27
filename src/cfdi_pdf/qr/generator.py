"""SAT QR code generator for CFDI 4.0."""

import logging
from decimal import Decimal
from io import BytesIO
from typing import TYPE_CHECKING

import qrcode
from qrcode.constants import ERROR_CORRECT_M

from ..exceptions import InvalidSATQRError

if TYPE_CHECKING:
    from ..models import CFDI

logger = logging.getLogger(__name__)


class SATQRGenerator:
    """Generates SAT-compliant QR codes for CFDI 4.0."""

    SAT_VERIFICATION_URL = "https://verificacfdi.facturaelectronica.sat.gob.mx/default.aspx"

    def __init__(
        self,
        box_size: int = 10,
        border: int = 4,
        error_correction: int = ERROR_CORRECT_M,
    ) -> None:
        """
        Initialize QR generator.

        Args:
            box_size: Size of each box in pixels
            border: Border size in boxes
            error_correction: QR error correction level
        """
        self.box_size = box_size
        self.border = border
        self.error_correction = error_correction

    def generate_from_cfdi(self, cfdi: "CFDI") -> bytes:
        """
        Generate QR code from CFDI model.

        Args:
            cfdi: CFDI model instance

        Returns:
            PNG image as bytes
        """
        if cfdi.timbre_fiscal is None:
            raise InvalidSATQRError("CFDI must have TimbreFiscalDigital to generate QR")

        return self.generate(
            uuid=cfdi.timbre_fiscal.uuid,
            rfc_emisor=cfdi.emisor.rfc,
            rfc_receptor=cfdi.receptor.rfc,
            total=cfdi.total,
            sello_cfd=cfdi.timbre_fiscal.sello_cfd,
        )

    def generate(
        self,
        uuid: str,
        rfc_emisor: str,
        rfc_receptor: str,
        total: Decimal,
        sello_cfd: str,
    ) -> bytes:
        """
        Generate SAT QR code.

        Args:
            uuid: Folio fiscal UUID
            rfc_emisor: RFC del emisor
            rfc_receptor: RFC del receptor
            total: Total del comprobante
            sello_cfd: Sello digital del CFDI

        Returns:
            PNG image as bytes
        """
        # Validate inputs
        self._validate_inputs(uuid, rfc_emisor, rfc_receptor, total, sello_cfd)

        # Build URL
        url = self._build_url(uuid, rfc_emisor, rfc_receptor, total, sello_cfd)

        logger.debug(f"Generating QR for URL: {url}")

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=self.error_correction,
            box_size=self.box_size,
            border=self.border,
        )

        qr.add_data(url)
        qr.make(fit=True)

        # Create image
        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to PNG bytes
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        return buffer.getvalue()

    def _build_url(
        self,
        uuid: str,
        rfc_emisor: str,
        rfc_receptor: str,
        total: Decimal,
        sello_cfd: str,
    ) -> str:
        """Build SAT verification URL (no encoding applied)."""
        total_formatted = self._format_total(total)
        fe = sello_cfd[-8:]
        uuid_upper = uuid.upper()

        return (
            f"{self.SAT_VERIFICATION_URL}"
            f"?id={uuid_upper}"
            f"&re={rfc_emisor}"
            f"&rr={rfc_receptor}"
            f"&tt={total_formatted}"
            f"&fe={fe}"
        )

    def _format_total(self, total: Decimal) -> str:
        """
        Format total with exactly 6 decimal places.

        Examples:
            1234.56 -> 1234.560000
            1234.567890 -> 1234.567890
            100 -> 100.000000
        """
        # Quantize to 6 decimal places
        formatted = f"{total:.6f}"

        # Validate format
        if "." not in formatted:
            raise InvalidSATQRError(f"Invalid total format: {formatted}")

        integer_part, decimal_part = formatted.split(".")
        if len(decimal_part) != 6:
            raise InvalidSATQRError(f"Total must have exactly 6 decimals: {formatted}")

        return formatted

    def _validate_inputs(
        self,
        uuid: str,
        rfc_emisor: str,
        rfc_receptor: str,
        total: Decimal,
        sello_cfd: str,
    ) -> None:
        """Validate QR code inputs."""
        if not uuid:
            raise InvalidSATQRError("UUID is required")

        if not rfc_emisor:
            raise InvalidSATQRError("RFC emisor is required")

        if not rfc_receptor:
            raise InvalidSATQRError("RFC receptor is required")

        if total < 0:
            raise InvalidSATQRError("Total cannot be negative")

        if not sello_cfd:
            raise InvalidSATQRError("Sello CFD is required")

        if len(sello_cfd) < 8:
            raise InvalidSATQRError("Sello CFD must be at least 8 characters")

        # Validate UUID format (basic check)
        if len(uuid) != 36 or uuid.count("-") != 4:
            logger.warning(f"UUID format may be invalid: {uuid}")
