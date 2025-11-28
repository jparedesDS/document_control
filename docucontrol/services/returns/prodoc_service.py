from __future__ import annotations

import re
from io import StringIO
import pandas as pd

from docucontrol.config import settings
from docucontrol.legacy.email_identification import email_employee, get_responsable_email
from docucontrol.legacy.po_identification import identificar_cliente_por_PO_PRODOC
from docucontrol.legacy.prodoc_data_process import (
    cambiar_tipo_estado,
    critico,
    procesar_documento_y_fecha,
    prodoc_vendor_number,
    reconocer_tipo_proyecto,
    reemplazar_null,
)
from .base import BaseReturnService, ReturnServiceConfig


class ProdocReturnService(BaseReturnService):
    def __init__(self):
        super().__init__(
            ReturnServiceConfig(
                sender_email="Prodoc.postmaster@woodplc.com",
                vendor_dir=settings.prodoc_returns_dir,
                combine_filename="all_tr_combine.xlsx",
                summary_prefix="PRODOC",
            )
        )

    def extract_transmittal_code(self, subject: str) -> str | None:
        match = re.search(r"TL-\d{2,4}[A-Z0-9]+-VDC-\d{4}", subject or "")
        return match.group(0) if match else None

    def parse_html_table(self, html: str) -> pd.DataFrame:
        df_list = pd.read_html(StringIO(html))
        table = df_list[0].copy()
        return table.loc[:, ["Name", "P.O.", "Title", "Rev", "S.R. Status", "Date"]]

    def transform_dataframe(self, df: pd.DataFrame, subject: str, received_time: str, transmittal: str | None):
        df = df.copy()
        df["Nº Pedido"] = df["P.O."]
        prodoc_vendor_number(df)
        df["Tipo de documento"] = df["Name"].str.extract(r"-(\D{2,3})(?=-\d{1,})", expand=False)
        df["Supp."] = "S00"
        reemplazar_null(df)
        df.insert(6, "Crítico", "Sí")
        df["P.O."] = df["P.O."].astype(str)
        identificar_cliente_por_PO_PRODOC(df)
        reconocer_tipo_proyecto(df)

        df_email = pd.DataFrame({"EMAIL": df["Tipo de documento"]})
        df_email = email_employee(df_email)
        df["Responsable_email"] = df["Nº Pedido"].apply(lambda val: get_responsable_email(val or ""))
        df["Responsable"] = df["Responsable_email"].map(
            {
                ";luis-bravo@eipsa.es;": "LB",
                ";ana-calvo@eipsa.es;": "AC",
                ";sandra-sanz@eipsa.es;": "SS",
                ";carlos-crespohor@eipsa.es;": "CC",
            }
        )

        procesar_documento_y_fecha(df, received_time)
        cambiar_tipo_estado(df)
        critico(df)
        df.rename(
            columns={
                "Name": "Doc. EIPSA",
                "Rev": "Rev.",
                "Title": "Título",
                "S.R. Status": "Estado",
                "P.O.": "PO",
            },
            inplace=True,
        )
        df["Doc. Cliente"] = df["Doc. EIPSA"]
        df["Nº Transmittal"] = transmittal

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
                "Estado",
                "Tipo de documento",
                "Crítico",
                "Nº Transmittal",
                "Fecha",
            ]
        )
        df_import = df_final.reindex(columns=["Nº Pedido", "Supp.", "PO", "Doc. Cliente", "Título", "Rev.", "Estado", "Fecha"])

        responsable_email = df["Responsable_email"].iloc[0]
        support_email = df_email.iloc[0, 0] if not df_email.empty else ""
        responsibles = [responsable_email or "", support_email or ""]
        return df_final, df_import, responsibles

