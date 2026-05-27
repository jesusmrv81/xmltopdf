"""Command-line interface for CFDI PDF."""

import argparse
import logging
import sys
from pathlib import Path

from .api import CFDIPDF
from .exceptions import CFDIPDFError


def setup_logging(verbose: bool = False) -> None:
    """Configure logging."""
    # Create a handler for console output
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    
    if verbose:
        # In verbose mode, show everything
        logging.root.setLevel(logging.DEBUG)
        console_handler.setLevel(logging.DEBUG)
    else:
        # In normal mode, silence root logger (used by dependencies)
        logging.root.setLevel(logging.WARNING)
        console_handler.setLevel(logging.WARNING)
        
        # But show our app's INFO messages
        app_logger = logging.getLogger("cfdi_pdf")
        app_logger.setLevel(logging.INFO)
        app_logger.addHandler(console_handler)
        app_logger.propagate = False
    
    logging.root.addHandler(console_handler)


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="cfdi-pdf",
        description="Convert CFDI 4.0 XML files to PDF",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  cfdi-pdf factura.xml factura.pdf
  cfdi-pdf factura.xml --template minimal
  cfdi-pdf *.xml --output-dir ./pdfs
  cfdi-pdf factura.xml --logo logo.png
        """,
    )

    parser.add_argument(
        "files",
        nargs="+",
        type=Path,
        help="CFDI XML file(s) to convert, optionally followed by output PDF path",
    )

    parser.add_argument(
        "-t",
        "--template",
        default="minimal",
        help="Template name (default: minimal)",
    )

    parser.add_argument(
        "-l",
        "--logo",
        type=Path,
        help="Path to logo image",
    )

    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        help="Output directory for batch conversion",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    parser.add_argument(
        "--list-templates",
        action="store_true",
        help="List available templates",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0",
    )

    args = parser.parse_args()

    setup_logging(args.verbose)

    # Handle --list-templates
    if args.list_templates:
        converter = CFDIPDF()
        templates = converter.list_templates()
        print("Available templates:")
        for template in templates:
            print(f"  - {template}")
        return 0

    # Separate XML files from output PDF
    # If last file is .pdf, treat it as output
    all_files = args.files
    output_path = None
    
    if len(all_files) > 1 and all_files[-1].suffix.lower() == ".pdf":
        output_path = all_files[-1]
        xml_files = all_files[:-1]
    else:
        xml_files = all_files
    
    if not xml_files:
        parser.error("At least one XML file is required")

    # Validate arguments
    if len(xml_files) > 1 and not args.output_dir and output_path:
        parser.error("For multiple files, use --output-dir instead of specifying a single PDF output")

    # Determine output mode
    single_file = len(xml_files) == 1 and not args.output_dir
    output_dir = args.output_dir or (output_path if output_path and output_path.is_dir() else None)

    # Initialize converter
    try:
        converter = CFDIPDF(template=args.template)
    except Exception as e:
        logging.error(f"Failed to initialize converter: {e}")
        return 1

    # Process files
    success_count = 0
    error_count = 0

    for xml_file in xml_files:
        try:
            # Determine output path
            if single_file and output_path and not output_path.is_dir():
                final_output_path = output_path
            elif output_dir:
                output_dir.mkdir(parents=True, exist_ok=True)
                final_output_path = output_dir / f"{xml_file.stem}.pdf"
            else:
                final_output_path = xml_file.with_suffix(".pdf")

            # Convert
            logging.info(f"Converting: {xml_file} -> {final_output_path}")
            converter.render(
                xml_path=xml_file,
                output=final_output_path,
                logo_path=args.logo,
            )

            print(f"✓ {xml_file.name} -> {final_output_path.name}")
            success_count += 1

        except CFDIPDFError as e:
            logging.error(f"Failed to convert {xml_file}: {e}")
            error_count += 1
        except Exception as e:
            logging.error(f"Unexpected error converting {xml_file}: {e}")
            error_count += 1

    # Summary
    if len(xml_files) > 1:
        print(f"\nConverted: {success_count}, Failed: {error_count}")

    return 0 if error_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
