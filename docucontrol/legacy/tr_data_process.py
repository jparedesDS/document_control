import numpy as np
import pandas as pd


def reemplazar_null(df: pd.DataFrame) -> pd.DataFrame:
    mapping = {np.nan: "S00", "S01": "S01", "S02": "S02", "S03": "S03", "S04": "S04", "S05": "S05", "S06": "S06", "S07": "S07"}
    df["Supp."] = df["Supp."].map(mapping).fillna("S00")
    return df


def reconocer_tipo_proyecto(df: pd.DataFrame) -> pd.DataFrame:
    mapping = {
        "411": "TEMPERATURA",
        "412": "TEMPERATURA",
        "610": "BIMETÁLICOS",
        "620": "TEMPERATURA",
        "640": "TEMPERATURA",
        "710": "NIVEL VIDRIO",
        "740": "TUBERÍAS",
        "910": "CAUDAL",
        "911": "SALTOS MULTIPLES",
        "920": "ORIFICIOS",
        "960": "ORIFICIOS",
        "010": "VALVULAS",
    }
    df["Material"] = df["PO"].str.extract(r"(\d{3}+\Z)", expand=False)
    df["Material"] = df["Material"].str[-3:].map(mapping)
    return df


def procesar_documento_y_fecha(df: pd.DataFrame, receivedtime):
    mapping = {
        "PLG": "Planos",
        "DWG": "Planos",
        "CAL": "Cálculos",
        "ESP": "Cálculos y Planos",
        "CER": "Certificado",
        "NACE": "Certificado",
        "DOS": "Dossier",
        "LIS": "Listado",
        "ITP": "Procedimientos",
        "PRC": "Procedimientos",
        "MAN": "Manual",
        "VDB": "Listado",
        "PLN": "PPI",
        "PLD": "Nameplate",
        "CAT": "Catalogo",
        "DL": "Listado",
    }
    df["Tipo de documento"] = df["Tipo de documento"].map(mapping)
    df["Fecha"] = pd.to_datetime(receivedtime, dayfirst=True)
    return df


def critico(df: pd.DataFrame) -> pd.DataFrame:
    mapping = {
        "Planos": "Sí",
        "Cálculos": "Sí",
        "Cálculos y Planos": "Sí",
        "Certificado": "No",
        "Dossier": "No",
        "Procedimientos": "No",
        "Manual": "Sí",
        "PPI": "Sí",
        "Nameplate": "No",
        "Catalogo": "Sí",
        "Listado": "Sí",
        "Repuestos": "No",
    }
    df["Crítico"] = df["Tipo de documento"].map(mapping)
    return df


def cambiar_tipo_estado(df: pd.DataFrame) -> pd.DataFrame:
    mapping = {
        "A - REJECTED": "Rechazado",
        "B - REVIEWED WITH MAJOR COMMENTS": "Com. Mayores",
        "C - REVIEWED WITH MINOR COMMENTS": "Com. Menores",
        "F - REVIEWED WITHOUT COMMENTS": "Aprobado",
        "F - ACCEPTED WITHOUT COMMENTS": "Aprobado",
        "W - ISSUED FOR CERTIFICATION": "Certificación",
        "M - VOID": "Eliminado",
        "R - REVIEWED AS BUILT": "Aprobado",
    }
    df["Return Status"] = df["Return Status"].map(mapping)
    return df

