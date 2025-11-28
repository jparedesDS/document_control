from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from docucontrol.config import settings
from docucontrol.core.exceptions import DataSourceNotFound
from docucontrol.core.models import OVRReportResult
from docucontrol.infra.io.ovr_styles import OVRExcelStyler
from docucontrol.utils.dates import today, format_date
from docucontrol.utils.paths import ensure_dir

log = logging.getLogger(__name__)


@dataclass(slots=True)
class OVRConfig:
    data_erp_path: Path | None = None
    data_tags_path: Path | None = None
    output_dir: Path | None = None


class OVRReportService:
    def __init__(self, config: OVRConfig | None = None, styler: OVRExcelStyler | None = None):
        self.config = config or OVRConfig()
        self.styler = styler or OVRExcelStyler()

    def _resolve_data_path(self) -> Path:
        path = self.config.data_erp_path or (settings.data_import_dir / "data_erp.xlsx")
        if not path.exists():
            raise DataSourceNotFound(f"No se encontró data_erp en {path}")
        return path

    def _resolve_tags_path(self) -> Path:
        path = self.config.data_tags_path or (settings.data_import_dir / "data_tags.xlsx")
        if not path.exists():
            raise DataSourceNotFound(f"No se encontró data_tags en {path}")
        return path

    def _resolve_output_dir(self) -> Path:
        return ensure_dir(self.config.output_dir or settings.output_dir)

    def _base_dataframe(self) -> pd.DataFrame:
        df = pd.read_excel(self._resolve_data_path())
        df = df[df["Estado"] != "Eliminado"].copy()
        df["Estado"] = df["Estado"].fillna("Sin Enviar")
        df = df.rename(columns={"Fecha": "Fecha Doc.", "Fecha Prevista": "Fecha FIN", "Fecha Pedido": "Fecha INICIAL"})
        for col in ["Fecha Doc.", "Fecha INICIAL", "Fecha FIN"]:
            df[col] = pd.to_datetime(df[col], dayfirst=True, errors="coerce")
        mask_aprobado = df["Estado"] == "Aprobado"
        df.loc[mask_aprobado, "Días Aprobación"] = (
            df.loc[mask_aprobado, "Fecha Doc."] - df.loc[mask_aprobado, "Fecha INICIAL"]
        ).dt.days
        return df

    @staticmethod
    def _historial_columns(df: pd.DataFrame, max_rev: int = 9) -> pd.DataFrame:
        def procesar_historial(historial: str):
            resultados = []
            patron = r"(\d{2}[/-]\d{2}[/-]\d{4})\s*([A-Za-zÁÉÍÓÚáéíóúüÜñÑ.\s]+?)\s*Rev\.?\s*(\d+)"
            matches = re.findall(patron, str(historial))
            for fecha_str, accion, rev_num in matches:
                accion = accion.strip()
                tipo = "Env." if "Enviado" in accion else "Dev."
                try:
                    fecha = pd.to_datetime(fecha_str, dayfirst=True)
                    resultados.append((tipo, int(rev_num), fecha))
                except ValueError:
                    continue
            return resultados

        historial = df["Historial Rev."].apply(procesar_historial)
        cols = []
        for i in range(max_rev + 1):
            cols.extend([f"Env. {i}", f"Dev. {i}"])
        fechas_df = pd.DataFrame("", index=df.index, columns=cols)
        for idx, eventos in historial.items():
            for tipo, rev_num, fecha in eventos:
                col_name = f"{tipo} {rev_num}"
                if col_name in fechas_df.columns:
                    fechas_df.at[idx, col_name] = fecha.strftime("%d-%m-%Y")
        return pd.concat([df, fechas_df], axis=1)

    def generate_simple_report(self) -> OVRReportResult:
        base = self._historial_columns(self._base_dataframe(), max_rev=8)
        df = base.reindex(
            columns=[
                "Nº Pedido",
                "Resp.",
                "Nº PO",
                "Cliente",
                "Material",
                "Nº Doc. Cliente",
                "Nº Doc. EIPSA",
                "Título",
                "Tipo Doc.",
                "Crítico",
                "Estado",
                "Nº Revisión",
                "Fecha INICIAL",
                "Fecha FIN",
                "Fecha Doc.",
                "Días Aprobación",
                "Reclamaciones",
                "Seguimiento",
                "Env. 0",
                "Dev. 0",
                "Env. 1",
                "Dev. 1",
                "Env. 2",
                "Dev. 2",
                "Env. 3",
                "Dev. 3",
                "Env. 4",
                "Dev. 4",
                "Env. 5",
                "Dev. 5",
                "Env. 6",
                "Dev. 6",
                "Env. 7",
                "Dev. 7",
                "Env. 8",
                "Dev. 8",
                "Historial Rev.",
            ]
        )
        df["Tipo Doc."] = df["Tipo Doc."].str.strip()
        df = df.drop(columns=["Seguimiento", "Resp.", "Reclamaciones", "Cliente", "Material", "Crítico"], errors="ignore")
        output = self._resolve_output_dir() / f"OVR_Simple_{format_date(today())}.xlsx"
        self.styler.save(df, str(output))
        return OVRReportResult(output_path=output, generated_at=today())

    def generate_union_report(self) -> OVRReportResult:
        base = self._historial_columns(self._base_dataframe())
        df = base.reindex(
            columns=[
                "Nº Pedido",
                "Resp.",
                "Nº PO",
                "Cliente",
                "Material",
                "Nº Doc. Cliente",
                "Nº Doc. EIPSA",
                "Título",
                "Tipo Doc.",
                "Crítico",
                "Estado",
                "Nº Revisión",
                "Fecha INICIAL",
                "Fecha FIN",
                "Fecha Doc.",
                "Días Aprobación",
                "Reclamaciones",
                "Seguimiento",
                "Env. 0",
                "Dev. 0",
                "Env. 1",
                "Dev. 1",
                "Env. 2",
                "Dev. 2",
                "Env. 3",
                "Dev. 3",
                "Env. 4",
                "Dev. 4",
                "Env. 5",
                "Dev. 5",
                "Env. 6",
                "Dev. 6",
                "Env. 7",
                "Dev. 7",
                "Env. 8",
                "Dev. 8",
                "Env. 9",
                "Dev. 9",
                "Historial Rev.",
            ]
        )
        df["Tipo Doc."] = df["Tipo Doc."].str.strip()
        df = df.drop(columns=["Seguimiento", "Resp.", "Reclamaciones", "Cliente", "Material", "Crítico"], errors="ignore")

        tags = pd.read_excel(self._resolve_tags_path())
        id_vars = [col for col in tags.columns if col not in ["Nº Doc. EIPSA Cálculo", "Nº Doc. EIPSA Plano"]]
        melted = tags.melt(
            id_vars=id_vars,
            value_vars=["Nº Doc. EIPSA Cálculo", "Nº Doc. EIPSA Plano"],
            var_name="Tipo Nº Doc.",
            value_name="Nº Doc. EIPSA Tag",
        )
        melted = melted[melted["Nº Doc. EIPSA Tag"].notna()]
        merge_eipsa = df.merge(melted, left_on="Nº Doc. EIPSA", right_on="Nº Doc. EIPSA Tag", how="left")
        merge_cliente = df.merge(melted, left_on="Nº Doc. Cliente", right_on="Nº Doc. EIPSA Tag", how="left")
        union = pd.concat([merge_eipsa, merge_cliente], ignore_index=True)
        union = union.drop_duplicates(subset=["Nº Doc. EIPSA", "Nº Doc. Cliente"])

        output = self._resolve_output_dir() / f"OVR_Report_Union_{format_date(today())}.xlsx"
        self.styler.save(union, str(output))
        return OVRReportResult(output_path=output, generated_at=today())

