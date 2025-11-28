from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict

import pandas as pd

from docucontrol.config import settings
from docucontrol.core.exceptions import InvalidDataset, ReportGenerationError
from docucontrol.core.models import MonitoringDatasets, MonitoringReportResult
from docucontrol.infra.integrations.erp_repository import ERPRepository
from docucontrol.infra.io.excel_writer import ExcelReportWriter
from docucontrol.infra.io.excel_styles import MonitoringReportStyler
from docucontrol.utils.dates import today, format_date


@dataclass(slots=True)
class MonitoringReportSheets:
    envio: pd.DataFrame
    devoluciones: pd.DataFrame
    criticos: pd.DataFrame
    criticos_mas15: pd.DataFrame
    sin_envio: pd.DataFrame
    total: pd.DataFrame
    status_global: pd.DataFrame

    def as_mapping(self) -> Dict[str, pd.DataFrame]:
        return {
            "ENVIADOS": self.envio,
            "DEVOLUCIONES": self.devoluciones,
            "CRÍTICOS": self.criticos,
            "CRÍTICOS +15d": self.criticos_mas15,
            "SIN ENVIAR": self.sin_envio,
            "ALL DOC.": self.total,
            "STATUS GLOBAL": self.status_global,
        }


class MonitoringReportService:
    def __init__(
        self,
        repository: ERPRepository | None = None,
        writer: ExcelReportWriter | None = None,
        styler: MonitoringReportStyler | None = None,
    ):
        self.repository = repository or ERPRepository()
        self.writer = writer or ExcelReportWriter()
        self.styler = styler or MonitoringReportStyler()

    def run(self, reference_date: datetime | None = None) -> MonitoringReportResult:
        reference_date = reference_date or today()
        datasets = self.repository.load_monitoring_datasets()
        sheets = self._build_sheets(datasets, reference_date)
        filename = settings.monitoring_report_name.format(date=format_date(reference_date))
        output_path = self.writer.write(sheets.as_mapping(), filename)
        try:
            self.styler.apply(output_path)
        except Exception as exc:  # pragma: no cover
            raise ReportGenerationError(str(exc)) from exc
        return MonitoringReportResult(output_path=output_path, generated_at=reference_date)

    def _build_sheets(self, data: MonitoringDatasets, reference_date: datetime) -> MonitoringReportSheets:
        erp_data = data.erp_data.copy()
        total_df = data.erp_data.copy()
        consulta = data.consulta_data.copy()

        cols_to_add = ["Nº Pedido", "Responsable", "Nº Oferta"]
        missing = [col for col in cols_to_add if col not in consulta.columns]
        if missing:
            raise InvalidDataset(f"Faltan columnas en consulta ERP: {missing}")

        erp_data = erp_data.merge(consulta[cols_to_add], on="Nº Pedido", how="left")
        total_df = total_df.merge(consulta[cols_to_add], on="Nº Pedido", how="left")

        erp_data["Estado"] = erp_data["Estado"].fillna("Sin Enviar")
        total_df["Estado"] = total_df["Estado"].fillna("Sin Enviar")

        erp_data = erp_data[erp_data["Estado"] != "Eliminado"].copy()
        total_df = total_df[total_df["Estado"] != "Eliminado"].copy()

        for df in (erp_data, total_df):
            if "Nº Doc. EIPSA" in df.columns:
                df.drop(df[df["Nº Doc. EIPSA"].astype(str).str.contains("-BIS", na=False)].index, inplace=True)

        date_columns = ["Fecha", "Fecha Pedido", "Fecha Prevista", "Fecha Fabricación", "Fecha Montaje", "Fecha Envío"]
        for df in (erp_data, total_df, consulta):
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors="coerce", dayfirst=True)

        df_comentados = erp_data[erp_data["Estado"].isin(["Com. Menores", "Com. Mayores", "Rechazado", "Comentado"])].copy()
        df_envio = erp_data[erp_data["Estado"] == "Enviado"].copy()
        df_sin_envio = erp_data[erp_data["Estado"] == "Sin Enviar"].copy()
        df_criticos = erp_data[
            (erp_data.get("Crítico") == "Sí") & (~erp_data["Estado"].isin(["Eliminado", "Aprobado", "Enviado"]))
        ].copy()

        self._calculate_days(df_comentados, reference_date, "Fecha")
        self._calculate_days(df_envio, reference_date, "Fecha")
        self._calculate_days(df_criticos, reference_date, "Fecha")
        self._calculate_days(df_sin_envio, reference_date, "Fecha Pedido")

        df_comentados = self._rename_column(df_comentados, "Fecha", "Fecha Dev. Doc.")
        df_envio = self._rename_column(df_envio, "Fecha", "Fecha Env. Doc.")
        df_criticos = self._rename_column(df_criticos, "Fecha", "Fecha Doc.")
        total_df = self._rename_column(total_df, "Fecha", "Fecha Doc.")
        df_sin_envio = self._rename_column(df_sin_envio, "Fecha", "Fecha Doc.")

        df_comentados.insert(12, "Notas", df_comentados["Fecha Dev. Doc."])
        mask = df_comentados["Estado"].isin(["Rechazado", "Com. Menores", "Com. Mayores", "Comentado"])
        df_comentados.loc[mask, "Notas"] = (
            "Enviar antes del " + (df_comentados.loc[mask, "Notas"] + pd.to_timedelta(15, unit="D")).dt.strftime("%d-%m-%Y")
        )

        status_global = (
            erp_data.groupby(["Nº Pedido", "Estado"])
            .size()
            .unstack(fill_value=0)
            .reset_index()
        )
        if "Eliminado" in status_global.columns:
            status_global.drop(columns="Eliminado", inplace=True)
        for col in ["Aprobado", "Com. Mayores", "Com. Menores", "Enviado", "Rechazado", "Sin Enviar"]:
            if col not in status_global.columns:
                status_global[col] = 0
        status_global["Total"] = status_global.iloc[:, 1:].sum(axis=1)
        status_global["% Completado"] = (status_global["Aprobado"] / status_global["Total"] * 100).fillna(0).round(2)
        status_global = status_global[status_global["% Completado"] != 100]

        for df in (total_df, df_envio, df_comentados, df_criticos, df_sin_envio):
            if "Nº Pedido" in df.columns:
                df.sort_values(by="Nº Pedido", ascending=False, inplace=True, na_position="last")

        column_order = [
            "Nº Pedido",
            "Responsable",
            "Nº Oferta",
            "Nº PO",
            "Cliente",
            "Material",
            "Fecha Pedido",
            "Fecha Prevista",
            "Nº Doc. Cliente",
            "Nº Doc. EIPSA",
            "Título",
            "Tipo Doc.",
            "Info/Review",
            "Repsonsable",
            "Días Envío",
            "Crítico",
            "Estado",
            "Notas",
            "Nº Revisión",
            "Fecha Doc.",
            "Fecha Env. Doc.",
            "Fecha Dev. Doc.",
            "Días Devolución",
            "Reclamaciones",
            "Seguimiento",
            "Historial Rev.",
        ]

        df_total = self._reorder_columns(total_df, column_order)
        df_envio = self._reorder_columns(df_envio, column_order)
        df_comentados = self._reorder_columns(df_comentados, column_order)
        df_criticos = self._reorder_columns(df_criticos, column_order)
        df_sin_envio = self._reorder_columns(df_sin_envio, column_order)

        df_criticos_menor15 = df_criticos[
            (df_criticos["Días Devolución"] <= 15) | (df_criticos["Días Devolución"].isna())
        ].copy()
        df_criticos_mas15 = df_criticos[df_criticos["Días Devolución"] > 15].copy()

        return MonitoringReportSheets(
            envio=df_envio,
            devoluciones=df_comentados,
            criticos=df_criticos_menor15,
            criticos_mas15=df_criticos_mas15,
            sin_envio=df_sin_envio,
            total=df_total,
            status_global=status_global,
        )

    @staticmethod
    def _calculate_days(df: pd.DataFrame, reference_date: datetime, column: str) -> None:
        if column in df.columns:
            df["Días Devolución"] = (reference_date - df[column]).dt.days

    @staticmethod
    def _rename_column(df: pd.DataFrame, old: str, new: str) -> pd.DataFrame:
        if old in df.columns:
            df = df.rename(columns={old: new})
        return df

    @staticmethod
    def _reorder_columns(df: pd.DataFrame, order: list[str]) -> pd.DataFrame:
        existing = [col for col in order if col in df.columns]
        remaining = [col for col in df.columns if col not in existing]
        return df[existing + remaining]

