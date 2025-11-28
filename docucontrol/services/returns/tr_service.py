from __future__ import annotations

import re
from io import StringIO
import pandas as pd

from docucontrol.config import settings
from docucontrol.legacy.email_identification import email_employee, get_responsable_email
from docucontrol.legacy.po_identification import identificar_cliente_por_PO
from docucontrol.legacy.tr_data_process import (
    cambiar_tipo_estado,
    critico,
    procesar_documento_y_fecha,
    reconocer_tipo_proyecto,
    reemplazar_null,
)
from .base import BaseReturnService, ReturnServiceConfig


class TRReturnService(BaseReturnService):
    def __init__(self):
        super().__init__(
            ReturnServiceConfig(
                sender_email="egesdoc@grupotr.es",
                vendor_dir=settings.tr_returns_dir,
                combine_filename="all_tr_combine.xlsx",
                summary_prefix="TR",
            )
        )

    def extract_transmittal_code(self, subject: str) -> str | None:
        match = re.search(r"\d{5}-\w+-\d+", subject)
        return match.group(0) if match else None

    def parse_html_table(self, html: str) -> pd.DataFrame:
        df_list = pd.read_html(StringIO(html))
        table = df_list[5].copy()
        return table.loc[:, ["Vendor Number", "TR Number", "Title", "Vendor Rev", "TR Rev", "Return Status"]]

    def transform_dataframe(self, df: pd.DataFrame, subject: str, received_time: str, transmittal: str | None):
        df = df.copy()
        df["Tipo de documento"] = df["Vendor Number"].str.extract(r"^([A-Z]{2,3})", expand=False)
        df["Supp."] = df["Vendor Number"].str.extract(r"([S]+\d+)", expand=False)
        reemplazar_null(df)
        df.insert(6, "Crítico", "Sí")
        pedido = df["Vendor Number"].str.extract(r"(\d+-\d+)", expand=False)
        df["Nº Pedido"] = "P-" + pedido.str.replace("-", "/", regex=False)
        po_match = re.search(r"(\d{10})", subject or "")
        df["PO"] = po_match.group(0) if po_match else ""
        df["Nº Transmittal"] = df["PO"]
        identificar_cliente_por_PO(df)
        reconocer_tipo_proyecto(df)

        df_email = pd.DataFrame({"EMAIL": df["Tipo de documento"]})
        df_email = email_employee(df_email)
        df["Responsable_email"] = df["Nº Pedido"].apply(lambda val: get_responsable_email(val or ""))
        df["Responsable"] = df["Responsable_email"].map(
            {
                ";luis-bravo@eipsa.es;": "LB",
                ";ana-calvo@eipsa.es;": "AC",
                ";sandra-sanz@eipsa.es;": "SS",
                ";carlos-crespohor@eipsa.es;": "CCH",
            }
        )

        procesar_documento_y_fecha(df, received_time)
        cambiar_tipo_estado(df)
        critico(df)
        df.rename(
            columns={
                "Vendor Number": "Doc. EIPSA",
                "Vendor Rev": "Rev.",
                "Title": "Título",
                "TR Number": "Doc. Cliente",
                "Return Status": "Estado",
                "TR Rev": "TR Rev.",
            },
            inplace=True,
        )
        df["Nº Transmittal"] = transmittal or df["Nº Transmittal"]

        df_final = df.reindex(
            columns=[
                "Nº Pedido",
                "Supp.",
                "Responsable",
                "Cliente",
                "Material",
                "PO",
                "Doc. EIPSA",
                "Doc. Cliente",
                "Título",
                "Rev.",
                "TR Rev.",
                "Estado",
                "Tipo de documento",
                "Crítico",
                "Nº Transmittal",
                "Fecha",
            ]
        )
        df_import = df_final.reindex(
            columns=["Nº Pedido", "Supp.", "PO", "Doc. EIPSA", "Doc. Cliente", "Título", "Rev.", "TR Rev.", "Estado", "Fecha"]
        )

        responsable_email = df["Responsable_email"].iloc[0]
        support_email = df_email.iloc[0, 0] if not df_email.empty else ""
        responsibles = [responsable_email or "", support_email or ""]
        return df_final, df_import, responsibles
 
