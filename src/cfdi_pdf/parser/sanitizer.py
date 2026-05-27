"""UTF-8 and XML sanitization utilities."""

import logging
import re
import typing
from typing import Any

logger = logging.getLogger(__name__)

# Matches characters that are NOT valid in XML 1.0:
# Valid ranges: U+0009, U+000A, U+000D, U+0020-U+D7FF, U+E000-U+FFFD, U+10000-U+10FFFF
_INVALID_XML_CHARS: re.Pattern[str] = re.compile(
    r"[^\u0009\u000A\u000D\u0020-\uD7FF\uE000-\uFFFD\U00010000-\U0010FFFF]"
)


class XMLSanitizer:
    """Sanitizes XML content for UTF-8 compliance and proper escaping."""

    # XML escape mappings
    _XML_ESCAPES: typing.ClassVar[dict[str, str]] = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&apos;",
    }

    @classmethod
    def sanitize_text(cls, text: str) -> str:
        """
        Sanitize text for XML compliance.

        - Removes invalid XML 1.0 characters via compiled regex (O(n) single pass)
        - Logs a warning with count when invalid characters are removed
        - Preserves valid Unicode (accents, ñ, emojis — with a warning)

        Args:
            text: Input text to sanitize

        Returns:
            Sanitized text
        """
        if not text:
            return text

        # Warn about emojis (U+10000+) before removal check — they ARE valid XML
        if any(ord(ch) > 0xFFFF for ch in text):
            logger.warning(
                "Text contains emoji/supplementary characters. "
                "Allowed by XML 1.0 but not recommended for SAT."
            )

        # Single-pass removal of invalid characters
        sanitized, count = _INVALID_XML_CHARS.subn("", text)

        if count:
            logger.warning("Removed %d invalid XML character(s)", count)

        return sanitized

    @classmethod
    def escape_xml(cls, text: str) -> str:
        """
        Escape special XML characters.

        Converts: & < > " ' to their XML entity equivalents.

        Args:
            text: Input text to escape

        Returns:
            Escaped text
        """
        if not text:
            return text

        # First sanitize
        text = cls.sanitize_text(text)

        # Then escape XML special characters
        for char, entity in cls._XML_ESCAPES.items():
            text = text.replace(char, entity)

        return text

    @classmethod
    def unescape_xml(cls, text: str) -> str:
        """
        Unescape XML entities back to characters.

        Args:
            text: Text with XML entities

        Returns:
            Unescaped text
        """
        if not text:
            return text

        # Reverse the escaping
        for char, entity in cls._XML_ESCAPES.items():
            text = text.replace(entity, char)

        return text

    @classmethod
    def sanitize_dict(cls, data: dict[str, Any]) -> dict[str, Any]:
        """
        Recursively sanitize all string values in a dictionary.

        Args:
            data: Dictionary with string values

        Returns:
            Dictionary with sanitized values
        """
        sanitized: dict[str, Any] = {}

        for key, value in data.items():
            if isinstance(value, str):
                sanitized[key] = cls.sanitize_text(value)
            elif isinstance(value, dict):
                sanitized[key] = cls.sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    cls.sanitize_dict(item) if isinstance(item, dict) else item for item in value
                ]
            else:
                sanitized[key] = value

        return sanitized
