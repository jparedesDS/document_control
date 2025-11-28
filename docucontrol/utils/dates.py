from __future__ import annotations

from datetime import datetime


def today() -> datetime:
    return datetime.now()


def format_date(dt: datetime, fmt: str = "%d-%m-%Y") -> str:
    return dt.strftime(fmt)

