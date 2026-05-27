"""Command-line interface for CFDI PDF."""

import argparse
import logging
import sys
from pathlib import Path

from .api import CFDIPDF
from .exceptions import CFDIPDFError

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False) -> None:
    """Configure logging."""
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))

    if verbose:
        logging.root.setLevel(logging.DEBUG)
        console_handler.setLevel(logging.DEBUG)
    else:
        logging.root.setLevel(logging.WARNING)
        console_handler.setLevel(logging.WARNING)

        app_logger = logging.getLogger("cfdi_pdf")
        app_logger.setLevel(logging.INFO)
        app_logger.addHandler(console_handler)
        app_logger.propagate = False

    logging.root.addHandler(console_handler)


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="cfdi-pdf",
        description="Convierte archivos CFDI 4.0 XML a PDF (tamaño carta). "
        "El PDF generado siempre se nombra con el UUID del timbre fiscal.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  # Un archivo — guarda {uuid}.pdf en el mismo directorio que el XML
  cfdi-pdf factura.xml

  # Varios archivos
  cfdi-pdf enero/*.xml

  # Directorio de salida personalizado
  cfdi-pdf factura.xml --output-dir ./pdfs

  # Con logo y template
  cfdi-pdf factura.xml --template corporativo --logo logo.png
        """,
    )

    parser.add_argument(
        "files",
        nargs="+",
        type=Path,
        metavar="XML",
        help="Archivo(s) CFDI XML a convertir",
    )

    parser.add_argument(
        "-t",
        "--template",
        default="minimal",
        help="Nombre del template (default: minimal)",
    )

    parser.add_argument(
        "-l",
        "--logo",
        type=Path,
        help="Ruta a imagen de logotipo (PNG, JPG o SVG)",
    )

    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        help="Directorio donde se guardarán los PDFs. "
        "Por defecto se usa el mismo directorio del XML.",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Activar salida detallada",
    )

    parser.add_argument(
        "--list-templates",
        action="store_true",
        help="Listar templates disponibles y salir",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0",
    )

    args = parser.parse_args()
    setup_logging(args.verbose)

    # ── --list-templates ──────────────────────────────────────────────────────
    if args.list_templates:
        converter = CFDIPDF()
        print("Templates disponibles:")
        for tmpl in converter.list_templates():
            print(f"  - {tmpl}")
        return 0

    xml_files: list[Path] = args.files

    # ── initialize converter ──────────────────────────────────────────────────
    try:
        converter = CFDIPDF(template=args.template)
    except Exception as exc:
        logger.error("No se pudo inicializar el convertidor: %s", exc)
        return 1

    # ── process files ─────────────────────────────────────────────────────────
    success_count = 0
    error_count = 0

    for xml_file in xml_files:
        try:
            output_path = converter.render(
                xml_path=xml_file,
                output_dir=args.output_dir,
                logo_path=args.logo,
            )
            print(f"✓ {xml_file.name} → {output_path}")
            success_count += 1

        except CFDIPDFError as exc:
            logger.error("Error al convertir %s: %s", xml_file, exc)
            error_count += 1
        except Exception as exc:
            logger.error("Error inesperado al convertir %s: %s", xml_file, exc)
            error_count += 1

    if len(xml_files) > 1:
        print(f"\nConvertidos: {success_count}  Fallidos: {error_count}")

    return 0 if error_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
