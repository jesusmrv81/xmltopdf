"""Tests para el logging estructurado (JSON)."""

import io
import json
import logging

import pytest

from cfdi_pdf.utils.logging import JsonFormatter, setup_json_logging


class TestJsonFormatter:
    """Test suite para JsonFormatter."""

    def test_format_returns_json(self) -> None:
        record = logging.LogRecord(
            "cfdi_pdf.api", logging.INFO, "api.py", 1, "hello %s", ("mundo",), None
        )
        out = JsonFormatter().format(record)

        payload = json.loads(out)
        assert payload["level"] == "INFO"
        assert payload["logger"] == "cfdi_pdf.api"
        assert payload["message"] == "hello mundo"
        assert "ts" in payload


class TestSetupJsonLogging:
    """Test suite para setup_json_logging."""

    def test_emits_json_to_stream(self, capsys: pytest.CaptureFixture[str]) -> None:
        setup_json_logging(level=logging.INFO)
        logging.getLogger("cfdi_pdf.test").info("evento de prueba")

        captured = capsys.readouterr().err
        assert captured
        payload = json.loads(captured.splitlines()[-1])
        assert payload["message"] == "evento de prueba"
        assert payload["level"] == "INFO"

    def test_format_exception(self) -> None:
        stream = io.StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(JsonFormatter())
        logger = logging.getLogger("cfdi_pdf.exc_test")
        logger.handlers = [handler]
        logger.propagate = False

        try:
            raise ZeroDivisionError("división por cero")
        except ZeroDivisionError:
            logger.exception("falló la división")

        payload = json.loads(stream.getvalue().strip())
        assert "exception" in payload
