from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List

import pandas as pd


@dataclass(slots=True)
class MonitoringDatasets:
    erp_data: pd.DataFrame
    consulta_data: pd.DataFrame


@dataclass(slots=True)
class MonitoringReportResult:
    output_path: Path
    generated_at: datetime


@dataclass(slots=True)
class ReclamationEmail:
    prefix: str
    po_number: str | None
    subject: str
    html_body: str
    dataframe: pd.DataFrame
    recipients: List[str]


@dataclass(slots=True)
class OVRReportResult:
    output_path: Path
    generated_at: datetime


@dataclass(slots=True)
class ReturnEmailResult:
    subject: str
    summary_path: Path
    transmittal_code: str | None = None

