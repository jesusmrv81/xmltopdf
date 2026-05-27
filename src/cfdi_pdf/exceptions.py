"""Custom exceptions for CFDI PDF library."""

from typing import Any


class CFDIPDFError(Exception):
    """Base exception for all CFDI PDF errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


class InvalidCFDIError(CFDIPDFError):
    """Raised when CFDI XML structure is invalid or incomplete."""

    pass


class InvalidSATQRError(CFDIPDFError):
    """Raised when SAT QR code generation fails or parameters are invalid."""

    pass


class TemplateRenderError(CFDIPDFError):
    """Raised when template rendering fails."""

    pass


class XMLParseError(CFDIPDFError):
    """Raised when XML parsing fails due to malformed XML or security issues."""

    pass


class UTF8SanitizationError(CFDIPDFError):
    """Raised when UTF-8 sanitization encounters unrecoverable characters."""

    pass


class TemplateNotFoundError(CFDIPDFError):
    """Raised when requested template does not exist."""

    pass


class PDFGenerationError(CFDIPDFError):
    """Raised when PDF generation fails."""

    pass
