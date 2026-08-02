"""Centralized structured logging configuration.

Call ``setup_logging()`` once at application startup (in ``main.py``)
to configure all loggers with a consistent format and level.

Format in **production** → JSON lines (one dict per log entry), easy to
ship to any log aggregator (CloudWatch, Datadog, ELK, etc.).

Format in **development** → human-friendly coloured output.
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone

from .config import get_settings


class JSONFormatter(logging.Formatter):
    """Emit each log record as a single JSON object."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info and record.exc_info[0] is not None:
            log_entry["exception"] = self.formatException(record.exc_info)
        # Attach extra structured fields if present
        for key in ("request_id", "method", "path", "status_code", "duration_ms", "user_id"):
            value = getattr(record, key, None)
            if value is not None:
                log_entry[key] = value
        return json.dumps(log_entry, default=str)


_DEV_FORMAT = "%(asctime)s  %(levelname)-8s  %(name)-30s  %(message)s"
_DEV_DATE_FMT = "%H:%M:%S"


def setup_logging() -> None:
    """Configure the root logger based on the current environment."""
    settings = get_settings()

    level = logging.DEBUG if settings.debug else logging.INFO

    root = logging.getLogger()
    root.setLevel(level)

    # Remove any pre-existing handlers (e.g. uvicorn defaults)
    root.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    if settings.environment == "production":
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(logging.Formatter(_DEV_FORMAT, datefmt=_DEV_DATE_FMT))

    root.addHandler(handler)

    # Quieten noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
