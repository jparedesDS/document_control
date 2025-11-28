from __future__ import annotations

import re
from io import StringIO
import pandas as pd

from docucontrol.config import settings
from docucontrol.legacy.email_identification import email_employee, get_responsable_email
from docucontrol.legacy.gaia_data_process import (
    cambiar_tipo_estado,
    critico,
    procesar_documento_y_fecha,
    reconocer_tipo_proyecto,
    reemplazar_null,
)
from docucontrol.legacy.po_identification import identificar_cliente_por_PO
from .base import BaseReturnService, ReturnServiceConfig


class GaiaReturnService(BaseReturnService):
    def __init__(self):
        super().__init__(
            ReturnServiceConfig(
                sender_email="gaia-tpplm-prod@ten.com",
                vendor_dir=settings.gaia_returns_dir,
                combine_filename="all_tr_combine.xlsx",
                summary_prefix="GAIA",
            )
        )

    def extract_transmittal_code(self, subject: str) -> str | None:
        match = re.search(r"([A-Z0-9]+(?:-[A-Z0-9]+)+)", subject or "")
        return match.group(0) if match else None

    def parse_html_table(self, html: str) -> pd.DataFrame:
        df_list = pd.read_html(StringIO(html))
        table = df_list[7].copy()
        return table.loc[:, ["Reference", "Doc. Title", "Doc. Rev."]]

    def transform_dataframe(self, df: pd.DataFrame, subject: str, received_time: str, transmittal: str | None):
        df = df.copy()
        estado = re.findall(r"Code\s\d+", subject or "")
        df["Estado"] = estado[0] if estado else None
        df["Tipo de documento"] = df["Reference"].str.extract(r"-(DWG|CAL|VDDL|IND|DOS|ITP|NDE|CER|PH|DD|WD)-", expand=False)
        df["Supp."] = "S00"
        reemplazar_null(df)
        df.insert(3, "Crítico", "Sí")
        df["Nº Pedido"] = df["Reference"].str.extract(r"-(\d{2}-\d{3})-", expand=False)
        df["Nº Pedido"] = "P-" + df["Nº Pedido"].str.replace("-", "/", regex=False)
        df["PO"] = df["Reference"].str.extract(r"^(\d+[A-Z])", expand=False)
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
                ";carlos-crespohor@eipsa.es;": "CC",
            }
        )

        procesar_documento_y_fecha(df, received_time)
        cambiar_tipo_estado(df)
        critico(df)
        df.rename(
            columns={
                "Reference": "Doc. EIPSA",
                "Doc. Rev.": "Rev.",
                "Doc. Title": "Título",
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

