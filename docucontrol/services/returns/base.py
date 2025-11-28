from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List

import pandas as pd

from docucontrol.config import settings
from docucontrol.core.models import ReturnEmailResult
from docucontrol.legacy.apply_style_email import (
    aplicar_estilo_info,
    aplicar_estilos_html,
    aplicar_estilos_y_guardar_excel,
)
from docucontrol.legacy.email_identification import email_TO, email_TO_CC
from docucontrol.utils.dates import today
from docucontrol.utils.paths import ensure_dir

log = logging.getLogger(__name__)


@dataclass(slots=True)
class ReturnServiceConfig:
    sender_email: str
    vendor_dir: Path
    combine_filename: str
    summary_prefix: str


class BaseReturnService:
    def __init__(self, config: ReturnServiceConfig):
        self.config = config
        self.vendor_dir = ensure_dir(config.vendor_dir)
        self.combine_path = self.vendor_dir / config.combine_filename
        self.daily_dir = ensure_dir(self.vendor_dir / today().strftime("%d-%m-%Y"))

    def run(self) -> List[ReturnEmailResult]:
        try:
            import win32com.client as win32  # pragma: no cover
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("pywin32 es requerido para procesar correos de devoluciones") from exc

        namespace = win32.Dispatch("Outlook.Application").GetNamespace("MAPI")
        inbox = namespace.GetDefaultFolder(6)
        messages = inbox.Items.Restrict("[Unread]=true")
        messages.Sort("ReceivedTime", True)

        results: List[ReturnEmailResult] = []
        message = messages.GetFirst()
        while message:
            sender = self._get_sender_email(message)
            if sender != self.config.sender_email.lower():
                message = messages.GetNext()
                continue
            try:
                result = self._process_message(message)
                if result:
                    results.append(result)
            except Exception as exc:  # pragma: no cover
                log.exception("Error procesando mensaje %s: %s", getattr(message, "Subject", ""), exc)
            message = messages.GetNext()
        return results

    def _process_message(self, message) -> ReturnEmailResult | None:  # pragma: no cover
        received_time = message.ReceivedTime.strftime("%d-%m-%Y %H:%M:%S")
        subject = self._sanitize_subject(message.Subject)
        transmittal = self.extract_transmittal_code(message.Subject)
        dataframe = self.parse_html_table(message.HTMLBody)
        df_final, df_import, responsibles = self.transform_dataframe(dataframe, message.Subject, received_time, transmittal)

        summary_name = f"RESUMEN - {subject}.xlsx"
        summary_path = self.daily_dir / summary_name
        aplicar_estilos_y_guardar_excel(df_final, summary_path)

        df_body = df_import.drop(columns=[c for c in ["Nº Pedido", "Supp.", "PO", "Fecha"] if c in df_import.columns])
        df_body_html = aplicar_estilos_html(df_body)
        df_info = pd.DataFrame(
            {
                df_final["Cliente"].iloc[0]: ["Nº Pedido", "Supp.", "PO", "Fecha"],
                df_final["Material"].iloc[0]: [
                    df_import["Nº Pedido"].iloc[0],
                    df_import["Supp."].iloc[0],
                    df_import["PO"].iloc[0],
                    df_import["Fecha"].iloc[0],
                ],
            }
        )
        df_info_html = aplicar_estilo_info(df_info)
        body = df_info_html + df_body_html
        self._send_outlook_mail(
            subject=f"DEV: {df_final['Nº Pedido'].iloc[0]} [{subject}]",
            body=body,
            attachment=summary_path,
            responsibles=responsibles,
        )
        self._update_combined(df_final)
        return ReturnEmailResult(subject=subject, summary_path=summary_path, transmittal_code=transmittal)

    def _send_outlook_mail(self, subject: str, body: str, attachment: Path, responsibles: list[str]):  # pragma: no cover
        import win32com.client as win32

        clean = [r for r in responsibles if r]
        to_extra = clean[0] if clean else ""
        cc_extra = "".join(clean[1:]) if len(clean) > 1 else ""

        outlook = win32.Dispatch("outlook.application")
        mail = outlook.CreateItem(0)
        mail.Subject = subject
        mail.To = email_TO + to_extra
        mail.CC = email_TO_CC + cc_extra
        mail.HTMLBody = (
            "<html><body>"
            "<p>Buenos días,</p>"
            "<p>Han devuelto la siguiente documentación:</p>"
            f"<div>{body}</div>"
            "<p>DESCARGADO Y ACTUALIZADO EN ERP.</p>"
            f"<p>HAY QUE SUBIRLO ANTES DEL: {(today() + pd.DateOffset(days=15)).strftime('%d-%m-%Y')}</p>"
            "</body></html>"
        )
        mail.Attachments.Add(str(attachment))
        mail.Display()

    def _update_combined(self, df_final: pd.DataFrame) -> None:
        if self.combine_path.exists():
            prev = pd.read_excel(self.combine_path)
            combined = pd.concat([prev, df_final], ignore_index=True)
        else:
            combined = df_final
        combined.to_excel(self.combine_path, index=False)

    @staticmethod
    def _sanitize_subject(subject: str) -> str:
        clean = re.sub(r'[\/:*?"<>|]', "", subject or "")
        return clean[:120]

    @staticmethod
    def _get_sender_email(message) -> str:
        address = (getattr(message, "SenderEmailAddress", "") or "").lower()
        if address and "@" in address and not address.startswith("/"):
            return address
        try:
            exchange_user = message.Sender.GetExchangeUser()
            if exchange_user:
                return (exchange_user.PrimarySmtpAddress or "").lower()
        except Exception:
            pass
        return address

    def extract_transmittal_code(self, subject: str) -> str | None:
        return None

    def parse_html_table(self, html: str) -> pd.DataFrame:
        raise NotImplementedError

    def transform_dataframe(
        self, df: pd.DataFrame, original_subject: str, received_time: str, transmittal: str | None
    ) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
        raise NotImplementedError

