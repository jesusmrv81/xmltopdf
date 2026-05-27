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
        try:
            # Get template
            template = self._template_manager.get_template(template_name)

            # Prepare context
            context = self._build_context(cfdi, logo_path)

            # Render HTML
            logger.debug(f"Rendering template: {template_name}")
            html_content = template.render(**context)

            # Get base URL for CSS and assets resolution
            template_dir = self._template_manager.get_template_dir(template_name)
            base_url = str(template_dir) if template_dir else None

            # Generate PDF
            logger.debug("Generating PDF with WeasyPrint")
            html = HTML(string=html_content, base_url=base_url)

            if output_path:
                output_path = Path(output_path)
                html.write_pdf(str(output_path))
                logger.info(f"PDF saved to: {output_path}")
                return b""
            else:
                pdf_bytes = html.write_pdf()
                logger.info("PDF generated successfully")
                return pdf_bytes

        except Exception as e:
            if "Template" in str(type(e).__name__):
                raise
            raise PDFGenerationError(f"Failed to generate PDF: {e}") from e

    def _build_context(self, cfdi: CFDI, logo_path: str | Path | None = None) -> dict[str, Any]:
        """Build template context with all necessary data."""
        # Generate QR code
        qr_data = ""
        if cfdi.timbre_fiscal:
            try:
                qr_bytes = self._qr_generator.generate_from_cfdi(cfdi)
                qr_data = base64.b64encode(qr_bytes).decode("utf-8")
            except Exception as e:
                logger.warning(f"Failed to generate QR code: {e}")

        # Load logo if provided
        logo_data = ""
        if logo_path:
            try:
                logo_path = Path(logo_path)
                if logo_path.exists():
                    logo_bytes = logo_path.read_bytes()
                    # Detect MIME type
                    suffix = logo_path.suffix.lower()
                    mime_type = {
                        ".png": "image/png",
                        ".jpg": "image/jpeg",
                        ".jpeg": "image/jpeg",
                        ".svg": "image/svg+xml",
                    }.get(suffix, "image/png")
                    logo_data = f"data:{mime_type};base64,{base64.b64encode(logo_bytes).decode()}"
            except Exception as e:
                logger.warning(f"Failed to load logo: {e}")

        # Build cadena original if not present
        cadena_original = ""
        if cfdi.timbre_fiscal:
            cadena_original = cfdi.timbre_fiscal.cadena_origen or self._helpers.build_cadena_original(cfdi)

        return {
            # CFDI data
            "cfdi": cfdi,
            # QR code (base64)
            "qr_data": qr_data,
            # Logo (base64 data URL)
            "logo_data": logo_data,
            # Cadena original
            "cadena_original": cadena_original,
            # Formatted values
            "formatted": {
                "sub_total": self._formatters.format_currency(cfdi.sub_total, cfdi.moneda),
                "total": self._formatters.format_currency(cfdi.total, cfdi.moneda),
                "descuento": self._formatters.format_currency(cfdi.descuento, cfdi.moneda) if cfdi.descuento else None,
                "fecha": self._formatters.format_date(cfdi.fecha),
                "fecha_timbrado": self._formatters.format_date(cfdi.timbre_fiscal.fecha_timbrado) if cfdi.timbre_fiscal else None,
                "uuid": self._formatters.format_uuid(cfdi.timbre_fiscal.uuid) if cfdi.timbre_fiscal else None,
                "sello_cfd": self._helpers.format_sello(cfdi.timbre_fiscal.sello_cfd) if cfdi.timbre_fiscal else None,
                "sello_sat": self._helpers.format_sello(cfdi.timbre_fiscal.sello_sat) if cfdi.timbre_fiscal else None,
            },
            # Catalog descriptions
            "catalogs": {
                "regimen_fiscal_emisor": self._catalogs.get_regimen_fiscal(cfdi.emisor.regimen_fiscal),
                "regimen_fiscal_receptor": self._catalogs.get_regimen_fiscal(cfdi.receptor.regimen_fiscal),
                "uso_cfdi": self._catalogs.get_uso_cfdi(cfdi.receptor.uso_cfdi),
                "forma_pago": self._catalogs.get_forma_pago(cfdi.forma_pago),
                "metodo_pago": self._catalogs.get_metodo_pago(cfdi.metodo_pago),
                "tipo_comprobante": self._catalogs.get_tipo_comprobante(cfdi.tipo_comprobante),
                "exportacion": self._catalogs.get_exportacion(cfdi.exportacion),
                "moneda": self._catalogs.get_moneda(cfdi.moneda),
            },
            # Helper functions
            "format_currency": self._formatters.format_currency,
            "format_tax_rate": self._formatters.format_tax_rate,
            "format_number": self._formatters.format_number,
            "format_date": self._formatters.format_date,
            "get_impuesto": self._catalogs.get_impuesto,
            "get_objeto_impuesto": self._catalogs.get_objeto_impuesto,
            "moneda": cfdi.moneda,
        }
