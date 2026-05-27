"""UTF-8 and XML sanitization utilities."""

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


class XMLSanitizer:
    """Sanitizes XML content for UTF-8 compliance and proper escaping."""

    # Valid XML 1.0 characters
    _VALID_XML_CHARS = re.compile(
        r"^[\u0009\u000A\u000D\u0020-\uD7FF\uE000-\uFFFD\u10000-\u10FFFF]*$"
    )

    # XML escape mappings
    _XML_ESCAPES = {
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

        - Removes invalid XML characters
        - Logs warnings for removed characters
        - Preserves valid Unicode (accents, ñ, emojis with warning)

        Args:
            text: Input text to sanitize

        Returns:
            Sanitized text
        """
        if not text:
            return text

        # Check for emojis (warn but allow)
        if any(ord(char) > 0xFFFF for char in text):
            logger.warning("Text contains emoji characters. Allowed but not recommended for SAT.")

        # Remove invalid XML characters
        sanitized_chars = []
        invalid_count = 0

        for char in text:
            if cls._VALID_XML_CHARS.match(char):
                sanitized_chars.append(char)
            else:
                invalid_count += 1
                logger.warning(f"Removed invalid XML character: U+{ord(char):04X}")

        if invalid_count > 0:
            logger.warning(f"Removed {invalid_count} invalid XML character(s)")

        return "".join(sanitized_chars)

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
        sanitized = {}

        for key, value in data.items():
            if isinstance(value, str):
                sanitized[key] = cls.sanitize_text(value)
            elif isinstance(value, dict):
                sanitized[key] = cls.sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    cls.sanitize_dict(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                sanitized[key] = value

        return sanitized
