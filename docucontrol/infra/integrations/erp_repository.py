from __future__ import annotations

from pathlib import Path

import pandas as pd

from docucontrol.config import settings
from docucontrol.core.exceptions import DataSourceNotFound
from docucontrol.core.models import MonitoringDatasets


class ERPRepository:
    def __init__(self, data_dir: Path | None = None):
        self.data_dir = Path(data_dir or settings.data_import_dir)

    def _read_excel(self, path: Path) -> pd.DataFrame:
        if not path.exists():
            raise DataSourceNotFound(f"No se encontró el archivo requerido: {path}")
        return pd.read_excel(path)

    def load_monitoring_datasets(
        self,
        erp_filename: str = "data_erp.xlsx",
        consulta_filename: str = "consulta_erp.xlsx",
    ) -> MonitoringDatasets:
        erp_df = self._read_excel(self.data_dir / erp_filename)
        consulta_df = self._read_excel(self.data_dir / consulta_filename)
        return MonitoringDatasets(erp_data=erp_df, consulta_data=consulta_df)

