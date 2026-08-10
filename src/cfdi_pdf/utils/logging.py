"""Logging estructurado (JSON) para entornos de servicio.

Permite emitir los logs de la biblioteca como una línea JSON por evento,
listos para ser ingeridos por sistemas de monitoreo (CloudWatch, Datadog,
Loki, etc.).
"""

import json
import logging
import time


class JsonFormatter(logging.Formatter):
    """Formatea cada registro como una línea JSON."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(record.created)),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def setup_json_logging(level: int = logging.INFO, logger_name: str = "cfdi_pdf") -> None:
    """
    Configura el logger (por defecto ``cfdi_pdf``) para emitir JSON a stdout.

    Reemplaza los handlers existentes del logger indicado y desactiva la
    propagación, de modo que solo se emitan eventos JSON.
    """
    logger = logging.getLogger(logger_name)
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logger.handlers = [handler]
    logger.propagate = False
    logger.setLevel(level)
