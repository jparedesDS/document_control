import numpy as np
import pandas as pd


def reconocer_tipo_proyecto(df: pd.DataFrame) -> pd.DataFrame:
    mapping = {
        "214726C": "CAUDAL",
        "7070000087": "TEMPERATURA",
    }
    df["Material"] = df["PO"].map(mapping).fillna(df["PO"])
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
        "ITP": "PPI",
        "PRC": "Procedimientos",
        "MAN": "Manual",
        "VDB": "Listado",
        "PLN": "PPI",
        "PLD": "Nameplate",
        "CAT": "Catalogo",
        "DL": "Listado",
        "SPL": "Repuestos",
        "WD": "Soldadura",
        "VDDL": "Listado",
        "IND": "Indice",
        "NDE": "Procedimientos",
        "PH": "Procedimientos",
        "DD": "Dossier",
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
        "Indice": "No",
    }
    df["Crítico"] = df["Tipo de documento"].map(mapping)
    return df


def cambiar_tipo_estado(df: pd.DataFrame) -> pd.DataFrame:
    mapping = {
        "Code 1": "Com. Mayores",
        "Code 2": "Com. Menores",
        "Code 3": "Aprobado",
        "Code 4": "Informativo",
        "Code 5": "Rechazado",
    }
    df["Estado"] = df["Estado"].map(mapping)
    return df


def reemplazar_null(df: pd.DataFrame) -> pd.DataFrame:
    mapping = {np.nan: "S00", "S01": "S01", "S02": "S02", "S03": "S03", "S04": "S04", "S05": "S05", "S06": "S06", "S07": "S07"}
    df["Supp."] = df["Supp."].map(mapping).fillna("S00")
    return df

