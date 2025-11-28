from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from docucontrol.config import settings
from docucontrol.core.exceptions import DataSourceNotFound
from docucontrol.core.models import ReclamationEmail
from docucontrol.infra.email.html_table import dataframe_to_highlighted_html
from docucontrol.utils.dates import format_date, today

log = logging.getLogger(__name__)


@dataclass(slots=True)
class ReclamationsConfig:
    monitoring_report_path: Path | None = None


class ReclamationsService:
    def __init__(self, config: ReclamationsConfig | None = None):
        self.config = config or ReclamationsConfig()

    def _resolve_report_path(self, reference_date: str | None = None) -> Path:
        if self.config.monitoring_report_path:
            return self.config.monitoring_report_path
        date_str = reference_date or format_date(today())
        filename = settings.monitoring_report_name.format(date=date_str)
        path = settings.output_dir / filename
        if not path.exists():
            raise DataSourceNotFound(f"No se encontró el monitoring report en {path}")
        return path

    def generate_emails(self, reference_date: str | None = None) -> list[ReclamationEmail]:
        report_path = self._resolve_report_path(reference_date)
        log.info("Cargando ENVIADOS desde %s", report_path)
        df = pd.read_excel(report_path, sheet_name="ENVIADOS")
        df = df[df.get("Días Devolución", 0) >= 0].copy()
        drop_cols = [
            "Responsable",
            "Nº Oferta",
            "Fecha Pedido",
            "Cliente",
            "Fecha Prevista",
            "Info/Review",
            "Repsonsable",
            "Días Envío",
            "Material",
            "Tipo Doc.",
            "Crítico",
            "Fecha INICIAL",
            "Fecha FIN",
            "Reclamaciones",
            "Seguimiento",
            "Historial Rev.",
        ]
        df.drop(columns=[c for c in drop_cols if c in df.columns], inplace=True, errors="ignore")
        df.reset_index(drop=True, inplace=True)
        df["Prefijo Pedido"] = df["Nº Pedido"].astype(str).str.extract(r"^(P-\d+/\d+)", expand=False)

        if "Nº Revisión" in df.columns:
            df["Nº Revisión"] = df["Nº Revisión"].apply(lambda x: int(x) if pd.notnull(x) else "")
        if "Fecha Env. Doc." in df.columns:
            df["Fecha Env. Doc."] = pd.to_datetime(df["Fecha Env. Doc."], errors="coerce").dt.strftime("%d-%m-%Y")
        if "Estado" in df.columns:
            df["Estado"] = df["Estado"].replace({"Enviado": "Submitted"})

        rename_dict = {
            "Nº Pedido": "Order No.",
            "Nº PO": "PO No.",
            "Nº Doc. Cliente": "Client Doc. No.",
            "Nº Doc. EIPSA": "EIPSA Doc. No.",
            "Título": "Title",
            "Estado": "Status",
            "Nº Revisión": "Revision No.",
            "Fecha Env. Doc.": "Doc. Sent Date",
            "Días Devolución": "Return Days",
        }
        df.rename(columns=rename_dict, inplace=True)

        emails: list[ReclamationEmail] = []
        for prefijo, grupo in df.groupby("Prefijo Pedido"):
            if prefijo is None:
                continue
            grupo = grupo.sort_values(by="Return Days", ascending=False).drop(columns=["Prefijo Pedido"])
            html_table = dataframe_to_highlighted_html(grupo)
            po = grupo["PO No."].iloc[0] if "PO No." in grupo.columns and not grupo["PO No."].isnull().all() else "N/A"
            subject = f"RECLAIMS: {prefijo} / PO: {po} // DOC. UNDER REVIEW"
            body = (
                "<p>Dear All,</p>"
                "<p>- The following documents have been sent pending review and have not yet been returned by the customer:</p>"
                f"{html_table}"
                "<p>If you can tell us the resolution of these documents and when they are expected to be returned by the customer, I would appreciate it.</p>"
            )
            emails.append(
                ReclamationEmail(
                    prefix=prefijo,
                    po_number=str(po),
                    subject=subject,
                    html_body=body,
                    dataframe=grupo,
                    recipients=[],
                )
            )
        return emails

    @staticmethod
    def send_via_outlook(emails: list[ReclamationEmail]) -> None:
        try:
            import win32com.client as win32  # pragma: no cover
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("pywin32 no está instalado para automatizar Outlook") from exc

        outlook = win32.Dispatch("outlook.application")
        for email in emails:
            mail = outlook.CreateItem(0)
            mail.Subject = email.subject
            mail.HTMLBody = email.html_body + mail.HTMLBody
            mail.Display()

