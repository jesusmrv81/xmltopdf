"""Main API for CFDI PDF library."""

import logging
from pathlib import Path
from typing import Any

from .exceptions import CFDIPDFError
from .models import CFDI
from .parser import CFDIParser
from .qr import SATQRGenerator
from .render import RenderEngine, TemplateManager

logger = logging.getLogger(__name__)


class CFDIPDF:
    """
    Main class for converting CFDI 4.0 XML to PDF.

    Example:
        ```python
        from cfdi_pdf import CFDIPDF

        pdf = CFDIPDF(template="minimal")
        pdf.render(xml_path="factura.xml", output="factura.pdf")
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

        # Initialize components
        self._parser = CFDIParser()
        self._qr_generator = SATQRGenerator()

        # Convert custom paths to Path objects
        template_paths = None
        if custom_template_paths:
            template_paths = [Path(p) for p in custom_template_paths]

        self._template_manager = TemplateManager(custom_template_paths=template_paths)
        self._render_engine = RenderEngine(
            template_manager=self._template_manager,
            qr_generator=self._qr_generator,
        )

    def render(
        self,
        xml_path: str | Path,
        output: str | Path | None = None,
        template: str | None = None,
        logo_path: str | Path | None = None,
    ) -> bytes | None:
        """
        Render CFDI XML file to PDF.

        Args:
            xml_path: Path to CFDI XML file
            output: Path to save PDF (if None, returns bytes)
            template: Template name (overrides default)
            logo_path: Path to logo image (optional)

        Returns:
            PDF as bytes if output is None, otherwise None

        Raises:
            CFDIPDFError: If rendering fails
        """
        try:
            # Parse XML
            logger.info(f"Parsing XML: {xml_path}")
            cfdi = self._parser.parse_file(xml_path)

            # Render to PDF
            template_name = template or self._template
            logger.info(f"Rendering with template: {template_name}")

            result = self._render_engine.render(
                cfdi=cfdi,
                template_name=template_name,
                output_path=output,
                logo_path=logo_path,
            )

            if output:
                logger.info(f"PDF saved to: {output}")
                return None
            else:
                logger.info("PDF generated successfully")
                return result

        except CFDIPDFError:
            raise
        except Exception as e:
            raise CFDIPDFError(f"Failed to render PDF: {e}") from e

    def render_from_string(
        self,
        xml_content: str,
        output: str | Path | None = None,
        template: str | None = None,
        logo_path: str | Path | None = None,
    ) -> bytes | None:
        """
        Render CFDI from XML string to PDF.

        Args:
            xml_content: XML content as string
            output: Path to save PDF (if None, returns bytes)
            template: Template name (overrides default)
            logo_path: Path to logo image (optional)

        Returns:
            PDF as bytes if output is None, otherwise None

        Raises:
            CFDIPDFError: If rendering fails
        """
        try:
            # Parse XML
            logger.info("Parsing XML string")
            cfdi = self._parser.parse_string(xml_content)

            # Render to PDF
            template_name = template or self._template
            logger.info(f"Rendering with template: {template_name}")

            result = self._render_engine.render(
                cfdi=cfdi,
                template_name=template_name,
                output_path=output,
                logo_path=logo_path,
            )

            if output:
                logger.info(f"PDF saved to: {output}")
                return None
            else:
                logger.info("PDF generated successfully")
                return result

        except CFDIPDFError:
            raise
        except Exception as e:
            raise CFDIPDFError(f"Failed to render PDF: {e}") from e

    def parse(self, xml_path: str | Path) -> CFDI:
        """
        Parse CFDI XML file without rendering.

        Args:
            xml_path: Path to CFDI XML file

        Returns:
            CFDI model instance
        """
        return self._parser.parse_file(xml_path)

    def parse_string(self, xml_content: str) -> CFDI:
        """
        Parse CFDI XML string without rendering.

        Args:
            xml_content: XML content as string

        Returns:
            CFDI model instance
        """
        return self._parser.parse_string(xml_content)

    def list_templates(self) -> list[str]:
        """
        List all available templates.

        Returns:
            List of template names
        """
        return self._template_manager.list_templates()

    def set_template(self, template: str) -> None:
        """
        Set default template.

        Args:
            template: Template name
        """
        self._template = template

    def get_template(self) -> str:
        """
        Get current default template.

        Returns:
            Template name
        """
        return self._template
