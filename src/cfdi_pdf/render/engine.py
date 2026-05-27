"""PDF render engine using Jinja2 and WeasyPrint."""

import base64
import logging
from pathlib import Path
from typing import Any

from weasyprint import HTML

from ..exceptions import PDFGenerationError, TemplateRenderError
from ..models import CFDI
from ..qr import SATQRGenerator
from ..sat import SATCatalogs, SATHelpers
from ..utils import Formatters
from .template import TemplateManager

logger = logging.getLogger(__name__)

# MIME types for logo images
_LOGO_MIME_TYPES: dict[str, str] = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".svg": "image/svg+xml",
}


class RenderEngine:
    """Renders CFDI to PDF using Jinja2 templates and WeasyPrint."""

    def __init__(
        self,
        template_manager: TemplateManager | None = None,
        qr_generator: SATQRGenerator | None = None,
    ) -> None:
        """
        Initialize render engine.

        Args:
            template_manager: Template manager instance
            qr_generator: QR generator instance
        """
        self._template_manager = template_manager or TemplateManager()
        self._qr_generator = qr_generator or SATQRGenerator()
        self._catalogs = SATCatalogs()
        self._helpers = SATHelpers()
        self._formatters = Formatters()

    def render(
        self,
        cfdi: CFDI,
        template_name: str = "minimal",
        output_path: str | Path | None = None,
        logo_path: str | Path | None = None,
    ) -> bytes:
        """
        Render CFDI to PDF.

        Args:
            cfdi: CFDI model instance
            template_name: Name of the template to use
            output_path: Optional path to save PDF (if None, returns bytes)
            logo_path: Optional path to logo image

        Returns:
            PDF as bytes

        Raises:
            TemplateRenderError: If template rendering fails
            PDFGenerationError: If PDF generation fails
        """
        # Get template — raises TemplateNotFoundError (subclass of CFDIPDFError) on miss
        template = self._template_manager.get_template(template_name)

        # Prepare context
        context = self._build_context(cfdi, logo_path)

        # Render HTML
        logger.debug("Rendering template: %s", template_name)
        try:
            html_content = template.render(**context)
        except Exception as exc:
            raise TemplateRenderError(f"Failed to render template '{template_name}'") from exc

        # Get base URL for CSS and asset resolution
        template_dir = self._template_manager.get_template_dir(template_name)
        base_url = str(template_dir) if template_dir else None

        # Generate PDF
        logger.debug("Generating PDF with WeasyPrint")
        try:
            html = HTML(string=html_content, base_url=base_url)
            if output_path:
                resolved = Path(output_path)
                html.write_pdf(str(resolved))
                logger.info("PDF saved to: %s", resolved)
                return b""
            else:
                pdf_bytes: bytes = html.write_pdf()
                logger.info("PDF generated successfully")
                return pdf_bytes
        except Exception as exc:
            raise PDFGenerationError(f"Failed to generate PDF: {exc}") from exc

    def _build_context(self, cfdi: CFDI, logo_path: str | Path | None = None) -> dict[str, Any]:
        """Build template context with all necessary data."""
        qr_data = self._build_qr_data(cfdi)
        logo_data = self._build_logo_data(logo_path)
        cadena_original = self._build_cadena_original(cfdi)

        return {
            # CFDI data
            "cfdi": cfdi,
            # QR code (base64-encoded PNG)
            "qr_data": qr_data,
            # Logo (base64 data URL or empty string)
            "logo_data": logo_data,
            # Cadena original del complemento
            "cadena_original": cadena_original,
            # Pre-formatted display values
            "formatted": self._build_formatted(cfdi),
            # Human-readable catalog descriptions
            "catalogs": self._build_catalogs(cfdi),
            # Helper callables for templates
            "format_currency": self._formatters.format_currency,
            "format_tax_rate": self._formatters.format_tax_rate,
            "format_number": self._formatters.format_number,
            "format_date": self._formatters.format_date,
            "get_impuesto": self._catalogs.get_impuesto,
            "get_objeto_impuesto": self._catalogs.get_objeto_impuesto,
            "moneda": cfdi.moneda,
        }

    # ── private helpers ───────────────────────────────────────────────────────

    def _build_qr_data(self, cfdi: CFDI) -> str:
        """Return base64-encoded QR PNG, or empty string on failure."""
        if cfdi.timbre_fiscal is None:
            return ""
        try:
            qr_bytes = self._qr_generator.generate_from_cfdi(cfdi)
            return base64.b64encode(qr_bytes).decode("utf-8")
        except Exception as exc:
            logger.warning("Failed to generate QR code: %s", exc)
            return ""

    def _build_logo_data(self, logo_path: str | Path | None) -> str:
        """Return base64 data URL for logo, or empty string on failure."""
        if logo_path is None:
            return ""
        try:
            path = Path(logo_path)
            if not path.exists():
                logger.warning("Logo file not found: %s", path)
                return ""
            logo_bytes = path.read_bytes()
            mime_type = _LOGO_MIME_TYPES.get(path.suffix.lower(), "image/png")
            return f"data:{mime_type};base64,{base64.b64encode(logo_bytes).decode()}"
        except OSError as exc:
            logger.warning("Failed to load logo: %s", exc)
            return ""

    def _build_cadena_original(self, cfdi: CFDI) -> str:
        """Return cadena original from timbre or helpers fallback."""
        if cfdi.timbre_fiscal is None:
            return ""
        return cfdi.timbre_fiscal.cadena_origen or self._helpers.build_cadena_original(cfdi)

    def _build_formatted(self, cfdi: CFDI) -> dict[str, str | None]:
        """Build pre-formatted display values dict."""
        tfd = cfdi.timbre_fiscal
        return {
            "sub_total": self._formatters.format_currency(cfdi.sub_total, cfdi.moneda),
            "total": self._formatters.format_currency(cfdi.total, cfdi.moneda),
            "descuento": (
                self._formatters.format_currency(cfdi.descuento, cfdi.moneda)
                if cfdi.descuento
                else None
            ),
            "fecha": self._formatters.format_date(cfdi.fecha),
            "fecha_timbrado": (self._formatters.format_date(tfd.fecha_timbrado) if tfd else None),
            "uuid": self._formatters.format_uuid(tfd.uuid) if tfd else None,
            "sello_cfd": self._helpers.format_sello(tfd.sello_cfd) if tfd else None,
            "sello_sat": self._helpers.format_sello(tfd.sello_sat) if tfd else None,
        }

    def _build_catalogs(self, cfdi: CFDI) -> dict[str, str]:
        """Build human-readable catalog descriptions dict."""
        return {
            "regimen_fiscal_emisor": self._catalogs.get_regimen_fiscal(cfdi.emisor.regimen_fiscal),
            "regimen_fiscal_receptor": self._catalogs.get_regimen_fiscal(
                cfdi.receptor.regimen_fiscal
            ),
            "uso_cfdi": self._catalogs.get_uso_cfdi(cfdi.receptor.uso_cfdi),
            "forma_pago": self._catalogs.get_forma_pago(cfdi.forma_pago),
            "metodo_pago": self._catalogs.get_metodo_pago(cfdi.metodo_pago),
            "tipo_comprobante": self._catalogs.get_tipo_comprobante(cfdi.tipo_comprobante),
            "exportacion": self._catalogs.get_exportacion(cfdi.exportacion),
            "moneda": self._catalogs.get_moneda(cfdi.moneda),
        }
