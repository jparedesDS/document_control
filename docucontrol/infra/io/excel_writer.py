from __future__ import annotations

from pathlib import Path
from typing import Mapping

import pandas as pd

from docucontrol.config import settings
from docucontrol.utils.paths import ensure_dir


class ExcelReportWriter:
    def __init__(self, output_dir: Path | None = None):
        self.output_dir = ensure_dir(Path(output_dir or settings.output_dir))

    def write(self, sheets: Mapping[str, pd.DataFrame], filename: str) -> Path:
        output_path = self.output_dir / filename
        with pd.ExcelWriter(output_path, engine="openpyxl", datetime_format="DD/MM/YYYY") as writer:
            for sheet_name, df in sheets.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        return output_path

