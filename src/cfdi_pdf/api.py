"""Main API for CFDI PDF library."""

import logging
from collections.abc import Callable
from pathlib import Path
from typing import NamedTuple

from .exceptions import CFDIPDFError
from .models import CFDI
from .parser import CFDIParser
from .qr import SATQRGenerator
from .render import RenderEngine, TemplateManager

logger = logging.getLogger(__name__)

# Callable invocado tras cada render con (cfdi, output) donde output es la ruta
# del PDF o el nombre de archivo si no se escribió a disco.
RenderHook = Callable[[CFDI, str], None]


class BatchResult(NamedTuple):
    """Resultado de procesar un archivo en ``render_batch``."""

    source: Path
    output: Path | None
    error: str | None


def _render_one(args: tuple[Path, str | Path | None, str | None, str | Path | None]) -> BatchResult:
    """Worker para el modo paralelo de ``render_batch`` (pickleable)."""
    xml_path, output_dir, template, logo_path = args
    try:
        pdf = CFDIPDF(
            template=template or "minimal",
            max_xml_size=None,
        )
        output = pdf.render(
            xml_path=xml_path,
            output_dir=output_dir,
            template=template,
            logo_path=logo_path,
        )
        return BatchResult(xml_path, output, None)
    except Exception as exc:  # un error por archivo no aborta el lote
        return BatchResult(xml_path, None, str(exc))


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
        custom_template_paths: list[str | Path] | None = None,
        validate_xsd: bool = False,
        validate_catalogs: bool = False,
        max_xml_size: int | None = 10_000_000,
        on_render: RenderHook | None = None,
    ) -> None:
        """
        Initialize CFDIPDF converter.

        Args:
            template: Default template name (e.g., "minimal")
            custom_template_paths: Additional paths to search for templates
            validate_xsd: If True, validate the CFDI against the official SAT
                XSD schema (cfdv40.xsd) during parsing.
            validate_catalogs: If True, validate the SAT catalog keys (moneda,
                régimen fiscal, uso CFDI, impuestos, etc.) during parsing.
            max_xml_size: Maximum XML size in bytes (default 10 MB). None
                disables the limit.
            on_render: Callable ``(cfdi, output)`` invocado tras cada render
                exitoso; ``output`` es la ruta del PDF o el nombre de archivo.
        """
        self._template = template
        self._on_render = on_render

        self._parser = CFDIParser(
            validate_xsd=validate_xsd,
            validate_catalogs=validate_catalogs,
            max_xml_size=max_xml_size,
        )
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
            self._notify_render(cfdi, str(output_path))
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
            self._notify_render(cfdi, str(output_path))
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
            self._notify_render(cfdi, filename)
            return pdf_bytes, filename

        except CFDIPDFError:
            raise
        except Exception as exc:
            raise CFDIPDFError(f"Failed to render PDF: {exc}") from exc

    def render_bytes_from_string(
        self,
        xml_content: str,
        template: str | None = None,
        logo_path: str | Path | None = None,
    ) -> tuple[bytes, str]:
        """
        Render CFDI XML string to PDF bytes without writing to disk.

        Args:
            xml_content: XML content as string
            template: Template name (overrides default)
            logo_path: Path to logo image (optional)

        Returns:
            Tuple of (pdf_bytes, uuid_filename) where uuid_filename is
            the recommended filename, e.g. ``"a1b2c3...-uuid.pdf"``.

        Raises:
            CFDIPDFError: If rendering fails
        """
        try:
            logger.info("Parsing XML string")
            cfdi = self._parser.parse_string(xml_content)

            template_name = template or self._template
            pdf_bytes = self._render_engine.render(
                cfdi=cfdi,
                template_name=template_name,
                output_path=None,
                logo_path=logo_path,
            )

            filename = self._uuid_filename(cfdi)
            self._notify_render(cfdi, filename)
            return pdf_bytes, filename

        except CFDIPDFError:
            raise
        except Exception as exc:
            raise CFDIPDFError(f"Failed to render PDF: {exc}") from exc

    def render_batch(
        self,
        xml_paths: list[str | Path],
        output_dir: str | Path | None = None,
        template: str | None = None,
        logo_path: str | Path | None = None,
        workers: int | None = None,
    ) -> list[BatchResult]:
        """
        Render multiple XML files, reusing this instance.

        En modo secuencial (``workers`` ≤ 1 o None) se reutiliza la misma
        instancia (templates y recursos compilados una sola vez). Con
        ``workers`` > 1 se procesa en paralelo con ``ProcessPoolExecutor``
        (WeasyPrint no es thread-safe, pero sí multiproceso).

        Args:
            xml_paths: Lista de rutas de CFDI XML.
            output_dir: Directorio de salida (por defecto, el de cada XML).
            template: Template a usar (por defecto, el de la instancia).
            logo_path: Logo a usar en todos.
            workers: Número de procesos (None/1 = secuencial).

        Returns:
            Lista de ``BatchResult`` con (source, output | None, error | None).
        """
        paths = [Path(p) for p in xml_paths]

        if workers is None or workers <= 1:
            results: list[BatchResult] = []
            for source in paths:
                try:
                    output = self.render(
                        xml_path=source,
                        output_dir=output_dir,
                        template=template,
                        logo_path=logo_path,
                    )
                    results.append(BatchResult(source, output, None))
                except Exception as exc:  # un error no aborta el lote
                    results.append(BatchResult(source, None, str(exc)))
            return results

        from concurrent.futures import ProcessPoolExecutor

        tasks = [(source, output_dir, template, logo_path) for source in paths]
        with ProcessPoolExecutor(max_workers=workers) as executor:
            return list(executor.map(_render_one, tasks))

    def parse(self, xml_path: str | Path) -> CFDI:
        """Parse CFDI XML file without rendering."""
        return self._parser.parse_file(xml_path)

    def parse_string(self, xml_content: str) -> CFDI:
        """Parse CFDI XML string without rendering."""
        return self._parser.parse_string(xml_content)

    def list_templates(self) -> list[str]:
        """List all available templates."""
        return self._template_manager.list_templates()

    def ensure_resources(self, all_resources: bool = False) -> None:
        """
        Predescarga los recursos oficiales del SAT (XSLT de la cadena original
        y, opcionalmente, los XSD de validación).

        Útil para entornos sin red o deploys: una vez descargados, quedan
        cacheados en disco y la biblioteca funciona offline.

        Args:
            all_resources: si es True, también descarga los esquemas XSD
                (incluye el catálogo catCFDI.xsd, ~6 MB).
        """
        from .sat.resources import XSD_RESOURCES, XSLT_RESOURCES, get_manager

        manager = get_manager()
        manager.ensure_many(XSLT_RESOURCES)
        if all_resources:
            manager.ensure_many(XSD_RESOURCES)

    def set_template(self, template: str) -> None:
        """Set default template."""
        self._template = template

    def get_template(self) -> str:
        """Get current default template."""
        return self._template

    def set_render_hook(self, on_render: RenderHook | None) -> None:
        """Set (or clear with None) the post-render hook."""
        self._on_render = on_render

    # ── private helpers ───────────────────────────────────────────────────────

    def _notify_render(self, cfdi: CFDI, output: str) -> None:
        """Invoca el hook post-render si está configurado."""
        if self._on_render is not None:
            self._on_render(cfdi, output)

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
