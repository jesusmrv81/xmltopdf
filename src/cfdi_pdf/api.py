"""Main API for CFDI PDF library."""

import logging
from pathlib import Path

from .exceptions import CFDIPDFError
from .models import CFDI
from .parser import CFDIParser
from .qr import SATQRGenerator
from .render import RenderEngine, TemplateManager

logger = logging.getLogger(__name__)


class CFDIPDF:
    """
    Main class for converting CFDI 4.0 XML to PDF.

    The output file is always named after the UUID of the timbre fiscal:
        <uuid>.pdf

    Example:
        ```python
        from cfdi_pdf import CFDIPDF

        pdf = CFDIPDF(template="minimal")
        # Saves to ./a1b2c3d4-...-uuid.pdf in the same directory as the XML
        pdf.render(xml_path="factura.xml")

        # Or specify an output directory
        pdf.render(xml_path="factura.xml", output_dir="./pdfs")
        ```
    """

    def __init__(
        self,
        template: str = "minimal",
        locale: str = "es_MX",
        currency_format: bool = True,
        custom_template_paths: list[str | Path] | None = None,
    ) -> None:
        """
        Initialize CFDIPDF converter.

        Args:
            template: Default template name (e.g., "minimal")
            locale: Locale for formatting (default: "es_MX")
            currency_format: Whether to format currencies
            custom_template_paths: Additional paths to search for templates
        """
        self._template = template
        self._locale = locale
        self._currency_format = currency_format

        self._parser = CFDIParser()
        self._qr_generator = SATQRGenerator()

        template_paths = [Path(p) for p in custom_template_paths] if custom_template_paths else None
        self._template_manager = TemplateManager(custom_template_paths=template_paths)
        self._render_engine = RenderEngine(
            template_manager=self._template_manager,
            qr_generator=self._qr_generator,
        )

    # ── public API ────────────────────────────────────────────────────────────

    def render(
        self,
        xml_path: str | Path,
        output_dir: str | Path | None = None,
        template: str | None = None,
        logo_path: str | Path | None = None,
    ) -> Path:
        """
        Render CFDI XML file to PDF, named after the UUID of the timbre fiscal.

        The output filename is always ``{uuid}.pdf`` (lowercase UUID).
        If ``output_dir`` is not provided, the PDF is written in the same
        directory as the source XML file.

        Args:
            xml_path: Path to CFDI XML file
            output_dir: Directory where the PDF will be saved.
                        Defaults to the directory of ``xml_path``.
            template: Template name (overrides default)
            logo_path: Path to logo image (optional)

        Returns:
            Path to the generated PDF file.

        Raises:
            CFDIPDFError: If rendering fails
        """
        try:
            xml_path = Path(xml_path)
            logger.info("Parsing XML: %s", xml_path)
            cfdi = self._parser.parse_file(xml_path)

            output_path = self._resolve_output_path(cfdi, xml_path, output_dir)

            template_name = template or self._template
            logger.info("Rendering with template: %s", template_name)

            self._render_engine.render(
                cfdi=cfdi,
                template_name=template_name,
                output_path=output_path,
                logo_path=logo_path,
            )

            logger.info("PDF saved to: %s", output_path)
            return output_path

        except CFDIPDFError:
            raise
        except Exception as exc:
            raise CFDIPDFError(f"Failed to render PDF: {exc}") from exc

    def render_from_string(
        self,
        xml_content: str,
        output_dir: str | Path | None = None,
        template: str | None = None,
        logo_path: str | Path | None = None,
    ) -> Path:
        """
        Render CFDI from XML string to PDF, named after the UUID.

        Args:
            xml_content: XML content as string
            output_dir: Directory where the PDF will be saved (default: cwd)
            template: Template name (overrides default)
            logo_path: Path to logo image (optional)

        Returns:
            Path to the generated PDF file.

        Raises:
            CFDIPDFError: If rendering fails
        """
        try:
            logger.info("Parsing XML string")
            cfdi = self._parser.parse_string(xml_content)

            output_path = self._resolve_output_path(cfdi, source_path=None, output_dir=output_dir)

            template_name = template or self._template
            logger.info("Rendering with template: %s", template_name)

            self._render_engine.render(
                cfdi=cfdi,
                template_name=template_name,
                output_path=output_path,
                logo_path=logo_path,
            )

            logger.info("PDF saved to: %s", output_path)
            return output_path

        except CFDIPDFError:
            raise
        except Exception as exc:
            raise CFDIPDFError(f"Failed to render PDF: {exc}") from exc

    def render_bytes(
        self,
        xml_path: str | Path,
        template: str | None = None,
        logo_path: str | Path | None = None,
    ) -> tuple[bytes, str]:
        """
        Render CFDI XML file to PDF bytes without writing to disk.

        Args:
            xml_path: Path to CFDI XML file
            template: Template name (overrides default)
            logo_path: Path to logo image (optional)

        Returns:
            Tuple of (pdf_bytes, uuid_filename) where uuid_filename is
            the recommended filename, e.g. ``"a1b2c3...-uuid.pdf"``.

        Raises:
            CFDIPDFError: If rendering fails
        """
        try:
            xml_path = Path(xml_path)
            logger.info("Parsing XML: %s", xml_path)
            cfdi = self._parser.parse_file(xml_path)

            template_name = template or self._template
            pdf_bytes = self._render_engine.render(
                cfdi=cfdi,
                template_name=template_name,
                output_path=None,
                logo_path=logo_path,
            )

            filename = self._uuid_filename(cfdi)
            return pdf_bytes, filename

        except CFDIPDFError:
            raise
        except Exception as exc:
            raise CFDIPDFError(f"Failed to render PDF: {exc}") from exc

    def parse(self, xml_path: str | Path) -> CFDI:
        """Parse CFDI XML file without rendering."""
        return self._parser.parse_file(xml_path)

    def parse_string(self, xml_content: str) -> CFDI:
        """Parse CFDI XML string without rendering."""
        return self._parser.parse_string(xml_content)

    def list_templates(self) -> list[str]:
        """List all available templates."""
        return self._template_manager.list_templates()

    def set_template(self, template: str) -> None:
        """Set default template."""
        self._template = template

    def get_template(self) -> str:
        """Get current default template."""
        return self._template

    # ── private helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _uuid_filename(cfdi: CFDI) -> str:
        """Return ``{uuid}.pdf`` (lowercase) from the timbre fiscal."""
        if cfdi.timbre_fiscal is None:
            raise CFDIPDFError(
                "CFDI does not have a TimbreFiscalDigital — cannot determine UUID for filename."
            )
        return f"{cfdi.timbre_fiscal.uuid.lower()}.pdf"

    def _resolve_output_path(
        self,
        cfdi: CFDI,
        source_path: Path | None,
        output_dir: str | Path | None,
    ) -> Path:
        """
        Build the full output path: ``<output_dir>/<uuid>.pdf``.

        Falls back to the source XML directory when ``output_dir`` is None,
        or to ``Path.cwd()`` when the source is also unknown.
        """
        filename = self._uuid_filename(cfdi)

        if output_dir is not None:
            directory = Path(output_dir)
        elif source_path is not None:
            directory = source_path.parent
        else:
            directory = Path.cwd()

        directory.mkdir(parents=True, exist_ok=True)
        return directory / filename
