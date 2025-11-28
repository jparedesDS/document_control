from __future__ import annotations

import logging
from logging.config import dictConfig

from .settings import settings


def configure_logging(level: str = "INFO") -> None:
    log_path = settings.tmp_dir / "docucontrol.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {"format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s"},
            },
            "handlers": {
                "console": {"class": "logging.StreamHandler", "formatter": "default", "level": level},
                "file": {
                    "class": "logging.FileHandler",
                    "formatter": "default",
                    "level": level,
                    "filename": str(log_path),
                    "encoding": "utf-8",
                },
            },
            "root": {"handlers": ["console", "file"], "level": level},
        }
    )


configure_logging()

