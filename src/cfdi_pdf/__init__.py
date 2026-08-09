"""CFDI PDF - Professional CFDI 4.0 XML to PDF converter for Mexico SAT."""

from importlib.metadata import PackageNotFoundError, version

from .api import CFDIPDF
from .crypto import SelloVerifier
from .exceptions import (
    CFDIPDFError,
    InvalidCFDIError,
    InvalidSATQRError,
    PDFGenerationError,
    TemplateNotFoundError,
    TemplateRenderError,
    UTF8SanitizationError,
    XMLParseError,
)

try:
    __version__ = version("cfdi-pdf")
except PackageNotFoundError:  # pragma: no cover - package not installed
    __version__ = "0.0.0+dev"

__all__ = [
    "CFDIPDF",
    "CFDIPDFError",
    "InvalidCFDIError",
    "InvalidSATQRError",
    "PDFGenerationError",
    "SelloVerifier",
    "TemplateNotFoundError",
    "TemplateRenderError",
    "UTF8SanitizationError",
    "XMLParseError",
]
